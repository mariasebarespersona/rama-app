from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import asyncpg
from typing import List
import os
from fastapi.responses import Response
from fastapi import Request

from openai import OpenAI
from fastapi import Request
from datetime import datetime


from fastapi.middleware.cors import CORSMiddleware

from retriever import retrieve_relevant_chunks
from answer_generator import generate_answer


import fitz  # PyMuPDF
from embedder import embed_and_store  # We will define this next


from dotenv import load_dotenv
load_dotenv()



# Get your API key
api_key = os.getenv("OPENAI_API_KEY")

# Create OpenAI client
client = OpenAI(api_key=api_key)




app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all frontend origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP  methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Mount static files for UI
# app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve React build folder
app.mount("/static", StaticFiles(directory="build/static"), name="static")




# Database connection
DB_URL = "postgresql://maria:maria@localhost/rama_real_estate"

async def get_db():
    return await asyncpg.connect(DB_URL)

# Document type classification
DOCUMENT_CATEGORIES = {
    "purchase_documents": ["contract", "notary_deed", "notary_registration", "deposit", "tax_ITP_IBA"],
    "renovation_documents": ["geotechnical_study", "land_plans", "architect_plans", "budget", "architect_contract", "surveyor_contract", "building_license", "contractor_contract", "trade_contract","builder_payments"],
    "sales_documents": ["sale_contract", "payment_certification"]
}


def extract_text_from_pdf(file_bytes: bytes) -> str:
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    

@app.post("/upload_property_details")
async def upload_property_details(
    request: Request,
    property_id: int = Form(...),
    address: str = Form(...),
    purchase_price: float = Form(...),
    status: str = Form(...)
):
    try:
        conn = await get_db()
        try:
            query = """
                INSERT INTO properties (id, address, purchase_price, status)
                VALUES ($1, $2, $3, $4)
                RETURNING id
            """
            result = await conn.fetchrow(query,property_id, address, purchase_price, status)
        finally:
            await conn.close()

        return {
            "message": "Property details uploaded successfully.",
            "property_id": result["id"]
        }

    except Exception as e:
        error_message = str(e)
        print(f"Error in upload_property_details: {error_message}")
        raise HTTPException(status_code=500, detail=error_message)


@app.post("/upload")
async def upload_document(
    request: Request,
    property_id: int = Form(...), 
    doc_type: str = Form(...), 
    file: UploadFile = File(...)
):
    try:
        table = None
        for tbl, types in DOCUMENT_CATEGORIES.items():
            if doc_type in types:
                table = tbl
                break

        if not table:
            raise HTTPException(status_code=400, detail="Invalid document type")

        file_data = await file.read()
        
        conn = await get_db()
        try:
            query = f"""
                INSERT INTO {table} (property_id, document_type, document) 
                VALUES ($1, $2, $3)
            """
            await conn.execute(query, property_id, doc_type, file_data)
        finally:
            await conn.close()

        return {"message": f"{doc_type} uploaded successfully for property {property_id}"}
    except Exception as e:
        error_message = str(e)
        print(f"Error in upload_document: {error_message}")  # Log error in terminal
        raise HTTPException(status_code=500, detail=error_message)


# @app.post("/upload")
# async def upload_document(
#     property_id: int = Form(...),
#     doc_type: str = Form(...),
#     file: UploadFile = File(...)
# ):
#     file_data = await file.read()
#     text = extract_text_from_pdf(file_data)

#     db: Session = SessionLocal()
#     try:
#         document = Document(
#             property_id=property_id,
#             doc_type=doc_type,
#             content=file_data,
#             upload_date=datetime.now()
#         )
#         db.add(document)
#         db.commit()

#         # Embed and store the text in vector DB
#         embed_and_store(text, property_id, doc_type)

#         return {"message": "Document uploaded and processed successfully"}
#     finally:
#         db.close()


# @app.get("/property/{property_id}")
# async def get_property_details(property_id: int):
#     """Fetches full property details and all uploaded documents."""
#     conn = await get_db()
#     try:
#         # Fetch property details
#         property_query = "SELECT * FROM properties WHERE id = $1"
#         property_data = await conn.fetchrow(property_query, property_id)
#         if not property_data:
#             raise HTTPException(status_code=404, detail="Property not found")

#         # Fetch associated documents with IDs
#         docs = {}
#         for table in DOCUMENT_CATEGORIES.keys():
#             query = f"SELECT id, document_type, uploaded_at FROM {table} WHERE property_id = $1 ORDER BY uploaded_at DESC"
#             docs[table] = await conn.fetch(query, property_id)

#     finally:
#         await conn.close()
    
#     return {
#         "property": dict(property_data),
#         "documents": {k: [dict(doc) for doc in v] for k, v in docs.items()}
#     }


# ✅ API ROUTES FIRST
@app.get("/properties")
async def list_properties():
    """Fetches all properties."""
    conn = await get_db()
    try:
        properties = await conn.fetch("SELECT * FROM properties")
        if not properties:
            raise HTTPException(status_code=404, detail="No properties found")
        return {"properties": [dict(p) for p in properties]}
    finally:
        await conn.close()

@app.get("/api/property/{property_id}")
async def get_property_details(property_id: int):
    """Fetches full property details and all uploaded documents."""
    conn = await get_db()
    try:
        property_query = "SELECT * FROM properties WHERE id = $1"
        property_data = await conn.fetchrow(property_query, property_id)
        if not property_data:
            raise HTTPException(status_code=404, detail="Property not found")

        docs = {}
        for table in DOCUMENT_CATEGORIES.keys():
            query = f"SELECT id, document_type, uploaded_at FROM {table} WHERE property_id = $1 ORDER BY uploaded_at DESC"
            docs[table] = await conn.fetch(query, property_id)
    finally:
        await conn.close()
    
    return {
        "property": dict(property_data),
        "documents": {k: [dict(doc) for doc in v] for k, v in docs.items()}
    }

@app.get("/document/{doc_id}")
async def get_document(doc_id: int):
    """Retrieves a document as a downloadable PDF."""
    conn = await get_db()
    try:
        for table in DOCUMENT_CATEGORIES.keys():
            query = f"SELECT document, document_type FROM {table} WHERE id = $1"
            document_data = await conn.fetchrow(query, doc_id)
            if document_data:
                return Response(
                    content=document_data["document"],
                    media_type="application/pdf",  # Set MIME type to PDF
                    headers={"Content-Disposition": f"inline; filename={document_data['document_type']}.pdf"}
                )
    finally:
        await conn.close()
    
    raise HTTPException(status_code=404, detail="Document not found")


# @app.post("/add-property")
# async def add_property(address: str = Form(...), purchase_price: float = Form(...)):
#     """Adds a new property to the database."""
#     conn = await get_db()
#     try:
#         query = "INSERT INTO properties (address, purchase_price, status) VALUES ($1, $2, 'purchased') RETURNING id"
#         new_id = await conn.fetchval(query, address, purchase_price)
#     finally:
#         await conn.close()
    
#     return {"message": "Property added", "property_id": new_id}


@app.post("/add-property")
async def add_property(
    property_id: int = Form(...),
    address: str = Form(...),
    purchase_price: float = Form(...),
    status: str = Form(...)
):
    try:
        conn = await get_db()
        try:
            query = """
                INSERT INTO properties (id, address, purchase_price, status)
                VALUES ($1, $2, $3, $4)
            """
            await conn.execute(query, property_id, address, purchase_price, status)
        finally:
            await conn.close()

        return {"message": "Property details added successfully", "property_id": property_id}
    except Exception as e:
        print(f"Error in add_property: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to add property details")


# @app.get("/properties")
# async def list_properties():
#     """Fetches all properties."""
#     conn = await get_db()
#     try:
#         properties = await conn.fetch("SELECT * FROM properties")
#         if not properties:
#             raise HTTPException(status_code=404, detail="No properties found")
#         return {"properties": [dict(p) for p in properties]}
#     finally:
#         await conn.close()
    
#     # return {"properties": [dict(p) for p in properties]}

# @app.get("/")
# async def serve_ui():
#     """Serves the UI."""
#     return FileResponse("static/index.html")


from chatbox import extract_intent_and_entities, route_chat_action

# @app.post("/api/chat")
# async def chat_with_bot(request: Request):
#     data = await request.json()
#     message = data.get("message")
#     if not message:
#         raise HTTPException(status_code=400, detail="Message is required")

#     try:
#         conn = await get_db()
#         try:
#             result =  extract_intent_and_entities(message)
#             response = await route_chat_action(result["intent"], result["entities"], conn)
            
#         finally:
#             await conn.close()
#         return {"response": response}
#     except Exception as e:
#         print(f"Chatbot error: {str(e)}")
#         return {"response": "Sorry, something went wrong while processing your message."}

class ChatSession:
    def __init__(self):
        self.context = {
            "property_id": None,
            "document_type": None
        }

    def update_context(self, entities):
        if 'property_id' in entities:
            self.context['property_id'] = entities['property_id']
        if 'document_type' in entities:
            self.context['document_type'] = entities['document_type']

    def fill_missing(self, entities):
        if 'property_id' not in entities and self.context['property_id']:
            entities['property_id'] = self.context['property_id']
        if 'document_type' not in entities and self.context['document_type']:
            entities['document_type'] = self.context['document_type']
        return entities

session = ChatSession()



@app.post("/api/chat")
async def chat_with_bot(request: Request):
    data = await request.json()
    message = data.get("message")
    if not message:
        raise HTTPException(status_code=400, detail="Message is required")

    try:
        conn = await get_db()
        try:
            result = extract_intent_and_entities(message)

            # Fill missing context from session
            filled_entities = session.fill_missing(result["entities"])

            # Update session with new info
            session.update_context(filled_entities)

            # Route action with filled entities
            response = await route_chat_action(result["intent"], filled_entities, conn)
        finally:
            await conn.close()
        return {"response": response}
    except Exception as e:
        print(f"Chatbot error: {str(e)}")
        return {"response": "Sorry, something went wrong while processing your message."}



# @app.post("/api/chat/rag")
# async def chat_rag(property_id: int, query: str):
#     try:
#         chunks = retrieve_relevant_chunks(query, property_id)
#         answer = generate_answer(query, chunks)
#         return {"answer": answer}
#     except Exception as e:
#         print(f"RAG chatbot error: {str(e)}")
#         raise HTTPException(status_code=500, detail="Failed to process query with RAG")

# In-memory history storage (use a proper store like Redis or DB in prod)
chat_sessions = {}

@app.post("/api/chat/rag")
async def chat_rag(request: Request):
    data = await request.json()
    property_id = data.get("property_id")
    query = data.get("query")
    session_id = data.get("session_id")  # Unique per user/session (e.g., property_30_user_abc)

    if not query or not property_id or not session_id:
        raise HTTPException(status_code=400, detail="Missing query, property ID, or session ID.")

    try:
        # Retrieve document context
        chunks = retrieve_relevant_chunks(query, property_id)
        doc_context = "\n".join([chunk['text'] for chunk in chunks])

        # Build or extend session history
        history = chat_sessions.get(session_id, [])
        history.append({"role": "user", "content": query})

        # Add document context and system message
        messages = [
            {"role": "system", "content": "You are a helpful assistant answering questions about property documents. Infer logical answers such as recurring monthly payments based on the context if not explicitly stated."},
            {"role": "system", "content": f"Relevant document content:\n{doc_context}"}
        ] + history

        # Call the LLM
        response = openai.ChatCompletion.create(
            model="gpt-4",  # or "gpt-3.5-turbo"
            messages=messages,
            temperature=0.3
        )

        # Store assistant response in session
        assistant_reply = response['choices'][0]['message']['content']
        history.append({"role": "assistant", "content": assistant_reply})
        chat_sessions[session_id] = history

        return {"answer": assistant_reply}

    except Exception as e:
        print(f"RAG chatbot error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process query with RAG")


@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    """Serve frontend only if it's not an API route"""
    api_routes = ["property", "document", "upload", "add-property", "properties"]
    if any(full_path.startswith(route) for route in api_routes):
        raise HTTPException(status_code=404, detail="API route not found")
    
    index_path = os.path.join("build", "index.html")
    return FileResponse(index_path)



