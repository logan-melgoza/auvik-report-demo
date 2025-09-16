from flask import Flask, send_from_directory, jsonify, request, session
from flask_bcrypt import Bcrypt
from flask_session import Session
from flask_cors import CORS
from sqlalchemy import text
from config import ApplicationConfig
from models import db, User
from dotenv import load_dotenv
from hmac import compare_digest
from auvik_report import generate_report, gather_tenants
import os

OUTPUT_DIR = os.path.join(os.getcwd(), 'output')

load_dotenv('.env')

app = Flask(__name__)
app.config.from_object(ApplicationConfig)

Session(app)

CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")}})

db.init_app(app)
bcrypt = Bcrypt(app)

with app.app_context():
    db.create_all()

@app.route("/api/register", methods=["POST"])
def register_user():
    data = request.get_json()
    email = data.get("email").strip().lower()
    password = data.get("password")
    confirm_password = data.get("confirmPassword")
    invite = data.get('invite')

    reg_secret = os.getenv('REGISTRATION_SECRET')
    if not invite or not reg_secret or not compare_digest(invite, reg_secret):
        return jsonify({'error': 'Invalid invitation'}), 403

    
    if not email or not password or not confirm_password:
        return jsonify({"error": "Missing Fields"}), 400
    
    if password != confirm_password:
        return jsonify({"error": "Passwords do not match"}), 400
    
    user_exists = User.query.filter_by(email=email).first()
    if user_exists:
        return jsonify({"error": "User already exists"}), 409
    
    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
    new_user = User(email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    session["user_id"] = new_user.id
    return jsonify({
        "id": new_user.id,
        "email": new_user.email
    }), 201

@app.route("/api/login", methods=["POST"])
def login_user():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Missing Fields"}), 400

    user = User.query.filter_by(email=email).first()

    if user is None:
        return jsonify({"error": "Unauthorized"}), 401
    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({"error": "Unauthorized"}), 401

    session["user_id"] = user.id
    return jsonify({
        "id": user.id,
        "email": user.email
    }), 200

@app.route("/api/me")
def me():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    user = User.query.filter_by(id=user_id).first()
    return jsonify({
        "id": user.id,
        "email": user.email
    }), 200

@app.route("/api/logout", methods=["POST"])
def logout_user():
    session.pop("user_id", None)
    return "", 204

@app.get("/api/health/db")
def health_db():
    try:
        db.session.execute(text("SELECT 1"))
        return jsonify({"db": "ok"}), 200
    except Exception as e:
        return jsonify({"db": "error", "detail": str(e)}), 500

@app.route("/api/generate-report", methods=["POST"])
def generate_report_route():
    data = request.get_json()
    domain = data.get("domain")

    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    name = generate_report(domain)

    pdf_path = f'/output/{domain}.pdf'

    return jsonify({
        'domain': domain,
        'name': name,
        'preview': pdf_path,
        'download': pdf_path
    })

@app.route("/api/tenants")
def gather_tenants_list():
    tenants = gather_tenants()
    return jsonify(tenants)

@app.route("/output/<path:filename>")
def serve_report(filename):
    return send_from_directory(OUTPUT_DIR, filename)

if __name__ == "__main__":
    app.run(port=5555, debug=True)
