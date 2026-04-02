#!/usr/bin/env python3
"""
migrate_feeding_schedules.py
Migration to create feeding_schedules table.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from models.db import get_connection

SQL = [
    """
    CREATE TABLE IF NOT EXISTS feeding_schedules (
        id           INT AUTO_INCREMENT PRIMARY KEY,
        user_id      INT NOT NULL,
        time         VARCHAR(20) NOT NULL,
        title        VARCHAR(255) NOT NULL,
        items_json   TEXT NOT NULL,
        is_completed BOOLEAN DEFAULT FALSE,
        created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX (user_id),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """
]

def run():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            for stmt in SQL:
                cur.execute(stmt)
                print(f"✅  Executed: {stmt.strip()[:60]}...")
        conn.commit()
        print("\n✅  Migration complete.")
    except Exception as e:
        print(f"\n❌  Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    run()
