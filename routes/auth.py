from flask import Blueprint, request, jsonify, session, current_app
from models.db import get_connection
from werkzeug.security import generate_password_hash, check_password_hash
from utils.otp_utils import generate_otp, validate_password_complexity, send_otp_email
from datetime import datetime, timedelta
import pytz
import uuid

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    """Generates and sends an OTP for new user registration."""
    data = request.get_json()
    full_name = data.get("full_name", data.get("fullName", "")).strip()
    farm_name = data.get("farm_name", data.get("farmName", "")).strip()
    email_or_phone = data.get("email_or_phone", data.get("emailOrPhone", "")).strip()
    password = data.get("password", "")

    import re
    name_regex = r"^[A-Za-z\s]{2,}$"
    if not re.match(name_regex, full_name):
        return jsonify({"error": "Full Name must contain only alphabets and be at least 2 characters."}), 400
    if not re.match(name_regex, farm_name):
        return jsonify({"error": "Farm Name must contain only alphabets and be at least 2 characters."}), 400

    if not email_or_phone or not password:
        return jsonify({"error": "email_or_phone and password are required"}), 400
        
    # Phone validation if numeric
    if email_or_phone.isdigit():
        if len(email_or_phone) != 10:
            return jsonify({"error": "Phone number must be 10 digits"}), 400
        if len(set(email_or_phone)) == 1:
            return jsonify({"error": "Invalid phone number (too repetitive)"}), 400
        if email_or_phone[0] not in "6789":
            return jsonify({"error": "Phone number must start with 6, 7, 8, or 9"}), 400

    if not validate_password_complexity(password):
        return jsonify({"error": "Password must be at least 8 characters long and contain uppercase, lowercase, number, and special character."}), 400


    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Check if user already exists
            cur.execute("SELECT id FROM users WHERE email_or_phone = %s", (email_or_phone,))
            if cur.fetchone():
                return jsonify({"error": "User already exists"}), 409
                
            # Create User Directly
            cur.execute(
                "INSERT INTO users (full_name, email_or_phone, farm_name, password_hash) VALUES (%s, %s, %s, %s)",
                (full_name, email_or_phone, farm_name, generate_password_hash(password))
            )
            conn.commit()

    finally:
        conn.close()

    return jsonify({"message": "Account created successfully. Please login."}), 200

# Registration verification is no longer needed since we bypass OTP
# (Keeping the route definition for now to avoid breaking potential client references, 
# but it will return 404/Error if session is missing)
@auth_bp.route("/register/verify", methods=["POST"])
def verify_registration():
    return jsonify({"error": "Registration OTP no longer required. Please login directly."}), 410

@auth_bp.route("/login", methods=["POST"])
def login():

    data           = request.get_json()
    email_or_phone = data.get("email_or_phone", data.get("emailOrPhone", "")).strip()
    password       = data.get("password", "")

    if not email_or_phone or not password:
        return jsonify({"error": "email_or_phone and password are required"}), 400

    # Phone validation if numeric
    if email_or_phone.isdigit():
        if len(email_or_phone) != 10:
            return jsonify({"error": "Phone number must be 10 digits"}), 400
        if len(set(email_or_phone)) == 1:
            return jsonify({"error": "Invalid phone number (too repetitive)"}), 400
        if email_or_phone[0] not in "6789":
            return jsonify({"error": "Phone number must start with 6, 7, 8, or 9"}), 400

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE email_or_phone = %s", (email_or_phone,))
            user = cur.fetchone()
    finally:
        conn.close()

    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Invalid credentials"}), 401

    # ── Store user info in server-side session ──────────────────────
    session["user_id"]         = user["id"]
    session["email_or_phone"]  = user["email_or_phone"]
    session["phone"]           = user.get("phone", "")
    session["full_name"]       = user["full_name"]
    session["farm_name"]       = user["farm_name"]
    session.permanent          = True

    return jsonify({
        "message": "Logged in successfully",
        "user": {
            "id":             user["id"],
            "full_name":      user["full_name"],
            "email_or_phone": user["email_or_phone"],
            "phone":          user.get("phone", ""),
            "farm_name":      user["farm_name"],
        }
    }), 200


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"}), 200


@auth_bp.route("/me", methods=["GET"])
def me():
    """Return current logged-in user from session."""
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    return jsonify({
        "user": {
            "id":             session["user_id"],
            "full_name":      session["full_name"],
            "email_or_phone": session["email_or_phone"],
            "phone":          session.get("phone", ""),
            "farm_name":      session["farm_name"],
        }
    }), 200

@auth_bp.route("/profile/update", methods=["POST"])
def update_profile():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    data = request.get_json()
    full_name = data.get("full_name", "").strip()
    farm_name = data.get("farm_name", "").strip()
    email = data.get("email", "").strip()
    phone = data.get("phone", "").strip()

    import re
    name_regex = r"^[A-Za-z\s]{2,}$"
    if not re.match(name_regex, full_name):
        return jsonify({"error": "Full Name must contain only alphabets and be at least 2 characters."}), 400
    if not re.match(name_regex, farm_name):
        return jsonify({"error": "Farm Name must contain only alphabets and be at least 2 characters."}), 400
    
    email_regex = r"[A-Z0-9a-z._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,64}"
    if not re.match(email_regex, email):
        return jsonify({"error": "Invalid email format"}), 400
        
    digits = "".join([c for c in phone if c.isdigit()])
    if len(digits) != 10:
        return jsonify({"error": "Phone number must be 10 digits"}), 400
    if len(set(digits)) == 1:
        return jsonify({"error": "Invalid phone number (too repetitive)"}), 400
    if digits[0] not in "6789":
        return jsonify({"error": "Phone number must start with 6, 7, 8, or 9"}), 400

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE users SET full_name = %s, farm_name = %s, email_or_phone = %s, phone = %s WHERE id = %s",
                (full_name, farm_name, email, phone, session["user_id"])
            )
            conn.commit()
            
            session["full_name"] = full_name
            session["farm_name"] = farm_name
            session["email_or_phone"] = email
            session["phone"] = phone
    finally:
        conn.close()

    return jsonify({"message": "Profile updated successfully"}), 200


    
@auth_bp.route("/profile/delete", methods=["DELETE"])
def delete_account():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401
        
    user_id = session["user_id"]
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Delete user - cascading will handle the rest
            cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
            conn.commit()
            
            # Clear session
            session.clear()
            return jsonify({"message": "Account and all associated data deleted successfully."}), 200
            
    except Exception as e:
        print(f"Error deleting account: {e}")
        return jsonify({"error": "Failed to delete account."}), 500
    finally:
        conn.close()


@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json()
    email_or_phone = data.get("email_or_phone", data.get("emailOrPhone", "")).strip()
    
    if not email_or_phone:
        return jsonify({"error": "email_or_phone is required"}), 400

    # Phone validation if numeric
    if email_or_phone.isdigit():
        if len(email_or_phone) != 10:
            return jsonify({"error": "Phone number must be 10 digits"}), 400
        if len(set(email_or_phone)) == 1:
            return jsonify({"error": "Invalid phone number (too repetitive)"}), 400
        if email_or_phone[0] not in "6789":
            return jsonify({"error": "Phone number must start with 6, 7, 8, or 9"}), 400
        
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE email_or_phone = %s", (email_or_phone,))
            if not cur.fetchone():
                return jsonify({"error": "User does not exist"}), 404
                
            otp_code = generate_otp()
            expires_at = datetime.now() + timedelta(minutes=10)
            
            cur.execute("DELETE FROM otp_codes WHERE email_or_phone = %s AND context = %s", (email_or_phone, 'forgot_password'))
            
            cur.execute(
                "INSERT INTO otp_codes (email_or_phone, otp_code, context, expires_at) VALUES (%s, %s, %s, %s)",
                (email_or_phone, otp_code, 'forgot_password', expires_at)
            )
            conn.commit()
            
            from app import mail
            success = send_otp_email(mail, email_or_phone, otp_code, 'forgot_password')
            if not success:
                return jsonify({"error": "Failed to send OTP email."}), 500
                
    finally:
        conn.close()
        
    return jsonify({"message": "OTP sent successfully."}), 200

@auth_bp.route("/forgot-password/verify", methods=["POST"])
def verify_forgot_password():
    data = request.get_json()
    email_or_phone = data.get("email_or_phone", data.get("emailOrPhone", "")).strip()
    otp_code = data.get("otp", "").strip()
    
    print(f"DEBUG: Verifying OTP for {email_or_phone}: {otp_code}")
    
    if not email_or_phone or not otp_code:
        return jsonify({"error": "email_or_phone and otp are required"}), 400
        
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM otp_codes WHERE email_or_phone = %s AND context = 'forgot_password' AND otp_code = %s ORDER BY id DESC LIMIT 1",
                (email_or_phone, otp_code)
            )
            otp_record = cur.fetchone()
            
            if not otp_record:
                print(f"DEBUG: No OTP record found for {email_or_phone}")
                return jsonify({"error": "Invalid OTP"}), 400
                
            if otp_record['expires_at'] < datetime.now():
                print(f"DEBUG: OTP expired for {email_or_phone}")
                return jsonify({"error": "OTP has expired"}), 400
                
            # Generate a stateless reset token
            reset_token = str(uuid.uuid4())
            expires_at = datetime.now() + timedelta(minutes=20)
            
            # Store the token in the database instead of session
            cur.execute("DELETE FROM otp_codes WHERE email_or_phone = %s AND context = 'reset_token'", (email_or_phone,))
            cur.execute(
                "INSERT INTO otp_codes (email_or_phone, otp_code, context, expires_at) VALUES (%s, %s, %s, %s)",
                (email_or_phone, reset_token, 'reset_token', expires_at)
            )
            
            # Cleanup OTP
            cur.execute("DELETE FROM otp_codes WHERE email_or_phone = %s AND context = 'forgot_password'", (email_or_phone,))
            conn.commit()
            print(f"DEBUG: Reset token generated for {email_or_phone}: {reset_token}")
            
    finally:
        conn.close()
        
    return jsonify({
        "message": "OTP verified successfully.",
        "reset_token": reset_token
    }), 200

@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json()
    email_or_phone = data.get("email_or_phone", data.get("emailOrPhone", "")).strip()
    new_password = data.get("new_password", "")
    reset_token = data.get("reset_token", "").strip()
    
    print(f"DEBUG: Reset attempt for {email_or_phone}")
    
    if not email_or_phone or not new_password or not reset_token:
        return jsonify({"error": "email_or_phone, new_password and reset_token are required"}), 400
        
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Verify the token
            cur.execute(
                "SELECT * FROM otp_codes WHERE email_or_phone = %s AND context = 'reset_token' AND otp_code = %s ORDER BY id DESC LIMIT 1",
                (email_or_phone, reset_token)
            )
            token_record = cur.fetchone()
            
            if not token_record:
                print(f"DEBUG: Invalid or missing reset token for {email_or_phone}")
                return jsonify({"error": "Unauthorized. Invalid reset token."}), 401
                
            if token_record['expires_at'] < datetime.now():
                print(f"DEBUG: Reset token expired for {email_or_phone}")
                return jsonify({"error": "Reset token has expired."}), 401
                
            if not validate_password_complexity(new_password):
                return jsonify({"error": "Password must be at least 8 characters long and contain uppercase, lowercase, number, and special character."}), 400
                
            pw_hash = generate_password_hash(new_password)
            
            cur.execute(
                "UPDATE users SET password_hash = %s WHERE email_or_phone = %s",
                (pw_hash, email_or_phone)
            )
            affected = cur.rowcount
            
            # Fetch user details for session
            cur.execute("SELECT * FROM users WHERE email_or_phone = %s", (email_or_phone,))
            user = cur.fetchone()
            
            # Cleanup token
            cur.execute("DELETE FROM otp_codes WHERE email_or_phone = %s AND context = 'reset_token'", (email_or_phone,))
            conn.commit()
            print(f"DEBUG: Password updated for {email_or_phone}, affected rows: {affected}")

            if user:
                # ── Auto-login: Store user info in session ──────────────────────
                session["user_id"]         = user["id"]
                session["email_or_phone"]  = user["email_or_phone"]
                session["phone"]           = user.get("phone", "")
                session["full_name"]       = user["full_name"]
                session["farm_name"]       = user["farm_name"]
                session.permanent          = True
                
                return jsonify({
                    "message": "Password reset and logged in successfully.",
                    "user": {
                        "id":             user["id"],
                        "full_name":      user["full_name"],
                        "email_or_phone": user["email_or_phone"],
                        "phone":          user.get("phone", ""),
                        "farm_name":      user["farm_name"],
                    }
                }), 200
            
    finally:
        conn.close()
        
    return jsonify({"message": "Password reset successfully. Please login."}), 200

@auth_bp.route("/resend-otp", methods=["POST"])
def resend_otp():
    data = request.get_json()
    email_or_phone = data.get("email_or_phone", data.get("emailOrPhone", "")).strip()
    context = data.get("context", "").strip() # 'registration' or 'forgot_password'
    
    if not email_or_phone or context not in ['registration', 'forgot_password']:
        return jsonify({"error": "email_or_phone and valid context are required"}), 400
        
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Check if pending user / existing user makes sense
            if context == 'registration' and not session.get(f"reg_{email_or_phone}"):
                return jsonify({"error": "No pending registration found."}), 400
                
            if context == 'forgot_password':
                cur.execute("SELECT id FROM users WHERE email_or_phone = %s", (email_or_phone,))
                if not cur.fetchone():
                    return jsonify({"error": "User does not exist"}), 404
                    
            otp_code = generate_otp()
            expires_at = datetime.now() + timedelta(minutes=10)
            
            cur.execute("DELETE FROM otp_codes WHERE email_or_phone = %s AND context = %s", (email_or_phone, context))
            cur.execute(
                "INSERT INTO otp_codes (email_or_phone, otp_code, context, expires_at) VALUES (%s, %s, %s, %s)",
                (email_or_phone, otp_code, context, expires_at)
            )
            conn.commit()
            
            from app import mail
            success = send_otp_email(mail, email_or_phone, otp_code, context)
            if not success:
                return jsonify({"error": "Failed to send OTP email."}), 500
                
    finally:
        conn.close()
        
    return jsonify({"message": "OTP resent successfully."}), 200
