import os

from dotenv import load_dotenv

load_dotenv("Pinecone_API.env")

Pinecone_api = os.getenv("pinecone_api_key")
index_name = "documents"
embedding_model = "all-MiniLM-L6-v2"
embedding_dimension = 384
the_database = "Metadata.db"

chunk_size = 500
chunk_overlap = 50

allowed_file_extensions = (".pdf", ".txt")
chunking_strategies = ("Fixed", "Paragraph")