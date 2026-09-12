import os

import psycopg
from dotenv import load_dotenv

load_dotenv()


database_url = os.environ["DATABASE_URL"]


with psycopg.connect(database_url) as connection:

    with connection.cursor() as cursor:

        cursor.execute("""
            SELECT
                category,
                SUM(amount_paise) AS total_paise
            FROM expenses
            GROUP BY category
            ORDER BY total_paise DESC;
            """)

        rows = cursor.fetchall()

        for row in rows:
            print(row)
