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

#2. Extracting the text from a .pdf document.
def extract_text(filename : str, content: bytes) -> str:
    if filename.lower().endswith(".pdf"):
        reader = PdfReader(BytesIO(content))
        return "\n".join(page.extract_text() or " " for page in reader.pages)
    return content.decode("utf-8")

@app.post("/ingest") # Endpoint
async def ingest(file: UploadFile = File(...)):
    if not file.filename.lower().endswith((".pdf",".txt")):
        raise HTTPException(400,"Sorry, only .pdf and .txt files are allowed.")
    content = await file.read()
    text = extract_text(file.filename,content)
    return {"Filename" : file.filename, "Characters" : len(text), "Preview" : text[ :200]}
