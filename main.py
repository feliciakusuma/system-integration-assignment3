from flask import Flask, jsonify, request

app = Flask(__name__)

# A simple in-memory database of books
books = {
    "BK1001": {
        "title": "The Intelligent Investor",
        "author": "Benjamin Graham",
        "year": 1949,
        "publisher": "Harper & Brothers"
    }, 
    "BK1002": {
        "title": "Atomic Habits",
        "author": "James Clear",
        "year": 2018,
        "publisher": "Avery"
    },
    "BK1003": {
        "title": "The Psychology of Money",
        "author": "Morgan Housel",
        "year": 2020,
        "publisher": "Harriman House"
    },
    "BK1004": {
        "title": "Crime and Punishment",
        "author": "Fyodor Dostoevsky",
        "year": 1866,
        "publisher": "The Russian Messenger"
    },
    "BK1005": {
        "title": "To Kill a Mockingbird",
        "author": "Harper Lee",
        "year": 1960,
        "publisher": "J. B. Lippincott & Co."
    }
}

# Retrieve all books
@app.route('/books', methods=['GET'])
def get_all_books():
    return jsonify(books), 200

# Retrieve a specific book by ID
@app.route('/books/<string:book_id>', methods=['GET'])
def get_book(book_id):
    book = books.get(book_id)
    if book:
        return jsonify(book), 200
    else:
        return jsonify({"error": "Book not found"}), 404

# Add a new book with details: title, author, year, publisher
@app.route('/books/add/<string:book_id>', methods=['POST'])
def add_book(book_id):
    # Check if book already exists
    if book_id in books:
        return jsonify({"error": "Book already exists"}), 409

    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid data provided"}), 400

    required_fields = ["title", "author", "year", "publisher"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing fields in request body"}), 400

    books[book_id] = {
        "title": data["title"],
        "author": data["author"],
        "year": data["year"],
        "publisher": data["publisher"]
    }

    return jsonify(books[book_id]), 201

# Update an existing book's details
@app.route('/books/update/<string:book_id>', methods=['PUT'])
def update_book(book_id):
    if book_id not in books:
        return jsonify({"error": "Book not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid data provided"}), 400

    # Update only the fields provided in the request
    for key in ["title", "author", "year", "publisher"]:
        if key in data:
            books[book_id][key] = data[key]

    return jsonify(books[book_id]), 200

# Delete a book by ID
@app.route('/books/delete/<string:book_id>', methods=['DELETE'])
def delete_book(book_id):
    if book_id in books:
        del books[book_id]
        return jsonify({"message": f"Book {book_id} deleted successfully"}), 200
    else:
        return jsonify({"error": "Book not found"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)
