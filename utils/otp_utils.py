import random
import string
import re
from flask_mail import Message
from datetime import datetime, timedelta

def generate_otp(length=6):
    return ''.join(random.choices(string.digits, k=length))

def validate_password_complexity(password: str) -> bool:
    """
    Validates if password meets complexity requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    - At least one special character
    """
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    return True

import threading

def send_otp_email(mail, recipient, otp_code, context):
    def send_async_email(app, msg):
        with app.app_context():
            try:
                mail.send(msg)
                print(f"Email successfully sent to {recipient}")
            except Exception as e:
                print(f"Error sending async email to {recipient}: {e}")
                print(f"DEBUG FALLBACK: OTP for {recipient} is {otp_code} (context: {context})")

    try:
        if context == 'registration':
            subject = "PashuCare - Verification Code"
            body = f"Hello,\n\nThank you for choosing PashuCare! Your verification code for registration is: {otp_code}\n\nThis code will expire in 10 minutes.\n\nBest regards,\nPashuCare Team"
        elif context == 'forgot_password':
            subject = "Your PashuCare Password Reset OTP"
            body = f"You requested a password reset.\n\nYour OTP is: {otp_code}\n\nThis OTP will expire in 10 minutes. If you did not request this, please ignore this email."
        else:
            subject = "Your PashuCare OTP"
            body = f"Your OTP is: {otp_code}\n\nThis OTP will expire in 10 minutes."

        msg = Message(subject, recipients=[recipient], body=body)
        print(f"DEBUG: Preparing to send {context} email to {recipient}")
        print(f"DEBUG: Generated OTP for {recipient}: {otp_code} (context: {context})")
        
        # We need the real application object to send from a background thread
        from flask import current_app
        app = current_app._get_current_object()
        
        threading.Thread(target=send_async_email, args=(app, msg)).start()
        print(f"DEBUG: Async thread started for {recipient}")
        
        return True
    except Exception as e:
        print(f"Error initiating email thread: {e}")
        # Always return True in dev to keep the flow moving
        print(f"DEBUG: OTP generated for {recipient}: {otp_code} (context: {context})")
        return True
