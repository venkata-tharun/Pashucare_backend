from models.db import get_connection

def migrate():
    print("Starting migration: Create vaccinations table")
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Create vaccinations table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS vaccinations (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    animal_id INT NOT NULL,
                    vaccine_name VARCHAR(255) NOT NULL,
                    date_given DATE NOT NULL,
                    next_due_date DATE,
                    batch_number VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (animal_id) REFERENCES animals(id) ON DELETE CASCADE
                )
            """)
            print("Table 'vaccinations' created successfully.")
            conn.commit()
    except Exception as e:
        print(f"Migration failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
