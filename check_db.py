import pymysql
import pymysql.cursors
from config import DB_CONFIG

def check_schema():
    conn = pymysql.connect(
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        db=DB_CONFIG["db"],
        charset=DB_CONFIG["charset"],
        cursorclass=pymysql.cursors.DictCursor,
    )
    try:
        with conn.cursor() as cur:
            cur.execute("DESCRIBE health_records")
            rows = cur.fetchall()
            print("Columns in health_records:")
            for r in rows:
                print(f"- {r['Field']} ({r['Type']})")
    finally:
        conn.close()

if __name__ == "__main__":
    check_schema()
