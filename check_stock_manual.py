import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from models.db import get_connection

def check_stock():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM feed_stock")
            rows = cur.fetchall()
            print(f"Items in feed_stock: {len(rows)}")
            for r in rows:
                print(r)
    except Exception as e:
        print(f"Error checking stock: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_stock()
