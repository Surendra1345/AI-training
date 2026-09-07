from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
)
from langchain_core.documents import Document
from fastembed import TextEmbedding


PDF_PATH = r"C:\Users\User\Downloads\01_farmer_text_only.pdf"


# -----------------------------
# 1. Load document
# -----------------------------

loader = PyPDFLoader(PDF_PATH)
documents = loader.load()

print("Number of pages:", len(documents))


# -----------------------------
# 2. Fixed-size chunking
# -----------------------------

fixed_splitter = CharacterTextSplitter(
    separator="",
    chunk_size=300,
    chunk_overlap=50,
)

fixed_chunks = fixed_splitter.split_documents(documents)

print("Fixed chunks:", len(fixed_chunks))


# -----------------------------
# 3. Recursive chunking
# -----------------------------

recursive_splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=50,
)

recursive_chunks = recursive_splitter.split_documents(documents)

print("Recursive chunks:", len(recursive_chunks))


# -----------------------------
# 4. Structure-aware chunking
# -----------------------------

text = documents[0].page_content

sections = [
    "1. Farmer Registration",
    "2. Crop Information",
    "3. Storage Information",
    "4. Account Recovery",
]

structure_chunks = []

for i, heading in enumerate(sections):

    start = text.find(heading)

    if start == -1:
        continue

    if i + 1 < len(sections):
        end = text.find(sections[i + 1])
    else:
        end = len(text)

    section_text = text[start:end].strip()

    chunk = Document(
        page_content=section_text,
        metadata={
            "source": "01_farmer_text_only.pdf",
            "page": 1,
            "section": heading,
            "date": "2026-09-07",
        },
    )

    structure_chunks.append(chunk)


print("Structure-aware chunks:", len(structure_chunks))


# -----------------------------
# 5. Display results
# -----------------------------

print("\n--- FIXED CHUNKS ---")

for i, chunk in enumerate(fixed_chunks, start=1):
    print(f"\nChunk {i}:")
    print(chunk.page_content)


print("\n--- RECURSIVE CHUNKS ---")

for i, chunk in enumerate(recursive_chunks, start=1):
    print(f"\nChunk {i}:")
    print(chunk.page_content)


print("\n--- STRUCTURE-AWARE CHUNKS ---")

for i, chunk in enumerate(structure_chunks, start=1):
    print(f"\nChunk {i}:")
    print(chunk.page_content)


def add_metadata(chunks,chunking_method):
    for chunk in chunks:
        chunk.metadata={
            "source":"01_farmer_text_only.pdf",
            "page":chunk.metadata.get("page",0)+1,
            "section":chunk.metadata.get("section","unknown"),
            "date":"2026-09-07",
            "chunking_method":chunking_method
        }
    return chunks

fixed_chunks = add_metadata(fixed_chunks,"fixed")
recursive_chunks = add_metadata(recursive_chunks,"recursive")
structure_chunks = add_metadata(structure_chunks,"structure-aware")

print("\n--- METADATA ---")

for chunk in fixed_chunks[:2]:
    print(chunk.metadata)

for chunk in recursive_chunks[:2]:
    print(chunk.metadata)

for chunk in structure_chunks[:2]:
    print(chunk.metadata)

# -----------------------------
# 6. Generate embeddings
# -----------------------------


model = TextEmbedding("BAAI/bge-small-en-v1.5")

all_chunks = (
    fixed_chunks
    + recursive_chunks
    + structure_chunks
)

texts = [chunk.page_content for chunk in all_chunks]

embeddings = list(model.embed(texts))

print("\n--- EMBEDDINGS ---")
print("Total chunks:", len(all_chunks))
print("Total embeddings:", len(embeddings))
print("Embedding dimension:", len(embeddings[0]))

