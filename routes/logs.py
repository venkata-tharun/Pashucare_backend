from flask import Blueprint, request, jsonify, session
from models.db import get_connection

logs_bp = Blueprint("logs", __name__, url_prefix="/api/logs")


def require_login():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401


@logs_bp.route("", methods=["GET"])
def list_logs():
    err = require_login()
    if err:
        return err
    uid  = session["user_id"]
    type_filter = request.args.get("type")
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            if type_filter:
                cur.execute(
                    "SELECT * FROM farm_logs WHERE user_id=%s AND type=%s ORDER BY date DESC, id DESC",
                    (uid, type_filter)
                )
            else:
                cur.execute(
                    "SELECT * FROM farm_logs WHERE user_id=%s ORDER BY date DESC, id DESC",
                    (uid,)
                )
            rows = cur.fetchall()
            for r in rows:
                if r.get("date"):
                    r["date"] = str(r["date"])
                r["animalId"] = r.pop("animal_id", None)
    finally:
        conn.close()
    return jsonify(rows), 200


@logs_bp.route("", methods=["POST"])
def add_log():
    err = require_login()
    if err:
        return err
    uid  = session["user_id"]
    data = request.get_json()

    log_type    = data.get("type", "").strip()
    date        = data.get("date", "").strip()
    description = data.get("description", "").strip()
    animal_id   = data.get("animalId", data.get("animal_id", None))

    if not log_type or not date or not description:
        return jsonify({"error": "type, date and description are required"}), 400

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO farm_logs (user_id, type, date, description, animal_id) VALUES (%s,%s,%s,%s,%s)",
                (uid, log_type, date, description, animal_id)
            )
            conn.commit()
            eid = cur.lastrowid
    finally:
        conn.close()
    return jsonify({"id": eid, "message": "Log added"}), 201


@logs_bp.route("/<int:log_id>", methods=["PUT"])
def update_log(log_id):
    err = require_login()
    if err:
        return err
    uid  = session["user_id"]
    data = request.get_json()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE farm_logs SET type=%s, date=%s, description=%s, animal_id=%s WHERE id=%s AND user_id=%s",
                (
                    data.get("type"),
                    data.get("date"),
                    data.get("description"),
                    data.get("animalId", data.get("animal_id", None)),
                    log_id,
                    uid
                )
            )
            conn.commit()
    finally:
        conn.close()
    return jsonify({"message": "Updated"}), 200


@logs_bp.route("/<int:log_id>", methods=["DELETE"])
def delete_log(log_id):
    err = require_login()
    if err:
        return err
    uid = session["user_id"]
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM farm_logs WHERE id=%s AND user_id=%s", (log_id, uid))
            conn.commit()
    finally:
        conn.close()
    return jsonify({"message": "Deleted"}), 200
