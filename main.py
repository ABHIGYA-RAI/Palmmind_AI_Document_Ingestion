import uuid
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from chunking import chunk_text
from config import allowed_file_extensions, chunking_strategies
from database import save_metadata
from extraction import extract_text
from vector_storage import store_embeddings

#FastAPI app
app = FastAPI()

# This endpoint is the REST API
@app.post("/ingest")
async def ingest(file: UploadFile = File(...), chunking_strategy = Form("Fixed")):
    filename = file.filename or ""
    if not filename.lower().endswith(allowed_file_extensions):
        raise HTTPException(400, "Only .pdf and .txt files are allowed.")
    if chunking_strategy not in chunking_strategies:
        raise HTTPException(400, "Chunking strategy must be Fixed or Paragraph.")

    content = await file.read()
    text = extract_text(filename, content)
    chunks = chunk_text(text, chunking_strategy)
    if not chunks:
        raise HTTPException(400, "No text found in the file.")

    doc_id = str(uuid.uuid4())
    store_embeddings(doc_id, filename, chunks)
    save_metadata(doc_id, filename, chunking_strategy, len(chunks))

    return {
        "Document ID": doc_id,
        "Filename": filename,
        "Chunking strategy": chunking_strategy,
        "No. of chunks stored": len(chunks),
    }