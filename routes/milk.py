from flask import Blueprint, request, jsonify, session
from models.db import get_connection

milk_bp = Blueprint("milk", __name__, url_prefix="/api/milk")


def _user_has_animals(uid, cur):
    """Return True if the user owns at least one animal."""
    cur.execute("SELECT id FROM animals WHERE user_id = %s LIMIT 1", (uid,))
    return cur.fetchone() is not None


def _validate_cattle_tag(uid, tag, cur):
    """Return True if the given tag belongs to one of the user's animals."""
    cur.execute("SELECT id FROM animals WHERE user_id = %s AND tag = %s LIMIT 1", (uid, tag))
    return cur.fetchone() is not None


def require_login():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401


@milk_bp.route("", methods=["GET"])
def list_milk():
    err = require_login()
    if err:
        return err
    uid = session["user_id"]
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM milk_entries WHERE user_id=%s ORDER BY date DESC", (uid,))
            rows = cur.fetchall()
            for r in rows:
                if r.get("date"):
                    r["date"] = str(r["date"])
                # Map snake_case → camelCase and cast numerics to float
                r["milkType"]       = r.pop("milk_type", "Bulk Milk")
                r["cattleTag"]      = r.pop("cattle_tag", "")
                r["totalUsed"]      = float(r.pop("total_used", 0) or 0)
                r["cowMilkedNumber"] = int(r.pop("cow_milked_number", 0) or 0)
                r["am"]   = float(r.get("am", 0) or 0)
                r["noon"] = float(r.get("noon", 0) or 0)
                r["pm"]   = float(r.get("pm", 0) or 0)
    finally:
        conn.close()
    return jsonify(rows), 200


@milk_bp.route("/animal-tags", methods=["GET"])
def get_animal_tags():
    """Return list of {id, name, tag} for the current user's animals."""
    err = require_login()
    if err:
        return err
    uid = session["user_id"]
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, name, tag FROM animals WHERE user_id = %s ORDER BY name ASC",
                (uid,)
            )
            rows = cur.fetchall()
    finally:
        conn.close()
    return jsonify(rows), 200


@milk_bp.route("", methods=["POST"])
def add_milk():
    err = require_login()
    if err:
        return err
    uid  = session["user_id"]
    data = request.get_json()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # ── Guard: user must have at least one animal ──────────────
            if not _user_has_animals(uid, cur):
                return jsonify({"error": "Please add at least one animal before recording milk production."}), 403

            milk_type  = data.get("milkType", data.get("milk_type", "Bulk Milk"))
            cattle_tag = data.get("cattleTag", data.get("cattle_tag", ""))

            # ── Guard: Individual Milk MUST have a cattle tag (and it cannot be "All")
            if milk_type == "Individual Milk" and (not cattle_tag or cattle_tag == "All"):
                return jsonify({"error": "Individual Milk requires a specific cattle tag."}), 400

            # ── Guard: if a specific cattle tag is provided, it must belong to the user ──
            if cattle_tag and cattle_tag != "All":
                if not _validate_cattle_tag(uid, cattle_tag, cur):
                    return jsonify({"error": f"Cattle tag '{cattle_tag}' does not belong to any of your animals."}), 400

            cur.execute(
                """INSERT INTO milk_entries
                   (user_id, milk_type, date, cattle_tag, am, noon, pm, total_used, cow_milked_number, note)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (
                    uid,
                    milk_type,
                    data.get("date"),
                    cattle_tag,
                    data.get("am", 0),
                    data.get("noon", 0),
                    data.get("pm", 0),
                    data.get("totalUsed", data.get("total_used", 0)),
                    data.get("cowMilkedNumber", data.get("cow_milked_number", 0)),
                    data.get("note", ""),
                )
            )
            conn.commit()
            eid = cur.lastrowid
    finally:
        conn.close()
    return jsonify({"id": eid, "message": "Milk entry added"}), 201


@milk_bp.route("/<int:entry_id>", methods=["PUT"])
def update_milk(entry_id):
    err = require_login()
    if err:
        return err
    uid  = session["user_id"]
    data = request.get_json()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            milk_type  = data.get("milkType", data.get("milk_type", "Bulk Milk"))
            cattle_tag = data.get("cattleTag", data.get("cattle_tag", ""))

            if milk_type == "Individual Milk" and (not cattle_tag or cattle_tag == "All"):
                return jsonify({"error": "Individual Milk requires a specific cattle tag."}), 400

            if cattle_tag and cattle_tag != "All":
                if not _validate_cattle_tag(uid, cattle_tag, cur):
                    return jsonify({"error": f"Cattle tag '{cattle_tag}' does not belong to any of your animals."}), 400

            cur.execute(
                """UPDATE milk_entries SET milk_type=%s, date=%s, cattle_tag=%s,
                   am=%s, noon=%s, pm=%s, total_used=%s, cow_milked_number=%s, note=%s
                   WHERE id=%s AND user_id=%s""",
                (
                    milk_type, 
                    data.get("date"), 
                    cattle_tag,
                    data.get("am"), data.get("noon"), data.get("pm"),
                    data.get("totalUsed", data.get("total_used")), 
                    data.get("cowMilkedNumber", data.get("cow_milked_number")), 
                    data.get("note"),
                    entry_id, uid
                )
            )
            conn.commit()
    finally:
        conn.close()
    return jsonify({"message": "Updated"}), 200


@milk_bp.route("/<int:entry_id>", methods=["DELETE"])
def delete_milk(entry_id):
    err = require_login()
    if err:
        return err
    uid = session["user_id"]
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM milk_entries WHERE id=%s AND user_id=%s", (entry_id, uid))
            conn.commit()
    finally:
        conn.close()
    return jsonify({"message": "Deleted"}), 200
