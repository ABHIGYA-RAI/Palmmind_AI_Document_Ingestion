from io import BytesIO
from pypdf import PdfReader

# Extracting text of a PDF document
def extract_text(filename, content) :
    if filename.lower().endswith(".pdf"):
        reader = PdfReader(BytesIO(content))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    return content.decode("utf-8")