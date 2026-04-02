import pymysql
import pymysql.cursors
from config import DB_CONFIG

def create_otp_table():
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
            cur.execute("""
            CREATE TABLE IF NOT EXISTS otp_codes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                email_or_phone VARCHAR(255) NOT NULL,
                otp_code VARCHAR(10) NOT NULL,
                context VARCHAR(50) NOT NULL, -- e.g., 'registration', 'forgot_password'
                expires_at DATETIME NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX (email_or_phone)
            );
            """)
            conn.commit()
            print("Successfully ensured otp_codes table exists.")
    finally:
        conn.close()

if __name__ == "__main__":
    create_otp_table()
