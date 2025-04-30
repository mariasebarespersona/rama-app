# weaviate_setup.py
import weaviate
from weaviate.util import get_valid_uuid

client = weaviate.Client("http://localhost:8080")  # or hosted option

def init_schema():
    class_obj = {
        "class": "DocumentChunk",
        "vectorIndexType": "hnsw",
        "properties": [
            {"name": "text", "dataType": ["text"]},
            {"name": "property_id", "dataType": ["string"]},
            {"name": "document_type", "dataType": ["string"]},
        ]
    }
    if not client.schema.contains({"class": "DocumentChunk"}):
        client.schema.create_class(class_obj)

def store_chunks(chunks, embeddings, property_id, document_type):
    for chunk, vector in zip(chunks, embeddings):
        client.data_object.create({
            "text": chunk,
            "property_id": str(property_id),
            "document_type": document_type
        }, class_name="DocumentChunk", vector=vector)
