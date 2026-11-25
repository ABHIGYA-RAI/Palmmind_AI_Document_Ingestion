import re
from config import chunk_overlap, chunk_size

# Fixed Chunking strategy
def fixed_chunks(text, size = chunk_size, overlap = chunk_overlap) :
    step = size - overlap
    return [text[i:i + size] for i in range(0, len(text), step)]

#Paragraph Chunking strategy
def paragraph_chunks(text, max_size= chunk_size):
    chunks = []
    current = " "
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


def chunk_text(text, strategy) :
    if strategy == "Fixed":
        return fixed_chunks(text)
    elif strategy == "Paragraph":
        return paragraph_chunks(text)