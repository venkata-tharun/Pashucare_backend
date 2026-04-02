from flask import Blueprint, request, jsonify, session
from models.db import get_connection

transactions_bp = Blueprint("transactions", __name__, url_prefix="/api/transactions")


def require_login():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401


@transactions_bp.route("", methods=["GET"])
def list_transactions():
    err = require_login()
    if err:
        return err
    uid      = session["user_id"]
    category = request.args.get("category")   # optional filter: Income | Expense
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            if category:
                cur.execute(
                    "SELECT * FROM transactions WHERE user_id=%s AND category=%s ORDER BY date DESC",
                    (uid, category)
                )
            else:
                cur.execute("SELECT * FROM transactions WHERE user_id=%s ORDER BY date DESC", (uid,))
            rows = cur.fetchall()
            for r in rows:
                if r.get("date"):
                    r["date"] = str(r["date"])
                r["receiptNo"] = r.pop("receipt_no", "")
    finally:
        conn.close()
    return jsonify(rows), 200


@transactions_bp.route("", methods=["POST"])
def add_transaction():
    err = require_login()
    if err:
        return err
    uid  = session["user_id"]
    data = request.get_json()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO transactions (user_id, category, date, type, amount, receipt_no, note)
                   VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                (
                    uid,
                    data.get("category"),
                    data.get("date"),
                    data.get("type"),
                    data.get("amount"),
                    data.get("receiptNo", data.get("receipt_no", "")),
                    data.get("note", ""),
                )
            )
            conn.commit()
            eid = cur.lastrowid
    finally:
        conn.close()
    return jsonify({"id": eid, "message": "Transaction added"}), 201


@transactions_bp.route("/<int:tx_id>", methods=["DELETE"])
def delete_transaction(tx_id):
    err = require_login()
    if err:
        return err
    uid = session["user_id"]
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM transactions WHERE id=%s AND user_id=%s", (tx_id, uid))
            conn.commit()
    finally:
        conn.close()
    return jsonify({"message": "Deleted"}), 200
