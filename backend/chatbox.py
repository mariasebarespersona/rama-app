

# chatbot.py
import os
from typing import Dict
from openai import OpenAI
from dotenv import load_dotenv
import fitz  # PyMuPDF
import io



# Load the .env file
load_dotenv()

# Get your API key
api_key = os.getenv("OPENAI_API_KEY")

# Create OpenAI client
client = OpenAI(api_key=api_key)


def extract_intent_and_entities(message: str) -> Dict:
    prompt = f"""
    You are an assistant that extracts intent and entities from user questions related to a real estate management system. 
    Classify each message into one intent and extract entities.
    Use the information from the document chunks below and reason step by step. 
    If a document says that a payment happens monthly on a specific day, and the last payment was on May 15th, infer that the next payment is on June 15th.


    Example 1:
    User: When was the last builder payment made for property 30?
    Intent: extract_fact_from_document
    Entities: {{"property_id": 30, "document_type": "builder_payments", "fact": "last_payment_date"}}

    Example 2:
    User: How many contracts do we have for property 10?
    Intent: count_documents
    Entities: {{"property_id": 10, "document_type": "contract"}}


    ---
    User: {message}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )

        if not response.choices:
            raise ValueError("No choices returned from OpenAI API.")

        content = response.choices[0].message.content
        lines = content.strip().split("\n")
        if len(lines) < 2:
            raise ValueError("Incomplete response from GPT.")

        intent = lines[0].replace("Intent: ", "").strip()
        entities_line = lines[1].replace("Entities: ", "").strip()
        entities = eval(entities_line)  # ⚠️ Only if you're sure input is trusted

        return {"intent": intent, "entities": entities}

    except Exception as e:
        print("Chatbot error:", e)
        return {"intent": "error", "entities": {}}


async def route_chat_action(intent: str, entities: Dict, db) -> str:
    if intent == "get_last_payment":
        query = """
            SELECT MAX(uploaded_at) AS last_payment
            FROM renovation_documents
            WHERE document_type = $1
        """
        result = await db.fetchval(query, entities['document_type'])
        return f"Last {entities['document_type'].replace('_', ' ')} was uploaded on {result.strftime('%d %b %Y')}" if result else "No records found."

    elif intent == "count_documents":
        count = 0
        for table in ["purchase_documents", "renovation_documents", "sales_documents"]:
            query = f"SELECT COUNT(*) FROM {table} WHERE property_id = $1 AND document_type ILIKE '%' || $2 || '%'"
            count += await db.fetchval(query, entities['property_id'], entities['document_type'])
        return f"There are {count} {entities['document_type']}s for property {entities['property_id']}"

    elif intent == "get_document_content":
        return await get_latest_document_summary(entities, db)

    elif intent == "extract_fact_from_document":
        return await extract_fact_from_latest_document(entities, db)

    elif intent == "count_properties":
        query = "SELECT COUNT(*) FROM properties"
        count = await db.fetchval(query)
        return f"There are {count} properties in your system."

    return f"Sorry, I don't know how to handle the intent: {intent}"


async def get_latest_document_summary(entities: Dict, db) -> str:
    property_id = entities.get("property_id")
    doc_type = entities.get("document_type")

    if not property_id or not doc_type:
        return "Please specify both the property ID and the document type."

    table = get_table_for_document_type(doc_type)
    if not table:
        return f"I couldn't find a table for the document type: {doc_type}"

    query = f"""
        SELECT document 
        FROM {table}
        WHERE property_id = $1 AND document_type = $2
        ORDER BY uploaded_at DESC LIMIT 1
    """
    result = await db.fetchrow(query, property_id, doc_type)

    if not result:
        return f"No document of type '{doc_type}' found for property {property_id}."

    try:
        document_bytes = result["document"]
        pdf = fitz.open(stream=io.BytesIO(document_bytes), filetype="pdf")
        text = "\n".join(page.get_text() for page in pdf)
        if not text.strip():
            return f"The {doc_type} document for property {property_id} appears to be empty or unreadable."

        summary = await summarize_text(text)
        return f"Here is the summary of the {doc_type} document for property {property_id}:\n\n{summary[:1000]}..."

    except Exception as e:
        return f"Failed to read the document content: {str(e)}"


async def extract_fact_from_latest_document(entities: Dict, db) -> str:
    property_id = entities.get("property_id")
    doc_type = entities.get("document_type")
    fact = entities.get("fact")

    if not property_id or not doc_type or not fact:
        return "Missing property ID, document type, or fact to extract."

    table = get_table_for_document_type(doc_type)
    if not table:
        return f"I couldn't find a table for the document type: {doc_type}"

    query = f"""
        SELECT document 
        FROM {table}
        WHERE property_id = $1 AND document_type = $2
        ORDER BY uploaded_at DESC LIMIT 1
    """
    result = await db.fetchrow(query, property_id, doc_type)

    if not result:
        return f"No document of type '{doc_type}' found for property {property_id}."

    try:
        document_bytes = result["document"]
        pdf = fitz.open(stream=io.BytesIO(document_bytes), filetype="pdf")
        text = "\n".join(page.get_text() for page in pdf)

        if not text.strip():
            return f"The {doc_type} document for property {property_id} appears to be empty or unreadable."

        extract_prompt = f"""
        The following is a document from a real estate system. The user wants to know the {fact}.
        If this info is present, return it in a natural sentence. If not, say it wasn't found.

        Document:
        {text}
        """

        extract_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": extract_prompt}],
            temperature=0.3
        )

        return extract_response.choices[0].message.content.strip()

    except Exception as e:
        return f"Failed to extract fact from document: {str(e)}"


def get_table_for_document_type(doc_type: str) -> str:
    mapping = {
        "purchase_documents": ['contract', 'notary_deed', 'notary_registration', 'deposit', 'tax_ITP_IBA'],
        "renovation_documents": ['geotechnical_study', 'land_plans', 'architect_plans', 'budget', 'architect_contract', 'surveyor_contract', 'building_license', 'contractor_contract', 'trade_contract', 'builder_payments'],
        "sales_documents": ['sale_contract', 'payment_certification']
    }
    for tbl, types in mapping.items():
        if doc_type in types:
            return tbl
    return None


async def summarize_text(text: str) -> str:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Summarize the following document: {text}"}],
        temperature=0.3
    )
    return response.choices[0].message.content.strip()







