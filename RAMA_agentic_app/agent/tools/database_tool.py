import os
import psycopg2

class DatabaseTool:
    def __init__(self):
        self.conn = psycopg2.connect(os.getenv("DATABASE_URL"))

    def get_property_stats(self):
        with self.conn.cursor() as cur:
            cur.execute("SELECT status, COUNT(*) FROM properties GROUP BY status")
            return dict(cur.fetchall())