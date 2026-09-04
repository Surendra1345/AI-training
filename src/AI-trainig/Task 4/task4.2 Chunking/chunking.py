from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import CharacterTextSplitter,RecursiveCharacterTextSplitter
import re
import pymupdf
from rapidocr import RapidOCR

pdf_path = r"C:\Users\User\Downloads\02_farmer_text_and_texted_diagram.pdf"
pdf = pymupdf.open(pdf_path)
page = pdf[0]
pix = page.get_pixmap()
pix.save("page1.png")
print("PDF page converted to image")
ocr = RapidOCR()
result = ocr("page1.png")
# Get only extracted text
ocr_text = "\n".join(result.txts)

print("OCR extracted text:")
print(ocr_text)

# Fixed-size chunking
splitter = CharacterTextSplitter(
    separator="",
    chunk_size=50,
    chunk_overlap=10
)

# Split the OCR text
chunks = splitter.create_documents([ocr_text])

print(f"Number of chunks: {len(chunks)}")

for i, chunk in enumerate(chunks, start=1):
    print(f"\nChunk {i}:")
    print(f"Chunk text:\n{chunk.page_content}")

# Recursive chunking
recursive_splitter=RecursiveCharacterTextSplitter(
    chunk_size=50,
    chunk_overlap=10,
)
recursive_chunks=recursive_splitter.split_documents([ocr_text])
print(f"Number of recursive chunks: {len(recursive_chunks)}")

# Structure aware chunking
text = ocr_text
pattern = r"\d+\.\s+[A-Za-z ]+"
matches = re.findall(pattern, text)
print(f"Number of matches: {len(matches)}")
for i, heading in enumerate(matches):
    start = text.find(heading)
    if i + 1 < len(matches):
        end = text.find(matches[i + 1])
    else:
        end = len(text)
    chunk = text[start:end].strip()
    print(f"\nChunk {i + 1}:")
    print(f"Chunk text:\n{chunk}")
