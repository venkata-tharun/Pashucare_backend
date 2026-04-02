from flask import Blueprint, request, jsonify, session
from models.db import get_connection

animals_bp = Blueprint("animals", __name__, url_prefix="/api/animals")


def require_login():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401


@animals_bp.route("", methods=["GET"])
def list_animals():
    err = require_login()
    if err:
        return err
    uid = session["user_id"]
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM animals WHERE user_id = %s ORDER BY id DESC", (uid,))
            rows = cur.fetchall()
            # No changes needed for column names if they match model, 
            # but ensure case consistency if necessary.
    finally:
        conn.close()
    return jsonify(rows), 200


@animals_bp.route("", methods=["POST"])
def add_animal():
    err = require_login()
    if err:
        return err
    uid = session["user_id"]
    data = request.get_json()
    name   = data.get("name", "").strip()
    tag    = data.get("tag", "").strip()
    breed  = data.get("breed", "").strip()
    age    = data.get("age", "").strip()
    weight = data.get("weight", "").strip()
    gender = data.get("gender", "Female").strip()
    status = data.get("status", "Healthy")

    if not name or not tag:
        return jsonify({"error": "name and tag are required"}), 400

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO animals (user_id, name, tag, breed, age, weight, gender, status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                (uid, name, tag, breed, age, weight, gender, status)
            )
            conn.commit()
            eid = cur.lastrowid
    finally:
        conn.close()
    return jsonify({"id": eid, "message": "Animal added"}), 201


@animals_bp.route("/<int:animal_id>", methods=["PUT"])
def update_animal(animal_id):
    err = require_login()
    if err:
        return err
    uid = session["user_id"]
    data = request.get_json()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE animals SET name=%s, tag=%s, breed=%s, age=%s, weight=%s, gender=%s, status=%s WHERE id=%s AND user_id=%s",
                (
                    data.get("name"),
                    data.get("tag"),
                    data.get("breed"),
                    data.get("age"),
                    data.get("weight"),
                    data.get("gender"),
                    data.get("status"),
                    animal_id,
                    uid
                )
            )
            conn.commit()
    finally:
        conn.close()
    return jsonify({"message": "Updated"}), 200


@animals_bp.route("/<int:animal_id>", methods=["DELETE"])
def delete_animal(animal_id):
    err = require_login()
    if err:
        return err
    uid = session["user_id"]
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM animals WHERE id=%s AND user_id=%s", (animal_id, uid))
            conn.commit()
    finally:
        conn.close()
    return jsonify({"message": "Deleted"}), 200


# ── Health Records ────────────────────────────────────────────────
@animals_bp.route("/<int:animal_id>/health-records", methods=["GET"])
def list_health_records(animal_id):
    err = require_login()
    if err:
        return err
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM health_records WHERE animal_id=%s ORDER BY date DESC", (animal_id,))
            rows = cur.fetchall()
            for r in rows:
                if r.get("date"): r["date"] = str(r["date"])
    finally:
        conn.close()
    return jsonify(rows), 200


@animals_bp.route("/<int:animal_id>/health-records", methods=["POST"])
def add_health_record(animal_id):
    err = require_login()
    if err:
        return err
    data = request.get_json()
    date      = data.get("date")
    title     = data.get("title")
    doctor    = data.get("doctor")
    treatment = data.get("treatment")
    cost      = data.get("cost")
    status    = data.get("status", "Completed")

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO health_records (animal_id, date, title, doctor, treatment, cost, status) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                (animal_id, date, title, doctor, treatment, cost, status)
            )
            conn.commit()
            eid = cur.lastrowid
    finally:
        conn.close()
    return jsonify({"id": eid, "message": "Health record added"}), 201
@animals_bp.route("/<int:animal_id>/health-records/<int:record_id>", methods=["PUT"])
def update_health_record(animal_id, record_id):
    err = require_login()
    if err:
        return err
    data = request.get_json()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """UPDATE health_records SET date=%s, title=%s, doctor=%s, treatment=%s, cost=%s, status=%s 
                   WHERE id=%s AND animal_id=%s""",
                (
                    data.get("date"),
                    data.get("title"),
                    data.get("doctor"),
                    data.get("treatment"),
                    data.get("cost"),
                    data.get("status", "Completed"),
                    record_id,
                    animal_id
                )
            )
            conn.commit()
    finally:
        conn.close()
    return jsonify({"message": "Health record updated"}), 200


@animals_bp.route("/<int:animal_id>/health-records/<int:record_id>", methods=["DELETE"])
def delete_health_record(animal_id, record_id):
    err = require_login()
    if err:
        return err
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM health_records WHERE id=%s AND animal_id=%s", (record_id, animal_id))
            conn.commit()
    finally:
        conn.close()
    return jsonify({"message": "Health record deleted"}), 200


# ── Vaccination Records ──────────────────────────────────────────
@animals_bp.route("/<int:animal_id>/vaccinations", methods=["GET"])
def list_vaccinations(animal_id):
    err = require_login()
    if err:
        return err
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM vaccinations WHERE animal_id=%s ORDER BY date_given DESC", (animal_id,))
            rows = cur.fetchall()
            for r in rows:
                for k in ("date_given", "next_due_date"):
                    if r.get(k): r[k] = str(r[k])
                r["vaccineName"] = r.pop("vaccine_name", "")
                r["dateGiven"]   = r.pop("date_given", "")
                r["nextDueDate"] = r.pop("next_due_date", "")
                r["batchNumber"] = r.pop("batch_number", "")
    finally:
        conn.close()
    return jsonify(rows), 200


@animals_bp.route("/<int:animal_id>/vaccinations", methods=["POST"])
def add_vaccination(animal_id):
    err = require_login()
    if err:
        return err
    data = request.get_json()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO vaccinations (animal_id, vaccine_name, date_given, next_due_date, batch_number)
                   VALUES (%s,%s,%s,%s,%s)""",
                (
                    animal_id,
                    data.get("vaccineName"),
                    data.get("dateGiven"),
                    data.get("nextDueDate"),
                    data.get("batchNumber", "")
                )
            )
            conn.commit()
            eid = cur.lastrowid
    finally:
        conn.close()
    return jsonify({"id": eid, "message": "Vaccination recorded"}), 201
@animals_bp.route("/<int:animal_id>/vaccinations/<int:vaccination_id>", methods=["PUT"])
def update_vaccination(animal_id, vaccination_id):
    err = require_login()
    if err:
        return err
    data = request.get_json()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """UPDATE vaccinations SET vaccine_name=%s, date_given=%s, next_due_date=%s, batch_number=%s 
                   WHERE id=%s AND animal_id=%s""",
                (
                    data.get("vaccineName"),
                    data.get("dateGiven"),
                    data.get("nextDueDate"),
                    data.get("batchNumber", ""),
                    vaccination_id,
                    animal_id
                )
            )
            conn.commit()
    finally:
        conn.close()
    return jsonify({"message": "Vaccination updated"}), 200


@animals_bp.route("/<int:animal_id>/vaccinations/<int:vaccination_id>", methods=["DELETE"])
def delete_vaccination(animal_id, vaccination_id):
    err = require_login()
    if err:
        return err
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM vaccinations WHERE id=%s AND animal_id=%s", (vaccination_id, animal_id))
            conn.commit()
    finally:
        conn.close()
    return jsonify({"message": "Vaccination deleted"}), 200
