
from models.db import get_connection

def check():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Check for any registration OTPs
            cur.execute("SELECT * FROM otp_codes WHERE context = 'registration' ORDER BY id DESC LIMIT 5")
            codes = cur.fetchall()
            if codes:
                print("--- Recent Registration OTP Codes ---")
                for code in codes:
                    print(code)
            else:
                print("No registration OTP codes found.")
                
    finally:
        conn.close()

if __name__ == "__main__":
    check()
