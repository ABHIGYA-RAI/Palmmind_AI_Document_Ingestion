#1. Import the packages and libraries
import os
import re
import uuid
from io import BytesIO
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pinecone import Pinecone, ServerlessSpec
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

#2. Create a FastAPI app
app = FastAPI()

#3. Fetching the Pinecone vector database's API Key
load_dotenv("Pinecone_API.env")
pinecone_api_key = os.getenv("pinecone_api_key")
model = SentenceTransformer("all-MiniLM-L6-v2")
pine_cone = Pinecone(api_key=pinecone_api_key)
index_name = "documents"

#4. Creating the documents index in Pinecone console
if index_name not in pine_cone.list_indexes().names():
    pine_cone.create_index(
        name=index_name,
        dimension=384,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )
index = pine_cone.Index(index_name)

# 5. Extracting the text from PDF document
def extract_text(filename, content):
    if filename.lower().endswith(".pdf"):
        reader = PdfReader(BytesIO(content))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    return content.decode("utf-8")

#6. Chunking strategy no. 1: Fixed chunking
def fixed_chunks(text, size=500, overlap=50):
    step = size - overlap
    return [text[i:i + size] for i in range(0, len(text), step)]

#7. Chunking strategy no.2 : Paragraph chunking
def paragraph_chunks(text, max_size=500):
    chunks = []
    current = ""
    for line in re.split(r"\n+", text):
        line = line.strip()
        if not line:
            continue
        if len(current) + len(line) + 1 <= max_size:
            current += line + " "
        else:
            if current:
                chunks.append(current.strip())
            current = line + " "
    if current:
        chunks.append(current.strip())
    return chunks


def chunk_text(text, strategy):
    if strategy == "Fixed":
        return fixed_chunks(text)
    elif strategy == "Paragraph":
        return paragraph_chunks(text)

#8. Embedding and storing in Pinecone
def store_embeddings(doc_id, filename, chunks):
    vectors = model.encode(chunks).tolist()
    index.upsert(vectors=[
        (f"{doc_id}-{i}", vec, {"Filename": filename, "Chunk": i, "Text": chunk})
        for i, (vec, chunk) in enumerate(zip(vectors, chunks))
    ])

#9. Storing the metadata in SQL database
import sqlite3
from datetime import datetime
database = sqlite3.connect("Metadata.db",check_same_thread=False)
database.execute(""" 
          CREATE TABLE IF NOT EXISTS documents(
          doc_id TEXT PRIMARY KEY,
          filename TEXT,
          file_type TEXT,
          chunking_strategy TEXT,
          chunk_count INT,
          upload_at TEXT
         )
""")
database.commit()

def save_metadata(doc_id,filename,strategy,chunk_count):
    database.execute(
        "INSERT INTO documents VALUES(?,?,?,?,?,?)",
        (doc_id,filename,filename.split(".")[-1].lower(),strategy,chunk_count,datetime.now().isoformat()),
    )
    database.commit()

# The endpoint
@app.post("/ingest")
async def ingest(file: UploadFile = File(...), chunking_strategy: str = Form("Fixed")):
    if not file.filename.lower().endswith((".pdf", ".txt")):
        raise HTTPException(400, "Sorry, only .pdf and .txt files are allowed.")
    if chunking_strategy not in ["Fixed", "Paragraph"]:
        raise HTTPException(400, "Chunking strategy must be Fixed or Paragraph.")

    content = await file.read()
    text = extract_text(file.filename, content)
    chunks = chunk_text(text, chunking_strategy)
    if not chunks:
        raise HTTPException(400, "No text found in the file.")

    doc_id = str(uuid.uuid4())
    store_embeddings(doc_id, file.filename, chunks)
    save_metadata(doc_id,file.filename,chunking_strategy,len(chunks))

    return{
        "Document ID" : doc_id,
        "Filename" : file.filename,
        "Chunking strategy" : chunking_strategy,
        "No. of chunks stored" : len(chunks),
    }
