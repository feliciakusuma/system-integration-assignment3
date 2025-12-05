# main.py
import os
import json
import datetime
from flask import Flask, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, JWTManager, get_jwt_identity, get_jwt
from passlib.hash import pbkdf2_sha256 as hasher

app = Flask(__name__)

# JWT configuration
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "your-very-secure-jwt-signing-secret")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(hours=1)
jwt = JWTManager(app)

# ------------------------------
# Persistent user storage
# ------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(BASE_DIR, "users.json")

# Load users from file
def load_users():
    """Load users from a JSON file (persistent mock DB)."""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass

    # Default users if file doesn't exist or is invalid
    return {
        "user1": {
            "password_hash": hasher.hash("password123"),
            "roles": ["user"],
        },
        "admin": {
            "password_hash": hasher.hash("password456"),
            "roles": ["admin", "user"],
        },
    }

# Save users to file
def save_users():
    with open(USERS_FILE, "w") as f:
        json.dump(USERS, f, indent=2)


# Load users at startup
USERS = load_users()
# Ensure defaults are saved if file was missing/corrupt
save_users()

# ------------------------------
# In-memory books database
# ------------------------------

books = {
    "BK1001": {
        "title": "The Intelligent Investor",
        "author": "Benjamin Graham",
        "year": 1949,
        "publisher": "Harper & Brothers",
        "owner": "admin",
    },
    "BK1002": {
        "title": "Atomic Habits",
        "author": "James Clear",
        "year": 2018,
        "publisher": "Avery",
        "owner": "admin",
    },
    "BK1003": {
        "title": "The Psychology of Money",
        "author": "Morgan Housel",
        "year": 2020,
        "publisher": "Harriman House",
        "owner": "admin",
    },
    "BK1004": {
        "title": "Crime and Punishment",
        "author": "Fyodor Dostoevsky",
        "year": 1866,
        "publisher": "The Russian Messenger",
        "owner": "admin",
    },
    "BK1005": {
        "title": "To Kill a Mockingbird",
        "author": "Harper Lee",
        "year": 1960,
        "publisher": "J. B. Lippincott & Co.",
        "owner": "admin",
    },
}

# ------------------------------
# AUTHENTICATION (JWT)
# ------------------------------

# Authentication endpoint
@app.route("/login", methods=["POST"])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    if username not in USERS:
        return jsonify({"msg": "Bad username or password"}), 401

    user_record = USERS[username]
    if not hasher.verify(password or "", user_record["password_hash"]):
        return jsonify({"msg": "Bad username or password"}), 401

    user_roles = user_record["roles"]
    additional_claims = {"roles": user_roles}

    access_token = create_access_token(
        identity=username,
        additional_claims=additional_claims,
    )

    return jsonify(access_token=access_token), 200

# Authorization endpoint for user role
@app.route("/protected_user", methods=["GET"])
@jwt_required()
def protected_user_route():
    current_user = get_jwt_identity()
    return jsonify(
        logged_in_as=current_user,
        message=f"Hi {current_user}, you have successfully signed in as a standard user.",
    ), 200

# Authorization endpoint for admin role
@app.route("/protected_admin", methods=["GET"])
@jwt_required()
def protected_admin_route():
    claims = get_jwt()

    if "admin" not in claims.get("roles", []):
        return jsonify(msg="Admins only!"), 403

    current_user = get_jwt_identity()
    return jsonify(
        logged_in_as=current_user,
        message=f"Access granted: {current_user} is an admin.",
    ), 200


# ------------------------------
# REGISTRATION
# ------------------------------

# Registration endpoint
@app.route("/register", methods=["POST"])
def register():
    payload = request.get_json() or {}
    username = (payload.get("username") or "").strip()
    password = payload.get("password") or ""

    if not username or not password:
        return jsonify(msg="Username and password are required"), 400

    if username in USERS:
        return jsonify(msg="User already exists"), 409

    USERS[username] = {
        "password_hash": hasher.hash(password),
        "roles": ["user"],
    }
    save_users()

    return jsonify(msg="User registered successfully"), 201


# ------------------------------
# BOOK ENDPOINTS (JWT-PROTECTED + OWNER CHECKS)
# ------------------------------

# Retrieve all books
@app.route("/books", methods=["GET"])
@jwt_required()
def get_all_books():
    return jsonify(books), 200

# Retrieve a specific book by ID
@app.route("/books/<string:book_id>", methods=["GET"])
@jwt_required()
def get_book(book_id):
    book = books.get(book_id)
    if book:
        return jsonify(book), 200
    else:
        return jsonify({"error": "Book not found"}), 404

# Add a new book
@app.route("/books/add/<string:book_id>", methods=["POST"])
@jwt_required()
def add_book(book_id):
    current_user = get_jwt_identity()
    claims = get_jwt()

    if "admin" not in claims.get("roles", []):
        return jsonify({"error": "Admins only"}), 403

    if book_id in books:
        return jsonify({"error": "Book already exists"}), 409

    data = request.get_json() or {}
    if not data:
        return jsonify({"error": "Invalid data provided"}), 400

    required_fields = ["title", "author", "year", "publisher"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing fields in request body"}), 400

    books[book_id] = {
        "title": data["title"],
        "author": data["author"],
        "year": data["year"],
        "publisher": data["publisher"],
        "owner": current_user,
    }

    return jsonify(books[book_id]), 201

# Update an existing book
@app.route("/books/update/<string:book_id>", methods=["PUT"])
@jwt_required()
def update_book(book_id):
    current_user = get_jwt_identity()
    claims = get_jwt()

    if "admin" not in claims.get("roles", []):
        return jsonify({"error": "Admins only"}), 403

    if book_id not in books:
        return jsonify({"error": "Book not found"}), 404

    data = request.get_json() or {}
    if not data:
        return jsonify({"error": "Invalid data provided"}), 400

    for key in ["title", "author", "year", "publisher"]:
        if key in data:
            books[book_id][key] = data[key]

    return jsonify(books[book_id]), 200

# Delete a book
@app.route("/books/delete/<string:book_id>", methods=["DELETE"])
@jwt_required()
def delete_book(book_id):
    current_user = get_jwt_identity()
    claims = get_jwt()

    if "admin" not in claims.get("roles", []):
        return jsonify({"error": "Admins only"}), 403

    if book_id in books:
        del books[book_id]
        return jsonify({"message": f"Book {book_id} deleted successfully"}), 200

    return jsonify({"error": "Book not found"}), 404

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True, port=5000, ssl_context="adhoc")
