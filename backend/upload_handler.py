# upload_handler.py
from parser import extract_text_from_pdf
from embedder import chunk_text, get_embeddings
from weaviate_setup import store_chunks

def handle_document_upload(file_path, property_id, document_type):
    text = extract_text_from_pdf(file_path)
    chunks = chunk_text(text)
    embeddings = get_embeddings(chunks)
    store_chunks(chunks, embeddings, property_id, document_type)
