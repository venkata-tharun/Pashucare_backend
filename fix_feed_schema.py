from models.db import get_connection

def fix():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Check if feed_entries exists
            cur.execute("SHOW TABLES LIKE 'feed_entries'")
            if not cur.fetchone():
                print("Table feed_entries missing. Creating it...")
                cur.execute("""
                    CREATE TABLE feed_entries (
                        id         INT AUTO_INCREMENT PRIMARY KEY,
                        user_id    INT NOT NULL,
                        date       DATE NOT NULL,
                        feed_time  VARCHAR(50)  DEFAULT '',
                        feed_type  VARCHAR(100) DEFAULT '',
                        target_group VARCHAR(100) DEFAULT '',
                        quantity   DOUBLE       DEFAULT 0,
                        notes      TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """)
            else:
                # Table exists, check for target_group column
                cur.execute("DESCRIBE feed_entries")
                columns = [row['Field'] for row in cur.fetchall()]
                if 'target_group' not in columns:
                    print("Adding 'target_group' column to feed_entries...")
                    cur.execute("ALTER TABLE feed_entries ADD COLUMN target_group VARCHAR(100) DEFAULT '' AFTER feed_type")
                
                if 'feed_time' in columns:
                     # ensure enough length
                     cur.execute("ALTER TABLE feed_entries MODIFY COLUMN feed_time VARCHAR(50) DEFAULT ''")
                if 'feed_type' in columns:
                     cur.execute("ALTER TABLE feed_entries MODIFY COLUMN feed_type VARCHAR(100) DEFAULT ''")
            
            print("Ensuring farm_logs table...")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS farm_logs (
                    id          INT AUTO_INCREMENT PRIMARY KEY,
                    user_id     INT NOT NULL,
                    type        VARCHAR(100) NOT NULL,
                    date        DATE         NOT NULL,
                    description TEXT         NOT NULL,
                    animal_id   VARCHAR(100)  DEFAULT NULL,
                    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            
            conn.commit()
            print("Database fix complete!")
    except Exception as e:
        print(f"Error during prefix: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    fix()
