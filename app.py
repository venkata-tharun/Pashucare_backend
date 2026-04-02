import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask
from flask_session import Session
from flask_mail import Mail
import config
from dotenv import load_dotenv

load_dotenv()

from routes.auth         import auth_bp
from routes.animals      import animals_bp
from routes.milk         import milk_bp
from routes.transactions import transactions_bp
from routes.visitors     import visitors_bp
from routes.calving      import calving_bp
from routes.feed         import feed_bp
from routes.sanitation   import sanitation_bp
from routes.logs         import logs_bp
from routes.ai           import ai_bp
from routes.dashboard    import dashboard_bp
from routes.reports_export import reports_export_bp

app = Flask(__name__)

# ── Uploads Configuration ──────────────────────────────────────────
# Set up a folder for AI prediction images
UPLOAD_FOLDER = os.path.join(app.root_path, 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(os.path.join(UPLOAD_FOLDER, 'ai_images'), exist_ok=True)

# Serve static files from the uploads folder
from flask import send_from_directory
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ── Session Manager ────────────────────────────────────────────────
app.secret_key                    = config.SECRET_KEY
app.config["SESSION_TYPE"]        = config.SESSION_TYPE
app.config["SESSION_PERMANENT"]   = config.SESSION_PERMANENT
app.config["PERMANENT_SESSION_LIFETIME"] = config.PERMANENT_SESSION_LIFETIME
Session(app)   # Initialise Flask-Session (filesystem-backed, persists across restarts)

# ── Mail Setup ─────────────────────────────────────────────────────
smtp_port = int(os.getenv("SMTP_PORT", 587))
app.config['MAIL_SERVER'] = os.getenv("SMTP_SERVER", "smtp.gmail.com")
app.config['MAIL_PORT'] = smtp_port
app.config['MAIL_USE_TLS'] = (smtp_port == 587)
app.config['MAIL_USE_SSL'] = (smtp_port == 465)
app.config['MAIL_USERNAME'] = os.getenv("SMTP_USER", "")
app.config['MAIL_PASSWORD'] = os.getenv("SMTP_PASSWORD", "")
app.config['MAIL_DEFAULT_SENDER'] = os.getenv("SMTP_USER", "")
mail = Mail(app)

# ── CORS (allow iOS simulator to hit local API) ────────────────────
@app.after_request
def add_cors(response):
    response.headers["Access-Control-Allow-Origin"]      = "*"
    response.headers["Access-Control-Allow-Headers"]     = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"]     = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response

@app.route("/options-preflight", methods=["OPTIONS"])
def options():
    return "", 204

# ── Register blueprints ────────────────────────────────────────────
app.register_blueprint(auth_bp)
app.register_blueprint(animals_bp)
app.register_blueprint(milk_bp)
app.register_blueprint(transactions_bp)
app.register_blueprint(visitors_bp)
app.register_blueprint(calving_bp)
app.register_blueprint(feed_bp)
app.register_blueprint(sanitation_bp)
app.register_blueprint(logs_bp)
app.register_blueprint(ai_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(reports_export_bp)

# ── Health check & Root ────────────────────────────────────────────
@app.route("/", methods=["GET"])
def index():
    return {
        "status": "online",
        "message": "PashuCare Backend API is running. Base URL is /api"
    }, 200

@app.route("/favicon.ico")
def favicon():
    return "", 204

@app.route("/api/health", methods=["GET"])
def health():
    return {"status": "ok", "app": "PashuCare API"}, 200

# ── Global Error Handler ───────────────────────────────────────────
@app.errorhandler(Exception)
def handle_exception(e):
    # Log the error (optional)
    print(f"Server Error: {e}")
    # Return JSON instead of HTML
    return {"error": "Internal Server Error", "message": str(e)}, 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
