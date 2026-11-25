import sqlite3
from datetime import datetime
from config import the_database

# Creating a SQL table
database = sqlite3.connect(the_database, check_same_thread=False)
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

# Storing the metadata of the file in SQLite database
def save_metadata(doc_id,filename, strategy, chunk_count):
    database.execute(
        "INSERT INTO documents VALUES(?,?,?,?,?,?)",
        (
            doc_id,
            filename,
            filename.split(".")[-1].lower(),
            strategy,
            chunk_count,
            datetime.now().isoformat(),
        ),
    )
    database.commit()