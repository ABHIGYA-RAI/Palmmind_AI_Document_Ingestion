from fileinput import filename

from fastapi import FastAPI
from fastapi import UploadFile
from fastapi import File
from fastapi import HTTPException

app = FastAPI()
@app.post("/ingest")
async def ingest(file: UploadFile = File(...)):
    if not file.filename.endswith((".pdf",".txt")):
        raise HTTPException(400,"Sorry, only PDF and TXT files are allowed.")
    content = await file.read()
    return {"File" : file.filename, "Size" : len(content)}
