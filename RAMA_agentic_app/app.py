import os
import psycopg2
from io import BytesIO
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

import gradio as gr
from agent.agentic import AssistantManager
from agent.tools.document_tool import store_document, delete_document

load_dotenv()
assistant_mgr = AssistantManager()


app = FastAPI()

@app.get("/docs/{doc_id}")
def get_document(doc_id: int):
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cur = conn.cursor()

    for table in ['purchase_documents', 'renovation_documents', 'sales_documents']:
        cur.execute(f"SELECT document, document_type FROM {table} WHERE id = %s", (doc_id,))
        result = cur.fetchone()
        if result:
            content, doc_type = result
            if content is None:
                raise HTTPException(status_code=404, detail="Document is empty.")
            return StreamingResponse(BytesIO(content), media_type="application/pdf",
                headers={"Content-Disposition": f"inline; filename={doc_type}_{doc_id}.pdf"}
            )

    raise HTTPException(status_code=404, detail="Document not found.")



def get_property_addresses():
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cur = conn.cursor()
    cur.execute("SELECT address FROM properties")
    addresses = [row[0] for row in cur.fetchall()]
    conn.close()
    return addresses

property_addresses = get_property_addresses()

category_doc_types = {
    "purchase": ["notary_deed", "deposit", "contract", "registration", "tax_itp_iba"],
    "renovation": ["builder_payments", "land_plans", "budget", "surveyor_contract"],
    "sales": ["sale_contract", "payment_certification"]
}

def chat_interface(message, history):
    return assistant_mgr.handle_message(message)


with gr.Blocks() as io:
    gr.Markdown("## 🏡 RAMA Agentic Real Estate Assistant")

    gr.ChatInterface(fn=chat_interface)

    with gr.Row():
        with gr.Accordion("📤 Upload a Document", open=False):
            cat_dropdown = gr.Dropdown(choices=list(category_doc_types.keys()), label="Document Category")
            prop_dropdown = gr.Textbox(label="Property Address")
            doc_type_dropdown = gr.Dropdown(choices=[], label="Document Type")
            file_upload = gr.File(label="Upload PDF", file_types=[".pdf"])
            upload_btn = gr.Button("Upload Document")
            upload_output = gr.Textbox(label="Upload Status")

            def update_doc_types(cat):
                return gr.update(choices=category_doc_types.get(cat, []))

            def upload_callback(cat, address, doc_type, file):
                return store_document(address, cat, doc_type, file)

            cat_dropdown.change(fn=update_doc_types, inputs=[cat_dropdown], outputs=[doc_type_dropdown])
            upload_btn.click(fn=upload_callback, inputs=[cat_dropdown, prop_dropdown, doc_type_dropdown, file_upload], outputs=[upload_output])

        with gr.Accordion("🗑️ Delete a Document", open=False):
            del_cat = gr.Dropdown(choices=list(category_doc_types.keys()), label="Document Category")
            del_prop = gr.Dropdown(choices=property_addresses, label="Property Address")
            del_doc_type = gr.Dropdown(choices=[], label="Document Type")
            delete_btn = gr.Button("Delete Document")
            delete_output = gr.Textbox(label="Deletion Result")

            def update_del_doc_types(cat):
                return gr.update(choices=category_doc_types.get(cat, []))

            def delete_callback(cat, address, doc_type):
                return delete_document(address, cat, doc_type)

            del_cat.change(fn=update_del_doc_types, inputs=[del_cat], outputs=[del_doc_type])
            delete_btn.click(fn=delete_callback, inputs=[del_cat, del_prop, del_doc_type], outputs=[delete_output])


gr.mount_gradio_app(app, io, path="/")
