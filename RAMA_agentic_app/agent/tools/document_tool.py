import os
import psycopg2
from io import BytesIO
import smtplib
from email.message import EmailMessage

class DocumentTool:
    def __init__(self):
        self.conn = psycopg2.connect(os.getenv("DATABASE_URL"))

    def list_documents(self):
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT p.address, 'purchase' AS category, pd.document_type, pd.uploaded_at, pd.id
                FROM purchase_documents pd JOIN properties p ON pd.property_id = p.id
                UNION ALL
                SELECT p.address, 'renovation', rd.document_type, rd.uploaded_at, rd.id
                FROM renovation_documents rd JOIN properties p ON rd.property_id = p.id
                UNION ALL
                SELECT p.address, 'sales', sd.document_type, sd.uploaded_at, sd.id
                FROM sales_documents sd JOIN properties p ON sd.property_id = p.id
            """)
            rows = cur.fetchall()

        from collections import defaultdict
        grouped = defaultdict(lambda: defaultdict(list))
        for address, category, doc_type, uploaded_at, doc_id in rows:
            ts = uploaded_at.strftime('%Y-%m-%d %H:%M')
            link = f"http://localhost:7860/docs/{doc_id}"
            name = doc_type.replace('_', ' ').title()
            grouped[address][category].append(f"- [{name}]({link}) (uploaded at {ts})")

        lines = []
        for address, categories in grouped.items():
            lines.append(f"**🏠 {address}**")
            for cat, docs in categories.items():
                lines.append(f"**{cat.title()} Documents:**")
                lines.extend(docs)
            lines.append("")
        return "\n".join(lines)

    def email_document(self, property_address, document_name, email):
        property_id = get_property_id(property_address)
        if not property_id:
            return "❌ Property not found."

        doc_key = document_name.lower().replace(".pdf", "").replace(" ", "_")

        for category in ["purchase", "renovation", "sales"]:
            table = f"{category}_documents"
            with self.conn.cursor() as cur:
                cur.execute(
                    f"""
                    SELECT document_type, document
                    FROM {table}
                    WHERE property_id = %s AND document_type ILIKE %s
                    LIMIT 1
                    """,
                    (property_id, f"%{doc_key}%")
                )
                row = cur.fetchone()
                if row:
                    doc_type, content = row
                    filename = f"{doc_type}.pdf"
                    subject = f"📄 Requested Document: {doc_type.replace('_', ' ').title()}"
                    body = f"Attached is the requested document for {property_address}."

                    send_email_with_attachment(email, subject, body, filename, content)
                    return f"📧 Document '{filename}' sent to {email}!"

        return "❌ Document not found for this property."
    
    def delete_documents_chat(self, address,category, document_type, filter_keywords=None):
        """
        Deletes documents from the database.
        If filter_keywords is None, delete all documents.
        If filter_keywords is a list, delete documents whose names match any keyword.
        """
        property_id = get_property_id(address)
        table = f"{category}_documents"
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        cur = conn.cursor() 
        
        try:
            if filter_keywords is None:
                cur.execute(f"DELETE FROM {table};")
                message = f"All documents in '{category}' category deleted."
            else:
                deleted_count = 0
                for keyword in filter_keywords:
                    cur.execute(f"DELETE FROM {table} WHERE property_id = %s AND document_type = %s",(property_id, document_type))
                    deleted_count += cur.rowcount
                message = f"{deleted_count} document(s) deleted in '{category}' category matching: {', '.join(filter_keywords)}"
            
            conn.commit()
            return f"All documents from property '{property_id}' are deleted."
        
        except Exception as e:
            conn.rollback()
            return f"message: {str(e)}"

        # finally:
        #     cur.close()
        #     conn.close()



def get_property_id(address):
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cur = conn.cursor()
    cur.execute("SELECT id FROM properties WHERE address = %s", (address,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None

# 🔼 Upload document
def store_document(address, category, doc_type, file):
    property_id = get_property_id(address)
    if not property_id:
        return "Property not found."

    content = BytesIO(file.read()).getvalue()
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cur = conn.cursor()

    table = f"{category}_documents"
    cur.execute(
        f"INSERT INTO {table} (property_id, document_type, document, uploaded_at) VALUES (%s, %s, %s, now())",
        (property_id, doc_type, psycopg2.Binary(content))
    )
    conn.commit()
    conn.close()
    return f"✅ {doc_type.replace('_', ' ').title()} uploaded for {address}."

def delete_document(address, category, doc_type):
    property_id = get_property_id(address)
    if not property_id:
        return "Property not found."

    table = f"{category}_documents"
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cur = conn.cursor()

    cur.execute(
        f"DELETE FROM {table} WHERE property_id = %s AND document_type = %s",
        (property_id, doc_type)
    )
    deleted = cur.rowcount
    conn.commit()
    conn.close()

    if deleted == 0:
        return "⚠️ No document found to delete."
    return f"🗑️ Deleted {deleted} document(s) of type {doc_type.replace('_', ' ').title()} for {address}."


def send_email_with_attachment(to_email, subject, body, filename, file_content):
    msg=EmailMessage()
    msg['Subject']= subject
    msg["From"]=os.getenv("EMAIL_SENDER")
    msg["To"]= to_email
    msg.set_content(body)
    msg.add_attachment(file_content,maintype='application',subtype='pdf', filename=filename)

    with smtplib.SMTP_SSL("smtp.gmail.com",465) as smtp:
        smtp.login(os.getenv("EMAIL_SENDER"), os.getenv("EMAIL_PASSWORD"))
        smtp.send_message(msg)


