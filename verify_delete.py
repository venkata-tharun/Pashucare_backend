
from models.db import get_connection

def verify_deletion():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # 1. Create a dummy user
            cur.execute("INSERT INTO users (full_name, email_or_phone, password_hash) VALUES ('Delete Test', 'delete_test@gmail.com', 'hash')")
            user_id = cur.lastrowid
            
            # 2. Add some dummy data linked to this user
            cur.execute("INSERT INTO animals (user_id, name, tag) VALUES (%s, 'Test Cow', 'T-001')", (user_id,))
            animal_id = cur.lastrowid
            
            cur.execute("INSERT INTO milk_entries (user_id, date, am, noon, pm, total_used) VALUES (%s, '2026-03-30', 10, 0, 10, 20)", (user_id,))
            
            conn.commit()
            print(f"✅ Created test user {user_id} and related data.")
            
            # 3. Delete the user
            cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
            conn.commit()
            print(f"✅ Deleted test user {user_id}.")
            
            # 4. Verify everything is gone
            cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            if cur.fetchone(): print("❌ User NOT deleted!")
            else: print("✅ User deleted.")
            
            cur.execute("SELECT * FROM animals WHERE user_id = %s", (user_id,))
            if cur.fetchone(): print("❌ Animal NOT deleted!")
            else: print("✅ Animal deleted (cascade worked).")
            
            cur.execute("SELECT * FROM milk_entries WHERE user_id = %s", (user_id,))
            if cur.fetchone(): print("❌ Milk entry NOT deleted!")
            else: print("✅ Milk entry deleted (cascade worked).")
            
    finally:
        conn.close()

if __name__ == "__main__":
    verify_deletion()
