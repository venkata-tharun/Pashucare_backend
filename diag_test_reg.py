
from models.db import get_connection

def check():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM otp_codes WHERE email_or_phone = 'test_reg@gmail.com' ORDER BY id DESC LIMIT 1")
            code = cur.fetchone()
            if code:
                print(f"✅ OTP found in DB: {code}")
            else:
                print("❌ OTP NOT found in DB for 'test_reg@gmail.com'")
                
    finally:
        conn.close()

if __name__ == "__main__":
    check()
