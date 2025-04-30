# # embedder.py
# from openai import OpenAI
# import tiktoken

# client = OpenAI()
# tokenizer = tiktoken.encoding_for_model("text-embedding-3-small")

# def chunk_text(text: str, max_tokens=500):
#     words = text.split()
#     chunks, current_chunk = [], []
#     current_tokens = 0
#     for word in words:
#         tokens = len(tokenizer.encode(word))
#         if current_tokens + tokens > max_tokens:
#             chunks.append(" ".join(current_chunk))
#             current_chunk, current_tokens = [], 0
#         current_chunk.append(word)
#         current_tokens += tokens
#     if current_chunk:
#         chunks.append(" ".join(current_chunk))
#     return chunks

# def get_embeddings(texts: list[str]) -> list[list[float]]:
#     response = client.embeddings.create(
#         model="text-embedding-3-small",
#         input=texts
#     )
#     return [e.embedding for e in response.data]


from openai import OpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.vectorstores import FAISS
# from langchain.embeddings import OpenAIEmbeddings
import os
import pickle

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings


# Persistent FAISS index path
VECTORSTORE_DIR = "faiss_index"

embedding_model = OpenAIEmbeddings()

def embed_and_store(text: str, property_id: int, doc_type: str):
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_text(text)

    metadatas = [{"property_id": property_id, "doc_type": doc_type} for _ in chunks]
    new_vectorstore = FAISS.from_texts(chunks, embedding_model, metadatas=metadatas)

    # Merge with existing index or create new
    if os.path.exists(VECTORSTORE_DIR):
        existing = FAISS.load_local(VECTORSTORE_DIR, embedding_model)
        existing.merge_from(new_vectorstore)
        existing.save_local(VECTORSTORE_DIR)
    else:
        new_vectorstore.save_local(VECTORSTORE_DIR)
