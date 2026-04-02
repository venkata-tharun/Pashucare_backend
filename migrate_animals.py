#!/usr/bin/env python3
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from models.db import get_connection

SQL = [
    "ALTER TABLE animals ADD COLUMN age VARCHAR(100) DEFAULT '' AFTER breed;",
    "ALTER TABLE animals ADD COLUMN weight VARCHAR(100) DEFAULT '' AFTER age;",
    "ALTER TABLE animals ADD COLUMN gender VARCHAR(100) DEFAULT 'Female' AFTER weight;"
]

def run():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            for stmt in SQL:
                try:
                    cur.execute(stmt)
                    print(f"✅  Executed: {stmt}")
                except Exception as e:
                    print(f"⚠️  Skipped/Error: {e}")
        conn.commit()
        print("\n✅  Migration complete.")
    except Exception as e:
        print(f"\n❌  Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    run()
