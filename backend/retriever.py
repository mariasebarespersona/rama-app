# # retriever.py
# def retrieve_relevant_chunks(query, property_id, k=5):
#     query_embedding = get_embeddings([query])[0]
#     near_vector = {"vector": query_embedding}
#     filter_property = {
#         "path": ["property_id"],
#         "operator": "Equal",
#         "valueString": str(property_id)
#     }

#     result = client.query.get("DocumentChunk", ["text"])\
#         .with_near_vector(near_vector)\
#         .with_where(filter_property)\
#         .with_limit(k)\
#         .do()

#     return [item["text"] for item in result["data"]["Get"]["DocumentChunk"]]


from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings



from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()  # Now this will pick up the .env from the backend folder

VECTORSTORE_DIR = "faiss_index"
embedding_model = OpenAIEmbeddings()

def retrieve_relevant_chunks(query: str, property_id: int):
    if not os.path.exists(VECTORSTORE_DIR):
        return []

    vectorstore = FAISS.load_local(VECTORSTORE_DIR, embedding_model)
    docs = vectorstore.similarity_search_with_score(query, k=5)

    # Filter by property_id
    filtered = [
        doc for doc, score in docs
        if doc.metadata.get("property_id") == property_id
    ]
    return filtered

