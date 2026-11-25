import os
import re
import uuid
from io import BytesIO

from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pinecone import Pinecone, ServerlessSpec
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

app = FastAPI()

# Pinecone and embedding model setup
load_dotenv("Pinecone_API.env")
pinecone_api = os.getenv("pinecone_api_key")

model = SentenceTransformer("all-MiniLM-L6-v2")
pine_cone = Pinecone(api_key=pinecone_api)
index_name = "documents"

if index_name not in pine_cone.list_indexes().names():
    pine_cone.create_index(
        name=index_name,
        dimension=384,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="Kathmandu"),
    )
index = pine_cone.Index(index_name)


# 2. Extracting text from a document file
def extract_text(filename: str, content: bytes):
    if filename.lower().endswith(".pdf"):
        reader = PdfReader(BytesIO(content))
        return "\n".join(page.extract_text() or " " for page in reader.pages)
    return content.decode("utf-8")


# 3. Chunking strategies
def fixed_chunks(text: str, size: int = 500, overlap: int = 50) -> list[str]:
    step = size - overlap
    return [text[i:i + size] for i in range(0, len(text), step)]


def paragraph_chunks(text: str, max_size: int = 500) :
    chunks = []
    current = " "
    for paragraph in re.split(r"\n+", text):
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        if len(current) + len(paragraph) + 1 <= max_size:
            current += paragraph + " "
        else:
            if current:
                chunks.append(current.strip())
            current = paragraph + " "
    if current:
        chunks.append(current.strip())
    return chunks


def chunk_text(text: str, chunking_strategy: str) :
    if chunking_strategy == "Fixed":
        return fixed_chunks(text)
    elif chunking_strategy == "Paragraph":
        return paragraph_chunks(text)


# 4. Embedding (strings of text -> vectors/numbers)
def store_embeddings(doc_id: str, filename: str, chunks: list[str]):
    vectors = model.encode(chunks).tolist()

#5. Storing the embeddings in Pinecone vector database.
    index.upsert(vectors=[
        (f"{doc_id} - {i}",vec,{"Filename" : filename,"Chunk": i, "Text": chunk})
        for i,(vec,chunk) in enumerate(zip(vectors,chunks))
    ])


# Endpoint
@app.post("/ingest")
async def ingest(file: UploadFile = File(...), chunking_strategy: str = Form("Fixed")):
    if not file.filename.lower().endswith((".pdf", ".txt")):
        raise HTTPException(400, "Sorry, only .pdf and .txt files are allowed.")
    if chunking_strategy not in ["Fixed","Paragraph"]:
        raise HTTPException(400, "Chunking strategy should be either Fixed or Paragraph.")
    content = await file.read()
    text = extract_text(file.filename,content)
    chunks = chunk_text(text,chunking_strategy)
    if not chunks:
        raise HTTPException(400,"No text found in given file.")
    doc_id = str(uuid.uuid4())
    store_embeddings(doc_id,file.filename,chunks)

    return {"Document ID" : doc_id, "Filename" : file.filename, "Chunking strategy" : chunking_strategy, "Chunks stored" : len(chunks)}
