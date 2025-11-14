# Book Library API (Flask)

## Project Description

A simple Flask REST API for managing a small in-memory collection of books.
It supports listing, reading, creating, updating, and deleting books.

---

## Features

- List all books
- Get a book by ID
- Add a new book (title, author, year, publisher)
- Update an existing book
- Delete a book by ID

---

## API Endpoints

1. GET /books  
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

2. GET /books/{book_id}  
   Description: Returns details of a specific book.  
   Parameters: book_id (string, required): Unique book ID (e.g., BK1002)  
   Response Example:  
   {  
    "title": "Atomic Habits",  
    "author": "James Clear",  
    "year": 2018,  
    "publisher": "Avery"  
   }  
   Errors:  
   404: Book not found  
   400: Invalid ID format  

3. POST /books/add/{book_id}  
   Description: Creates a new book with the provided ID.  
   Parameters: book_id (string, required): New unique book ID  
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
   409: Book already exists  
   400: Invalid data provided  
   400: Missing fields in request body (required: title, author, year, publisher)  

4. PUT /books/update/{book_id}  
   Description: Updates an existing book’s fields  
   Parameters: book_id (string, required): Existing book ID  
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
   404: Book not found  
   400: Invalid data provided  

5. DELETE /books/delete/{book_id}  
   Description: Deletes a book by ID.  
   Parameters: book_id (string, required): Existing book ID  
   Response Example:  
   {  
    "message": "Book BK1006 deleted successfully"  
   }  
   Errors:  
   404: Book not found   
   400: Invalid ID format  

---

## Setup Instructions

1. Install dependencies
   Create a requirements.txt (if you do not have it) with:
   flask

   Then:
   pip install -r requirements.txt

2. Save the Python code as main.py

3. Run the server
   Run python main.py

   The app starts in debug mode on http://127.0.0.1:5000

---

## Example API Calls

Using cURL

1. Get all books
   curl -i http://127.0.0.1:5000/books

2. Get a book by ID
   curl -i http://127.0.0.1:5000/books/BK1002

3. Add a new book
   curl -i -X POST http://127.0.0.1:5000/books/add/BK1006 \
    -H "Content-Type: application/json" \
    -d '{
    "title": "Harry Potter and the Philosopher's Stone",
    "author": "J.K. Rowling",
    "year": 1997,
    "publisher": "Bloomsbury"
   }'

4. Update a book
   curl -i -X PUT http://127.0.0.1:5000/books/update/BK1006 \
    -H "Content-Type: application/json" \
    -d '{
    "year": 1998,
    "publisher": "Scholastic"
   }'

5. Delete a book
   curl -i -X DELETE http://127.0.0.1:5000/books/delete/BK1006

Using Postman

1. Base URL: http://127.0.0.1:5000

2. GET /books: Create a new request → GET → {{baseUrl}}/books → Send.

3. GET /books/:id: GET → {{baseUrl}}/books/BK1002 → Send.

4. POST /books/add/:id: POST → {{baseUrl}}/books/add/BK1006
   Body → raw → JSON:
   {
    "title": "Harry Potter and the Philosopher's Stone",
    "author": "J.K. Rowling",
    "year": 1997,
    "publisher": "Bloomsbury"
   }
   Send.

5. PUT /books/update/:id: PUT → {{baseUrl}}/books/update/BK1006
   Body → raw → JSON (any subset of fields).
   Example:
   {
    "title": "Harry Potter and the Sorcerer's Stone",
    "author": "J.K. Rowling",
    "year": 1998,
    "publisher": "Scholastic"
   }

6. DELETE /books/delete/:id: DELETE → {{baseUrl}}/books/delete/BK1006 → Send.
