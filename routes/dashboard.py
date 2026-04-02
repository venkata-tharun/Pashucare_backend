from flask import Blueprint, jsonify, session
from models.db import get_connection
from datetime import date

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")

def require_login():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

@dashboard_bp.route("/stats", methods=["GET"])
def get_stats():
    err = require_login()
    if err: return err
    
    uid = session["user_id"]
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # 1. Total Animals
            cur.execute("SELECT COUNT(*) as count FROM animals WHERE user_id=%s", (uid,))
            total_animals = cur.fetchone()["count"]
            
            # 2. Milk Today
            today = date.today().strftime('%Y-%m-%d')
            cur.execute(
                "SELECT SUM(am + noon + pm) as total FROM milk_entries WHERE user_id=%s AND date=%s",
                (uid, today)
            )
            milk_today_res = cur.fetchone()["total"]
            milk_today = f"{float(milk_today_res or 0):.1f}L"
            
            # 3. Visitors Today
            cur.execute("SELECT COUNT(*) as count FROM visitors WHERE user_id=%s AND date=%s", (uid, today))
            visitors_today = cur.fetchone()["count"]
            
            # 4. Sanitation Score
            cur.execute("SELECT score FROM sanitation_scores WHERE user_id=%s ORDER BY updated_at DESC LIMIT 1", (uid,))
            s_row = cur.fetchone()
            sanitation_score = s_row["score"] if s_row else "–"
            
            # 5. Calving Count (Active/Total records)
            cur.execute("SELECT COUNT(*) as count FROM calving_records WHERE user_id=%s", (uid,))
            calving_count = cur.fetchone()["count"]
            
            # 6. Revenue Today
            cur.execute(
                "SELECT SUM(amount) as total FROM transactions WHERE user_id=%s AND date=%s AND category='Income'",
                (uid, today)
            )
            rev_res = cur.fetchone()["total"]
            revenue_today = f"₹{int(rev_res or 0)}"

            # 7. Next Feeding Time
            cur.execute("SELECT time FROM feeding_schedules WHERE user_id=%s ORDER BY time ASC", (uid,))
            schedules = cur.fetchall()
            next_feed_time = "Not Set"
            if schedules:
                from datetime import datetime
                now_str = datetime.now().strftime("%H:%M")
                
                # Find first schedule after now
                upcoming = next((s["time"] for s in schedules if s["time"] > now_str), None)
                
                # If none today, pick the first one (for tomorrow)
                target_time = upcoming if upcoming else schedules[0]["time"]
                
                # Format to 12h
                try:
                    t_obj = datetime.strptime(target_time, "%H:%M")
                    next_feed_time = t_obj.strftime("%I:%M %p")
                except:
                    next_feed_time = target_time

            # 8. Recent Activity
            cur.execute(
                "SELECT * FROM farm_logs WHERE user_id=%s ORDER BY date DESC, id DESC LIMIT 5",
                (uid,)
            )
            recent_logs = cur.fetchall()
            for l in recent_logs:
                if l.get("date"): l["date"] = str(l["date"])

    finally:
        conn.close()
        
    return jsonify({
        "totalAnimals": total_animals,
        "milkToday": milk_today,
        "visitorsToday": visitors_today,
        "sanitationScore": sanitation_score,
        "calvingCount": calving_count,
        "revenueToday": revenue_today,
        "nextFeedTime": next_feed_time,
        "recentLogs": recent_logs
    }), 200

