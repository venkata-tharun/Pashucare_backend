from flask import Blueprint, request, jsonify, session
from models.db import get_connection

visitors_bp = Blueprint("visitors", __name__, url_prefix="/api/visitors")


def require_login():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401


def fmt_dt(val):
    if not val: return None
    # Convert '2026-03-11T09:08:15Z' to '2026-03-11 09:08:15'
    return val.replace("T", " ").replace("Z", "").split(".")[0]


@visitors_bp.route("", methods=["GET"])
def list_visitors():
    err = require_login()
    if err:
        return err
    uid = session["user_id"]
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM visitors WHERE user_id=%s ORDER BY date DESC", (uid,))
            rows = cur.fetchall()
            for r in rows:
                for k in ("date", "entry_time", "outgoing_time"):
                    if r.get(k):
                        r[k] = str(r[k])
                # Map snake_case to camelCase
                r["entryTime"]    = r.pop("entry_time", "")
                r["outgoingTime"] = r.pop("outgoing_time", "")
                r["personToMeet"] = r.pop("person_to_meet", "")
                r["vehicleNumber"] = r.pop("vehicle_number", "")
    finally:
        conn.close()
    return jsonify(rows), 200


@visitors_bp.route("", methods=["POST"])
def add_visitor():
    err = require_login()
    if err:
        return err
    uid  = session["user_id"]
    data = request.get_json()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO visitors
                   (user_id, name, phone, purpose, date, entry_time, outgoing_time,
                    person_to_meet, vehicle_number, notes, status)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (
                    uid,
                    data.get("name"),
                    data.get("phone"),
                    data.get("purpose", ""),
                    data.get("date"),
                    fmt_dt(data.get("entryTime", data.get("entry_time"))),
                    fmt_dt(data.get("outgoingTime", data.get("outgoing_time"))),
                    data.get("personToMeet", data.get("person_to_meet", "")),
                    data.get("vehicleNumber", data.get("vehicle_number", "")),
                    data.get("notes", ""),
                    data.get("status", "Pending"),
                )
            )
            conn.commit()
            eid = cur.lastrowid
    finally:
        conn.close()
    return jsonify({"id": eid, "message": "Visitor added"}), 201


@visitors_bp.route("/<int:visitor_id>", methods=["PUT"])
def update_visitor(visitor_id):
    err = require_login()
    if err:
        return err
    uid  = session["user_id"]
    data = request.get_json()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """UPDATE visitors SET name=%s, phone=%s, purpose=%s, date=%s,
                   entry_time=%s, outgoing_time=%s, person_to_meet=%s,
                   vehicle_number=%s, notes=%s, status=%s
                   WHERE id=%s AND user_id=%s""",
                (
                    data.get("name"), 
                    data.get("phone"), 
                    data.get("purpose"),
                    data.get("date"), 
                    fmt_dt(data.get("entryTime", data.get("entry_time"))),
                    fmt_dt(data.get("outgoingTime", data.get("outgoing_time"))),
                    data.get("personToMeet", data.get("person_to_meet")),
                    data.get("vehicleNumber", data.get("vehicle_number")),
                    data.get("notes"), 
                    data.get("status"),
                    visitor_id, uid
                )
            )
            conn.commit()
    finally:
        conn.close()
    return jsonify({"message": "Visitor updated"}), 200


@visitors_bp.route("/<int:visitor_id>", methods=["DELETE"])
def delete_visitor(visitor_id):
    err = require_login()
    if err:
        return err
    uid = session["user_id"]
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM visitors WHERE id=%s AND user_id=%s", (visitor_id, uid))
            conn.commit()
    finally:
        conn.close()
    return jsonify({"message": "Deleted"}), 200
