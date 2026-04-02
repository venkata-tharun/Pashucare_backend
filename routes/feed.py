from flask import Blueprint, request, jsonify, session
from models.db import get_connection

feed_bp = Blueprint("feed", __name__, url_prefix="/api/feed")


def require_login():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401


@feed_bp.route("/stock", methods=["GET"])
def list_stock():
    err = require_login()
    if err:
        return err
    uid = session["user_id"]
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM feed_stock WHERE user_id=%s ORDER BY name", (uid,))
            rows = cur.fetchall()
            for r in rows:
                if "quantity" in r:
                    r["quantity"] = float(r["quantity"])
    finally:
        conn.close()
    return jsonify(rows), 200


@feed_bp.route("/stock", methods=["POST"])
def add_or_update_stock():
    """Add stock to an existing item or create it."""
    err = require_login()
    if err:
        print(f"DEBUG STOCK: require_login failed")
        return err
    uid  = session["user_id"]
    data = request.get_json()
    name     = data.get("name", data.get("itemName", "")).strip()
    qty_add  = float(data.get("amountAdded", data.get("amount_added", data.get("quantity", 0))))
    
    print(f"DEBUG STOCK: User {uid} attempting to add {qty_add} to '{name}'")

    if not name:
        print(f"DEBUG STOCK: Item name is empty")
        return jsonify({"error": "name required"}), 400

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Check if item exists for this user
            cur.execute("SELECT id, quantity FROM feed_stock WHERE user_id=%s AND name=%s", (uid, name))
            row = cur.fetchone()
            if row:
                new_qty = float(row["quantity"]) + qty_add
                status  = "Good" if new_qty >= 1000 else ("Medium" if new_qty >= 200 else "Low")
                cur.execute(
                    "UPDATE feed_stock SET quantity=%s, status=%s WHERE id=%s",
                    (new_qty, status, row["id"])
                )
                print(f"DEBUG STOCK: Updated existing item {row['id']} to {new_qty}")
            else:
                status = "Good" if qty_add >= 1000 else ("Medium" if qty_add >= 200 else "Low")
                cur.execute(
                    "INSERT INTO feed_stock (user_id, name, quantity, status) VALUES (%s,%s,%s,%s)",
                    (uid, name, qty_add, status)
                )
                print(f"DEBUG STOCK: Inserted new item '{name}' with {qty_add}")

            # Log activity
            cur.execute(
                "INSERT INTO feed_activity (user_id, item_name, amount_added) VALUES (%s,%s,%s)",
                (uid, name, qty_add)
            )
            affected = cur.rowcount
            conn.commit()
            print(f"DEBUG STOCK: Transaction committed. Affected rows: {affected}")
    except Exception as e:
        print(f"DEBUG STOCK ERROR: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()
    return jsonify({"message": "Stock updated"}), 200


@feed_bp.route("/activity", methods=["GET"])
def list_activity():
    err = require_login()
    if err:
        return err
    uid = session["user_id"]
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM feed_activity WHERE user_id=%s ORDER BY date DESC LIMIT 50", (uid,))
            rows = cur.fetchall()
            for r in rows:
                if r.get("date"):
                    r["date"] = str(r["date"])
                if "amount_added" in r:
                    r["amountAdded"] = float(r.pop("amount_added"))
                else:
                    r["amountAdded"] = float(r.get("amountAdded", 0))
                r["itemName"] = r.pop("item_name", r.get("itemName", ""))
    finally:
        conn.close()
    return jsonify(rows), 200


@feed_bp.route("/entries", methods=["POST"])
def add_feed_entry():
    """Record a feeding event."""
    err = require_login()
    if err:
        return err
    uid  = session["user_id"]
    data = request.get_json()
    date      = data.get("date", "").strip()
    feed_time = data.get("feedTime", data.get("feed_time", "")).strip()
    feed_type = data.get("feedType", data.get("feed_type", "")).strip()
    target_group = data.get("target_group", data.get("targetGroup", "")).strip()
    quantity  = float(data.get("quantity", data.get("amount", 0)))
    notes     = data.get("notes", "")

    if not date:
        return jsonify({"error": "date required"}), 400

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # 1. Check if we have enough stock for this feed_type
            cur.execute("SELECT id, quantity FROM feed_stock WHERE user_id=%s AND name=%s", (uid, feed_type))
            row = cur.fetchone()
            
            if not row:
                return jsonify({"error": f"No stock available for {feed_type}"}), 400
                
            current_qty = float(row["quantity"])
            if current_qty < quantity:
                return jsonify({"error": f"Insufficient stock. Only {current_qty} kg available."}), 400
                
            # 2. Deduct from stock and update status
            new_qty = current_qty - quantity
            status = "Good" if new_qty >= 1000 else ("Medium" if new_qty >= 200 else "Low")
            cur.execute(
                "UPDATE feed_stock SET quantity=%s, status=%s WHERE id=%s",
                (new_qty, status, row["id"])
            )
            
            # 3. Create the feed entry
            cur.execute(
                "INSERT INTO feed_entries (user_id, date, feed_time, feed_type, target_group, quantity, notes) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                (uid, date, feed_time, feed_type, target_group, quantity, notes)
            )
            eid = cur.lastrowid
            conn.commit()
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()
    return jsonify({"id": eid, "message": "Feeding entry saved and stock updated"}), 201


@feed_bp.route("/entries/<int:eid>", methods=["PUT"])
def update_feed_entry(eid):
    err = require_login()
    if err: return err
    uid = session["user_id"]
    data = request.get_json()
    
    updates = []
    params = []
    
    fields = {
        "date": "date",
        "feedTime": "feed_time",
        "feed_time": "feed_time",
        "feedType": "feed_type",
        "feed_type": "feed_type",
        "target_group": "target_group",
        "targetGroup": "target_group",
        "quantity": "quantity",
        "amount": "quantity",
        "notes": "notes"
    }
    
    for req_key, db_col in fields.items():
        if req_key in data:
            updates.append(f"{db_col}=%s")
            params.append(data[req_key])
            
    if not updates:
        return jsonify({"message": "No changes"}), 200
        
    params.append(eid)
    params.append(uid)
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # 1. Fetch original entry to handle stock adjustments if needed
            cur.execute("SELECT feed_type, quantity FROM feed_entries WHERE id=%s AND user_id=%s", (eid, uid))
            old_entry = cur.fetchone()
            
            if not old_entry:
                return jsonify({"error": "Entry not found"}), 404
                
            old_feed_type = old_entry["feed_type"]
            old_quantity = float(old_entry["quantity"])
            
            # Extract new values, defaulting to old if not updated
            new_feed_type = data.get("feedType", data.get("feed_type", old_feed_type))
            new_quantity = float(data.get("quantity", data.get("amount", old_quantity)))
            
            # Stock adjustment logic if quantity or feed_type changed
            stock_changed = False
            if old_feed_type != new_feed_type or old_quantity != new_quantity:
                stock_changed = True
                
                # Check sufficient stock for new demand
                cur.execute("SELECT id, quantity FROM feed_stock WHERE user_id=%s AND name=%s", (uid, new_feed_type))
                new_stock_row = cur.fetchone()
                
                if not new_stock_row:
                    return jsonify({"error": f"No stock available for {new_feed_type}"}), 400
                    
                available_for_new = float(new_stock_row["quantity"])
                if old_feed_type == new_feed_type:
                    # Same feed type: they already "own" the old quantity
                    available_for_new += old_quantity
                    
                if available_for_new < new_quantity:
                    return jsonify({"error": f"Insufficient stock. Need {new_quantity} kg, but only {available_for_new} kg available for {new_feed_type}."}), 400
                
                # RESTORE old stock
                cur.execute("SELECT id, quantity FROM feed_stock WHERE user_id=%s AND name=%s", (uid, old_feed_type))
                old_stock_row = cur.fetchone()
                if old_stock_row:
                    restored_qty = float(old_stock_row["quantity"]) + old_quantity
                    status = "Good" if restored_qty >= 1000 else ("Medium" if restored_qty >= 200 else "Low")
                    cur.execute("UPDATE feed_stock SET quantity=%s, status=%s WHERE id=%s", (restored_qty, status, old_stock_row["id"]))
                else:
                    status = "Good" if old_quantity >= 1000 else ("Medium" if old_quantity >= 200 else "Low")
                    cur.execute("INSERT INTO feed_stock (user_id, name, quantity, status) VALUES (%s,%s,%s,%s)", (uid, old_feed_type, old_quantity, status))
                
                # RE-FETCH new stock row (in case old == new, the row was just updated above)
                cur.execute("SELECT id, quantity FROM feed_stock WHERE user_id=%s AND name=%s", (uid, new_feed_type))
                updated_new_stock_row = cur.fetchone()
                sub_qty = float(updated_new_stock_row["quantity"]) - new_quantity
                new_status = "Good" if sub_qty >= 1000 else ("Medium" if sub_qty >= 200 else "Low")
                cur.execute("UPDATE feed_stock SET quantity=%s, status=%s WHERE id=%s", (sub_qty, new_status, updated_new_stock_row["id"]))

            # Finally, update the feed entry itself
            cur.execute(
                f"UPDATE feed_entries SET {', '.join(updates)} WHERE id=%s AND user_id=%s",
                tuple(params)
            )
            conn.commit()
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()
        
    msg = "Entry updated and stock adjusted" if stock_changed else "Entry updated"
    return jsonify({"message": msg}), 200


@feed_bp.route("/entries/<int:eid>", methods=["DELETE"])
def delete_feed_entry(eid):
    err = require_login()
    if err: return err
    uid = session["user_id"]
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # 1. Get the entry to know how much to restore
            cur.execute("SELECT feed_type, quantity FROM feed_entries WHERE id=%s AND user_id=%s", (eid, uid))
            entry = cur.fetchone()
            
            if entry:
                feed_type = entry["feed_type"]
                restoring_qty = float(entry["quantity"])
                
                # 2. Delete the entry
                cur.execute("DELETE FROM feed_entries WHERE id=%s AND user_id=%s", (eid, uid))
                
                # 3. Restore stock
                cur.execute("SELECT id, quantity FROM feed_stock WHERE user_id=%s AND name=%s", (uid, feed_type))
                stock_row = cur.fetchone()
                if stock_row:
                    new_qty = float(stock_row["quantity"]) + restoring_qty
                    status = "Good" if new_qty >= 1000 else ("Medium" if new_qty >= 200 else "Low")
                    cur.execute(
                        "UPDATE feed_stock SET quantity=%s, status=%s WHERE id=%s",
                        (new_qty, status, stock_row["id"])
                    )
                else:
                    # Technically shouldn't happen, but just recreate it if deleted
                    status = "Good" if restoring_qty >= 1000 else ("Medium" if restoring_qty >= 200 else "Low")
                    cur.execute(
                        "INSERT INTO feed_stock (user_id, name, quantity, status) VALUES (%s,%s,%s,%s)",
                        (uid, feed_type, restoring_qty, status)
                    )
                    
                conn.commit()
            else:
                return jsonify({"error": "Entry not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()
    return jsonify({"message": "Entry deleted and stock restored"}), 200


@feed_bp.route("/entries", methods=["GET"])
def list_feed_entries():
    err = require_login()
    if err:
        return err
    uid = session["user_id"]
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM feed_entries WHERE user_id=%s ORDER BY date DESC, id DESC LIMIT 50",
                (uid,)
            )
            rows = cur.fetchall()
            for r in rows:
                if r.get("date"):
                    r["date"] = str(r["date"])
                if "quantity" in r:
                    r["quantity"] = float(r["quantity"])
                r["targetGroup"] = r.pop("target_group", "")
                r["feedTime"] = r.pop("feed_time", "")
                r["feedType"] = r.pop("feed_type", "")
    finally:
        conn.close()
    return jsonify(rows), 200


# ─── Feeding Schedules ────────────────────────────────────────────────

@feed_bp.route("/schedules", methods=["GET"])
def list_schedules():
    err = require_login()
    if err:
        return err
    uid = session["user_id"]
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM feeding_schedules WHERE user_id=%s ORDER BY time ASC", (uid,))
            rows = cur.fetchall()
            import json
            for r in rows:
                try:
                    r["items"] = json.loads(r.pop("items_json", "[]"))
                except:
                    r["items"] = []
                r["isCompleted"] = bool(r.pop("is_completed", False))
    finally:
        conn.close()
    return jsonify(rows), 200


@feed_bp.route("/schedules", methods=["POST"])
def add_schedule():
    err = require_login()
    if err:
        return err
    uid = session["user_id"]
    data = request.get_json()
    time  = data.get("time", "").strip()
    title = data.get("title", "").strip()
    items = data.get("items", []) # List of strings
    
    if not time or not title:
        return jsonify({"error": "time and title required"}), 400

    import json
    items_json = json.dumps(items)

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO feeding_schedules (user_id, time, title, items_json) VALUES (%s, %s, %s, %s)",
                (uid, time, title, items_json)
            )
            conn.commit()
            sid = cur.lastrowid
    finally:
        conn.close()
    return jsonify({"id": sid, "message": "Schedule added"}), 201


@feed_bp.route("/schedules/<int:sid>", methods=["PUT"])
def update_schedule(sid):
    err = require_login()
    if err:
        return err
    uid = session["user_id"]
    data = request.get_json()
    
    updates = []
    params = []
    
    if "time" in data:
        updates.append("time=%s")
        params.append(data["time"])
    if "title" in data:
        updates.append("title=%s")
        params.append(data["title"])
    if "items" in data:
        import json
        updates.append("items_json=%s")
        params.append(json.dumps(data["items"]))
    if "isCompleted" in data:
        updates.append("is_completed=%s")
        params.append(data["isCompleted"])
    
    if not updates:
        return jsonify({"message": "No changes"}), 200
        
    params.append(sid)
    params.append(uid)
    
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"UPDATE feeding_schedules SET {', '.join(updates)} WHERE id=%s AND user_id=%s",
                tuple(params)
            )
            conn.commit()
    finally:
        conn.close()
    return jsonify({"message": "Schedule updated"}), 200


@feed_bp.route("/schedules/<int:sid>", methods=["DELETE"])
def delete_schedule(sid):
    err = require_login()
    if err:
        return err
    uid = session["user_id"]
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM feeding_schedules WHERE id=%s AND user_id=%s", (sid, uid))
            conn.commit()
    finally:
        conn.close()
    return jsonify({"message": "Schedule deleted"}), 200
