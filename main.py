from fileinput import filename

from fastapi import FastAPI
from fastapi import UploadFile
from fastapi import File
from fastapi import HTTPException

app = FastAPI()
#1. Uploading the .txt and .pdf file
#@app.post("/ingest")
'''async def ingest(file: UploadFile = File(...)):
    if not file.filename.endswith((".pdf",".txt")):
        raise HTTPException(400,"Sorry, only PDF and TXT files are allowed.")
    content = await file.read()
    return {"File" : file.filename, "Size" : len(content)}'''

from pypdf import PdfReader
from io import BytesIO

from io import BytesIO
from fastapi import FastAPI, UploadFile, File, HTTPException
from pypdf import PdfReader

app = FastAPI()

#2. Extracting text from a document file.
def extract_text(filename : str, content: bytes) -> str:
    if filename.lower().endswith(".pdf"):
        reader = PdfReader(BytesIO(content))
        return "\n".join(page.extract_text() or " " for page in reader.pages)
    return content.decode("utf-8")

'''@app.post("/ingest") # Endpoint
async def ingest(file: UploadFile = File(...)):
    if not file.filename.lower().endswith((".pdf",".txt")):
        raise HTTPException(400,"Sorry, only .pdf and .txt files are allowed.")
    content = await file.read()
    text = extract_text(file.filename,content)
    return {"Filename" : file.filename, "Characters" : len(text), "Preview" : text[ :200]}'''

import re
def fixed_chunks(text: str, size: int = 500, overlap: int = 50) -> list[str]:
    step = size-overlap
    return [text[i:i+size] for i in range(0,len(text),step)]

def paragraph_chunks(text:str,max_size : int = 500) -> list[str]:
    chunks = [ ]
    current = " "
    for paragraph in re.split(r"\n+",text):
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

def chunk_text(text: str, chunking_strategy: str) -> list[str]:
    if chunking_strategy == "Fixed":
        return fixed_chunks(text)
    elif chunking_strategy == "Paragraph":
        return paragraph_chunks(text)

#Endpoint

from fastapi import Form
@app.post("/ingest")
async def ingest(file: UploadFile = File(...),chunking_strategy: str = Form("Fixed")):
    if not file.filename.endswith((".pdf",".txt")):
        raise HTTPException(400,"Sorry, only .pdf and .txt files are allowed.")
    if chunking_strategy not in ["Fixed","Paragraph"]:
        raise HTTPException(400,"Chunking strategy should be either fixed or paragraph.")
    content = await file.read()
    text = extract_text(file.filename,content)
    chunks = chunk_text(text,chunking_strategy)
    return {"Filename" : file.filename, "Chunking strategy" : chunking_strategy, "Chunks" : len(chunks),"First Chunk" : chunks[0] if chunks else " "}










