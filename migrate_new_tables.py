#!/usr/bin/env python3
"""
migrate_new_tables.py
Run once to create feed_entries and farm_logs tables.
Usage: python migrate_new_tables.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from models.db import get_connection

SQL = [
    """
    CREATE TABLE IF NOT EXISTS feed_entries (
        id         INT AUTO_INCREMENT PRIMARY KEY,
        user_id    INT NOT NULL,
        date       DATE NOT NULL,
        feed_time  VARCHAR(20)  DEFAULT '',
        feed_type  VARCHAR(50)  DEFAULT '',
        quantity   DOUBLE       DEFAULT 0,
        notes      TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    """
    CREATE TABLE IF NOT EXISTS farm_logs (
        id          INT AUTO_INCREMENT PRIMARY KEY,
        user_id     INT NOT NULL,
        type        VARCHAR(20)  NOT NULL,
        date        DATE         NOT NULL,
        description TEXT         NOT NULL,
        animal_id   VARCHAR(20)  DEFAULT NULL,
        created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
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
