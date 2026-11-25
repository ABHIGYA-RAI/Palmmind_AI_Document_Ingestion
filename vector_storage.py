from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer

from config import (
    embedding_dimension,
    embedding_model,
    index_name,
    Pinecone_api,
)

model = SentenceTransformer(embedding_model)
pc = Pinecone(api_key = Pinecone_api)

#Creating index in Pinecone console
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=embedding_dimension,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )
index = pc.Index(index_name)

# Embeddings and Pinecone storage of the vectors
def store_embeddings(doc_id, filename, chunks) :
    vectors = model.encode(chunks).tolist()
    index.upsert(vectors=[
        (f"{doc_id}-{i}", vec, {"Filename": filename, "Chunk": i, "Text": chunk})
        for i, (vec, chunk) in enumerate(zip(vectors, chunks))
    ])