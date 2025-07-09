import psycopg2
import os

class FinancialTool:
    def __init__(self):
        self.conn = psycopg2.connect(os.getenv("DATABASE_URL"))

    def get_summary(self):
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT p.address, p.purchase_price, p.sale_price,
                    COALESCE(SUM(py.amount), 0) AS total_paid
                FROM properties p
                LEFT JOIN payments py ON p.id = py.property_id
                GROUP BY p.id
            """)
            rows = cur.fetchall()
            summary = [
                f"{row[0]}: Bought at {row[1]}, Sold at {row[2]}, Total Paid: {row[3]}"
                for row in rows
            ]
            return "\n".join(summary)