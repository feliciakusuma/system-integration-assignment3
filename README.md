# Book Library API (Flask + JWT)

## Project Description

A simple Flask REST API for managing a small in-memory collection of books.
It supports listing, retrieving, creating, updating, and deleting books.

The API is secured with **JWT-based Authentication and Authorization**. Users must register, log in to receive a JWT access token, and then include that token as a Bearer token on protected endpoints.

---

## Features

- List all books
- Get a book by ID
- Add a new book (title, author, year, publisher)
- Update an existing book
- Delete a book by ID
- Register new users and log in to receive JWT tokens
- Role claims in tokens (admin/user) gate certain actions

---

## Method (Auth & Authorization Design)

This project demonstrates secure API access using **JWT**:

- **Authentication**

  - `POST /register` lets new users create accounts.
  - `POST /login` verifies username/password and returns a signed JWT access token.
  - Passwords are hashed using `PBKDF2-SHA256` (`passlib.hash.pbkdf2_sha256`) and never stored in plain text.

- **Persistent User Store**

  - All user credentials (username + password hash + roles) are stored in `users.json`.
  - On startup, the app loads `users.json`. If the file is missing or invalid, default users (`user1`, `admin`) are created.
  - When a new user registers, `users.json` is updated so users persist across app restarts.

- **Authorization**
  - All book endpoints are protected with `@jwt_required()`. Only authenticated users can access them.
  - JWT tokens include a `roles` claim:
    - Default registered users: `["user"]`
    - Seed admin user: `["admin", "user"]`
  - Admin-only actions:
    - `POST /books/add/<book_id>`
    - `PUT /books/update/<book_id>`
    - `DELETE /books/delete/<book_id>`
  - The book records also store an `owner` field, set to the username of the creator. Update/delete endpoints verify that the caller either:
    - owns the book, or
    - has the `admin` role (depending on how you enforce it in code).

---

## Setup Instructions

1. Install dependencies
   Create a requirements.txt (if you do not have it) with:
   - `flask`
   - `flask-jwt-extended`
   - `PyJWT`
   - `passlib`

   pip install -r requirements.txt

3. Run the application
   python main.py

   The app starts in debug mode on https://localhost:5000

---

## Troubleshooting

1. ModuleNotFoundError: No module named 'flask_jwt_extended

   This means the required dependencies are not installed.

   **Fix:**
   
   ```bash
   pip install -r requirements.txt
   ```

2. Certificate / SSL errors in curl or Postman

   The app uses a self-signed HTTPS certificate for local development.
   
   **Fix:**
   
   Use the `-k` flag to skip certificate verification:
   
   `curl -k https://localhost:5000/...`
   In Postman, disable SSL verification for `https://localhost:5000` in Settings (for local use only).

3. `401 Unauthorized` on protected endpoints
   This happens when the request doesn’t include a valid JWT access token.
   
   **Fix:**
   
   - Call `POST /login` with valid credentials.
   - Copy the `access_token` from the JSON response.
   - Include the token in the `Authorization` header on protected endpoints:  
      `Authorization: Bearer <token>`
   - Make sure you are sending the header on every protected request (e.g., `/books`, `/protected_user`, `/protected_admin`).

4. `json.decoder.JSONDecodeError` when starting the app  
    This usually means users.json is corrupted (for example, from manual editing or a partial write).

    **Fix:**
    - Delete the `users.json` file.
    - Restart the app.
    - The application will recreate `users.json` with default users.
    
---

## API Endpoints

All endpoints in this section require Authorization: Bearer <token> unless otherwise specified.

1. `GET /books`   
   Description: Returns all books.  
   Parameters: —  
   Response Example:  
   {  
    "BK1001": {  
    "title": "The Intelligent Investor",  
    "author": "Benjamin Graham",  
    "year": 1949,  
    "publisher": "Harper & Brothers"  
    }  
    ...  
    "BK1005": {  
    "title": "To Kill a Mockingbird",  
    "author": "Harper Lee",  
    "year": 1960,  
    "publisher": "J. B. Lippincott & Co."  
    }  
   }

2. `GET /books/{book_id}`   
   Description: Returns details of a specific book.  
   Parameters: `book_id` (string, required): Unique book ID (e.g., `BK1002`)  
   Response Example:  
   {  
    "title": "Atomic Habits",  
    "author": "James Clear",  
    "year": 2018,  
    "publisher": "Avery"  
   }  
   Errors:  
   `404`: Book not found  
   `400`: Invalid ID format

3. `POST /books/add/{book_id}`  
   Description: Creates a new book with the provided ID.  
   Parameters: `book_id` (string, required): New unique book ID  
   Request Body (JSON):  
   {  
    "title": "Harry Potter and the Philosopher's Stone",  
    "author": "J.K. Rowling",  
    "year": 1997,  
    "publisher": "Bloomsbury"  
   }  
   Response Example:  
   {  
    "title": "Harry Potter and the Philosopher's Stone",  
    "author": "J.K. Rowling",  
    "year": 1997,  
    "publisher": "Bloomsbury"  
   }  
   Errors:  
   `409`: Book already exists  
   `400`: Invalid or missing data

4. `PUT /books/update/{book_id}`  
   Description: Updates an existing book’s fields  
   Parameters: `book_id` (string, required): Existing book ID  
   Request Body (JSON): (any subset of fields)  
   Request Body (JSON):  
   {  
    "publisher": "Scholastic",  
    "year": 1998  
   }  
   Response Example:  
   {  
    "title": "Harry Potter and the Sorcerer's Stone",  
    "author": "J.K. Rowling",  
    "year": 1998,  
    "publisher": "Scholastic"  
   }  
   Errors:  
   `404`: Book not found  
   `400`: Invalid data provided

5. `DELETE /books/delete/{book_id}`  
   Description: Deletes a book by ID.  
   Parameters: `book_id` (string, required): Existing book ID  
   Response Example:  
   {  
    "message": "Book BK1006 deleted successfully"  
   }  
   Errors:  
   `404`: Book not found  
   `400`: Invalid ID format

---

## Usage Examples (curl)

Disable TLS verification for local self-signed certs (curl example uses `-k`).

1. Register a user:  
   curl -k -X POST https://localhost:5000/register \\
   -H "Content-Type: application/json" \\
   -d '{"username":"user2","password":"pass123"}'

2. Login to get a token:  
   TOKEN=$(curl -k -s -X POST https://localhost:5000/login \\
   -H "Content-Type: application/json" \\
   -d '{"username":"user2","password":"pass123"}' | jq -r .access_token)

3. Get all books:  
   curl -k -H "Authorization: Bearer $TOKEN" https://localhost:5000/books

4. Get a book by ID:  
   curl -k -H "Authorization: Bearer $TOKEN" https://localhost:5000/books/BK1002

5. Add a new book (admin token required):  
   curl -k -X POST https://localhost:5000/books/add/BK1006 \\
   -H "Authorization: Bearer $TOKEN" \\
   -H "Content-Type: application/json" \\
   -d '{  
    "title": "Harry Potter and the Philosopher's Stone",  
    "author": "J.K. Rowling",  
    "year": 1997,  
    "publisher": "Bloomsbury"  
   }'

6. Update a book (admin token required):  
   curl -k -X PUT https://localhost:5000/books/update/BK1006 \\
   -H "Authorization: Bearer $TOKEN" \\
   -H "Content-Type: application/json" \\
   -d '{  
    "year": 1998,  
    "publisher": "Scholastic"  
   }'

7. Delete a book (admin token required):  
   curl -k -X DELETE https://localhost:5000/books/delete/BK1006 \\
   -H "Authorization: Bearer $TOKEN"

---

## Usage Examples (Postman)

1. Base setup

   - Base URL: `https://localhost:5000` (self-signed; disable SSL verification for this host in Postman settings).

2. Register

   - Method/URL: `POST {{baseUrl}}/register`
   - Body: raw JSON

   ```json
   { "username": "user2", "password": "pass123" }
   ```

3. Login (get token)

   - Method/URL: `POST {{baseUrl}}/login`
   - Body: raw JSON (same as above)

4. Use token on protected requests

   - Authorization tab: type `Bearer Token`, value `{{token}}` (or manually add header `Authorization: Bearer {{token}}`).

5. Example requests
   - `GET {{baseUrl}}/protected_user` (any logged-in user)
   - `GET {{baseUrl}}/protected_admin` (requires admin; login as `admin`)
   - `GET {{baseUrl}}/books`
   - `GET {{baseUrl}}/books/BK1002`
   - `POST {{baseUrl}}/books/add/BK1006` (admin only; body: book JSON)
   - `PUT {{baseUrl}}/books/update/BK1006` (admin only; body: fields to change)
   - `DELETE {{baseUrl}}/books/delete/BK1006` (admin only)
