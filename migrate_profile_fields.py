from models.db import get_connection

def migrate():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Check if 'phone' column exists
            cur.execute("SHOW COLUMNS FROM users LIKE 'phone'")
            if not cur.fetchone():
                print("Adding 'phone' column to 'users' table...")
                cur.execute("ALTER TABLE users ADD COLUMN phone VARCHAR(20) AFTER email_or_phone")
                conn.commit()
                print("Column 'phone' added successfully.")
            else:
                print("Column 'phone' already exists.")
    except Exception as e:
        print(f"Error during migration: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
