#!/usr/bin/env python3
import os
import glob
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

os.environ["HF_TOKEN"] = os.environ.get("HF_TOKEN", "")


def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    pages = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        pages.append({"text": text, "page_num": i + 1})
    return pages


def load_documents(pdf_folder):
    pdf_files = glob.glob(os.path.join(pdf_folder, "*.pdf"))
    documents = []
    
    for pdf_file in pdf_files:
        print(f"Processing: {pdf_file}")
        pages = extract_text_from_pdf(pdf_file)
        pdf_name = os.path.basename(pdf_file)
        
        for page in pages:
            doc = Document(
                page_content=page["text"],
                metadata={"source": pdf_name, "page": page["page_num"]}
            )
            documents.append(doc)
    
    return documents


def split_documents(documents, chunk_size=1000, chunk_overlap=200):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)
    return chunks


def create_vector_store(chunks, model_name="sentence-transformers/all-mpnet-base-v2"):
    print("Loading embedding model...")
    embeddings = HuggingFaceEmbeddings(model_name=model_name)
    
    print("Creating FAISS vector store...")
    vector_store = FAISS.from_documents(chunks, embeddings)
    return vector_store


def save_vector_store(vector_store, output_path="faiss_index"):
    vector_store.save_local(output_path)
    print(f"Vector store saved to: {output_path}")


def main():
    pdf_folder = "resources"
    output_path = "faiss_index"
    
    print("Loading PDF documents...")
    documents = load_documents(pdf_folder)
    print(f"Loaded {len(documents)} documents")
    
    print("Splitting documents into chunks...")
    chunks = split_documents(documents)
    print(f"Created {len(chunks)} chunks")
    
    vector_store = create_vector_store(chunks)
    save_vector_store(vector_store, output_path)
    print("Indexing complete!")


if __name__ == "__main__":
    main()
