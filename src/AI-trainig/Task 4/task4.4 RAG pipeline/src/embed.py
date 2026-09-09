from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from embed_model import model

pdf_path = r"C:\Users\User\Downloads\RAG.pdf"

loader = PyPDFLoader(pdf_path)
documents = loader.load()
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=100
)

docs = text_splitter.split_documents(documents)
texts = [doc.page_content for doc in docs]
embeddings = list(model.embed(texts))