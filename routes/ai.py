from flask import Blueprint, request, jsonify, session, current_app
from models.db import get_connection
import os
import uuid
import json

ai_bp = Blueprint("ai", __name__, url_prefix="/api/ai")

def require_login():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

@ai_bp.route("/predictions", methods=["GET"])
def list_predictions():
    err = require_login()
    if err: return err
    
    uid = session["user_id"]
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM ai_predictions WHERE user_id=%s ORDER BY created_at DESC", (uid,))
            rows = cur.fetchall()
            for r in rows:
                if r.get("created_at"):
                    r["created_at"] = str(r["created_at"])
                if r.get("symptoms_json"):
                    try:
                        r["symptoms"] = json.loads(r["symptoms_json"])
                    except:
                        r["symptoms"] = []
                if r.get("precautions_json"):
                    try:
                        r["precautions"] = json.loads(r["precautions_json"])
                    except:
                        r["precautions"] = []
    finally:
        conn.close()
    return jsonify(rows), 200

@ai_bp.route("/predictions", methods=["POST"])
def save_prediction():
    err = require_login()
    if err: return err
    
    uid = session["user_id"]
    
    # Check if image is in request files
    image_file = request.files.get('image')
    data = request.form
    
    # If not in files/form, check json (though images won't be in json easily)
    if not image_file:
        return jsonify({"error": "Image is required"}), 400

    # Save image
    filename = f"{uuid.uuid4()}.jpg"
    upload_path = os.path.join(current_app.root_path, 'uploads', 'ai_images', filename)
    os.makedirs(os.path.dirname(upload_path), exist_ok=True)
    image_file.save(upload_path)
    
    relative_path = f"/uploads/ai_images/{filename}"

    disease_name = data.get("diseaseName", "Unknown")
    confidence = data.get("confidence", "0%")
    status = data.get("status", "Healthy")
    symptoms = data.get("symptoms", "[]") # Expecting JSON string
    precautions = data.get("precautions", "[]") # Expecting JSON string
    animal_id = data.get("animal_id")

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO ai_predictions 
                   (user_id, animal_id, disease_name, confidence, status, symptoms_json, precautions_json, image_path)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (uid, animal_id, disease_name, confidence, status, symptoms, precautions, relative_path)
            )
            conn.commit()
            pid = cur.lastrowid
    finally:
        conn.close()
        
    return jsonify({"id": pid, "imagePath": relative_path, "message": "Prediction saved successfully"}), 201
