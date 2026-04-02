
from models.db import get_connection

def check():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Check user
            cur.execute("SELECT * FROM users WHERE email_or_phone = 'tharunyadav973@gmail.com'")
            user = cur.fetchone()
            if user:
                print(f"✅ User found: {user}")
            else:
                print("❌ User 'tharunyadav973@gmail.com' NOT found!")
                
            # Check OTP codes
            cur.execute("SELECT * FROM otp_codes WHERE email_or_phone = 'tharunyadav973@gmail.com' ORDER BY id DESC LIMIT 5")
            codes = cur.fetchall()
            if codes:
                print("--- Recent OTP Codes for this user ---")
                for code in codes:
                    print(code)
            else:
                print("No OTP codes found for this user.")
                
    finally:
        conn.close()

if __name__ == "__main__":
    check()
