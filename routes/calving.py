from flask import Blueprint, request, jsonify, session
from models.db import get_connection

calving_bp = Blueprint("calving", __name__, url_prefix="/api/calving")


def require_login():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401


@calving_bp.route("", methods=["GET"])
def list_calving():
    err = require_login()
    if err:
        return err
    uid = session["user_id"]
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM calving_records WHERE user_id=%s ORDER BY breeding_date DESC", (uid,))
            rows = cur.fetchall()
            for r in rows:
                if r.get("breeding_date"):
                    r["breeding_date"] = str(r["breeding_date"])
                # Map snake_case to camelCase
                r["animalName"] = r.pop("animal_name", "")
                r["breedingDate"] = r.pop("breeding_date", "")
    finally:
        conn.close()
    return jsonify(rows), 200


@calving_bp.route("", methods=["POST"])
def add_calving():
    err = require_login()
    if err:
        return err
    uid  = session["user_id"]
    data = request.get_json()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO calving_records (user_id, animal_name, breeding_date) VALUES (%s,%s,%s)",
                (uid, data.get("animalName", data.get("animal_name")), data.get("breedingDate", data.get("breeding_date")))
            )
            conn.commit()
            eid = cur.lastrowid
    finally:
        conn.close()
    return jsonify({"id": eid, "message": "Calving record added"}), 201


@calving_bp.route("/<int:record_id>", methods=["PUT"])
def update_calving(record_id):
    err = require_login()
    if err:
        return err
    uid  = session["user_id"]
    data = request.get_json()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE calving_records SET animal_name=%s, breeding_date=%s WHERE id=%s AND user_id=%s",
                (data.get("animalName", data.get("animal_name")), data.get("breedingDate", data.get("breeding_date")), record_id, uid)
            )
            conn.commit()
    finally:
        conn.close()
    return jsonify({"message": "Updated"}), 200


@calving_bp.route("/<int:record_id>", methods=["DELETE"])
def delete_calving(record_id):
    err = require_login()
    if err:
        return err
    uid = session["user_id"]
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM calving_records WHERE id=%s AND user_id=%s", (record_id, uid))
            conn.commit()
    finally:
        conn.close()
    return jsonify({"message": "Deleted"}), 200
