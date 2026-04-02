from models.db import get_connection

conn = get_connection()
try:
    with conn.cursor() as cur:
        # Create sanitation_scores table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS sanitation_scores (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                score INT NOT NULL,
                tasks_json TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # In MySQL, entry_time is DATETIME, which doesn't accept "Z" at the end directly from ISO format if strict mode is on.
        # But for Python script we can just fix the backend route visitors.py to strip Z or replace T with space
    conn.commit()
finally:
    conn.close()

print("Database tables ensured.")
