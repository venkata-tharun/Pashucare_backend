import json
from flask import Blueprint, request, jsonify, session
from models.db import get_connection

sanitation_bp = Blueprint("sanitation", __name__, url_prefix="/api/sanitation")

def require_login():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

@sanitation_bp.route("/score", methods=["GET"])
def get_score():
    err = require_login()
    if err: return err
    
    uid = session["user_id"]
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT score FROM sanitation_scores WHERE user_id=%s ORDER BY updated_at DESC LIMIT 1", (uid,))
            row = cur.fetchone()
            score = row["score"] if row else None
    finally:
        conn.close()
    return jsonify({"score": score}), 200

@sanitation_bp.route("/checklist", methods=["GET"])
def get_checklist():
    err = require_login()
    if err: return err
    
    uid = session["user_id"]
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT score, tasks_json FROM sanitation_scores WHERE user_id=%s ORDER BY updated_at DESC LIMIT 1",
                (uid,)
            )
            row = cur.fetchone()
            if row:
                row["tasks"] = json.loads(row.pop("tasks_json", "{}"))
                return jsonify(row), 200
            else:
                return jsonify({"score": 0, "tasks": {}}), 200
    finally:
        conn.close()

@sanitation_bp.route("/checklist", methods=["POST"])
def save_checklist():
    err = require_login()
    if err: return err
    
    uid = session["user_id"]
    data = request.get_json()
    score = data.get("score")
    tasks = data.get("tasks", {})
    
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO sanitation_scores (user_id, score, tasks_json) VALUES (%s, %s, %s)",
                (uid, score, json.dumps(tasks))
            )
            conn.commit()
    finally:
        conn.close()
    return jsonify({"message": "Checklist saved", "score": score}), 201

