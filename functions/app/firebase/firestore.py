from flask import Blueprint, request, jsonify, current_app

firestore_bp = Blueprint('firestore_bp', __name__)

# Books routes
@firestore_bp.route('/firestore/books/add', methods=['POST'])
def add_book():
    data = request.get_json()
    db = current_app.config['FIRESTORE']
    doc_ref = db.collection('books').document()
    doc_ref.set(data)
    return jsonify({"success": True, "id": doc_ref.id}), 200

@firestore_bp.route('/firestore/books/<book_id>/delete', methods=['DELETE'])
def delete_book(book_id):
    db = current_app.config['FIRESTORE']
    doc_ref = db.collection('books').document(book_id)
    doc = doc_ref.get()
    if doc.exists:
        doc_ref.delete()
        return jsonify({"success": True, "id": book_id}), 200
    else:
        return jsonify({"error": "Book not found"}), 404

@firestore_bp.route('/firestore/books/<book_id>/update', methods=['PUT'])
def update_book(book_id):
    data = request.get_json()
    db = current_app.config['FIRESTORE']
    doc_ref = db.collection('books').document(book_id)
    doc = doc_ref.get()
    if doc.exists:
        doc_ref.update(data)
        return jsonify({"success": True, "id": book_id}), 200
    else:
        return jsonify({"error": "Book not found"}), 404


@firestore_bp.route('/firestore/books/user/<user_id>', methods=['GET'])
def get_user_books(user_id):
    db = current_app.config['FIRESTORE']
    books_ref = db.collection('books').where('user_id', '==', user_id)
    books = []
    for doc in books_ref.stream():
        book_data = doc.to_dict()
        book_data['id'] = doc.id
        books.append(book_data)
    return jsonify({"success": True, "books": books}), 200









# Users routes
@firestore_bp.route('/firestore/users/add', methods=['POST'])
def add_user():
    data = request.get_json()
    db = current_app.config['FIRESTORE']
    doc_ref = db.collection('users').document()
    doc_ref.set(data)
    return jsonify({"success": True, "id": doc_ref.id}), 200

@firestore_bp.route('/firestore/users/<user_id>/update', methods=['PUT'])
def update_user(user_id):
    data = request.get_json()
    db = current_app.config['FIRESTORE']
    doc_ref = db.collection('users').document(user_id)
    doc = doc_ref.get()
    if doc.exists:
        doc_ref.update(data)
        return jsonify({"success": True, "id": user_id}), 200
    else:
        return jsonify({"error": "User not found"}), 404

@firestore_bp.route('/firestore/users/<user_id>/delete', methods=['DELETE'])
def delete_user(user_id):
    db = current_app.config['FIRESTORE']
    doc_ref = db.collection('users').document(user_id)
    doc = doc_ref.get()
    if doc.exists:
        doc_ref.delete()
        return jsonify({"success": True, "id": user_id}), 200
    else:
        return jsonify({"error": "User not found"}), 404

# Published Books routes
@firestore_bp.route('/firestore/published_books/add/<book_id>', methods=['POST'])
def add_published_book(book_id):
    data = request.get_json()
    db = current_app.config['FIRESTORE']
    doc_ref = db.collection('published_books').document(book_id)
    doc_ref.set(data)
    return jsonify({"success": True, "id": doc_ref.id}), 200

@firestore_bp.route('/firestore/published_books/<book_id>/update', methods=['PUT'])
def update_published_book(book_id):
    data = request.get_json()
    db = current_app.config['FIRESTORE']
    doc_ref = db.collection('published_books').document(book_id)
    doc = doc_ref.get()
    if doc.exists:
        doc_ref.update(data)
        return jsonify({"success": True, "id": book_id}), 200
    else:
        return jsonify({"error": "Published book not found"}), 404

@firestore_bp.route('/firestore/published_books/<book_id>/delete', methods=['DELETE'])
def delete_published_book(book_id):
    db = current_app.config['FIRESTORE']
    doc_ref = db.collection('published_books').document(book_id)
    doc = doc_ref.get()
    if doc.exists:
        doc_ref.delete()
        return jsonify({"success": True, "id": book_id}), 200
    else:
        return jsonify({"error": "Published book not found"}), 404

# Translated Books routes
@firestore_bp.route('/firestore/translated_books/add', methods=['POST'])
def add_translated_book():
    data = request.get_json()
    db = current_app.config['FIRESTORE']
    doc_ref = db.collection('translated_books').document()
    doc_ref.set(data)
    return jsonify({"success": True, "id": doc_ref.id}), 200

@firestore_bp.route('/firestore/translated_books/<book_id>/update', methods=['PUT'])
def update_translated_book(book_id):
    data = request.get_json()
    db = current_app.config['FIRESTORE']
    doc_ref = db.collection('translated_books').document(book_id)
    doc = doc_ref.get()
    if doc.exists:
        doc_ref.update(data)
        return jsonify({"success": True, "id": book_id}), 200
    else:
        return jsonify({"error": "Translated book not found"}), 404

@firestore_bp.route('/firestore/translated_books/<book_id>/delete', methods=['DELETE'])
def delete_translated_book(book_id):
    db = current_app.config['FIRESTORE']
    doc_ref = db.collection('translated_books').document(book_id)
    doc = doc_ref.get()
    if doc.exists:
        doc_ref.delete()
        return jsonify({"success": True, "id": book_id}), 200
    else:
        return jsonify({"error": "Translated book not found"}), 404





# @firestore_bp.route('/firestore/books/add')
# @firestore_bp.route('/firestore/books/<book_id>/delete')
# @firestore_bp.route('/firestore/books/<book_id>/update')

# @firestore_bp.route('/firestore/users/add')
# @firestore_bp.route('/firestore/users/<user_id>/update')
# @firestore_bp.route('/firestore/users/<user_id>/delete')

# @firestore_bp.route('/firestore/published_books/add')
# @firestore_bp.route('/firestore/published_books/<book_id>/update')
# @firestore_bp.route('/firestore/published_books/<book_id>/delete')

# @firestore_bp.route('/firestore/translated_books/add')
# @firestore_bp.route('/firestore/translated_books/<book_id>/update')
# @firestore_bp.route('/firestore/translated_books/<book_id>/delete')