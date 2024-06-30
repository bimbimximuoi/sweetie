from flask import Blueprint, request, jsonify, current_app, send_file
from werkzeug.utils import secure_filename
import os
from io import BytesIO

storage_bp = Blueprint('storage_bp', __name__)

# User book routes
@storage_bp.route('/storage/users/<user_id>/books/<book_id>/add', methods=['POST'])
def add_user_book(user_id, book_id):
    file = request.files.get('file')
    if not file:
        return jsonify({"error": "No file part"}), 400

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    file_ext = os.path.splitext(file.filename)[1]
    filename = secure_filename(f"{book_id}{file_ext}")
    user_path = f"users/{user_id}/books/{filename}"
    bucket = current_app.config['STORAGE']
    blob = bucket.blob(user_path)
    blob.upload_from_file(file.stream)
    return jsonify({"success": True, "filename": user_path}), 200

@storage_bp.route('/storage/users/<user_id>/books/<book_id>/get', methods=['GET'])
def get_user_book(user_id, book_id):
    bucket = current_app.config['STORAGE']
    user_path = f"users/{user_id}/books/{book_id}"
    blobs = list(bucket.list_blobs(prefix=user_path))

    if not blobs:
        return jsonify({"error": "File not found"}), 404

    file_data = blobs[0].download_as_bytes()
    filename = blobs[0].name.split("/")[-1]
    return send_file(BytesIO(file_data), download_name=filename, as_attachment=True)

@storage_bp.route('/storage/users/<user_id>/books/<book_id>/update', methods=['POST'])
def update_user_book(user_id, book_id):
    delete_user_book(user_id, book_id)
    return add_user_book(user_id, book_id)

@storage_bp.route('/storage/users/<user_id>/books/<book_id>/delete', methods=['DELETE'])
def delete_user_book(user_id, book_id):
    bucket = current_app.config['STORAGE']
    user_path = f"users/{user_id}/books/{book_id}"
    blobs = list(bucket.list_blobs(prefix=user_path))

    if not blobs:
        return jsonify({"error": "File not found"}), 404

    for blob in blobs:
        blob.delete()

    return jsonify({"success": True, "book_id": book_id}), 200

# User podcast routes
@storage_bp.route('/storage/users/<user_id>/podcast/<podcast_id>/add', methods=['POST'])
def add_user_podcast(user_id, podcast_id):
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    file_ext = os.path.splitext(file.filename)[1]
    filename = secure_filename(f"{podcast_id}{file_ext}")
    user_path = f"users/{user_id}/podcasts/{filename}"
    bucket = current_app.config['STORAGE']
    blob = bucket.blob(user_path)
    blob.upload_from_file(file.stream)
    return jsonify({"success": True, "filename": user_path}), 200

@storage_bp.route('/storage/users/<user_id>/podcast/<podcast_id>/get', methods=['GET'])
def get_user_podcast(user_id, podcast_id):
    bucket = current_app.config['STORAGE']
    user_path = f"users/{user_id}/podcasts/{podcast_id}"
    blobs = list(bucket.list_blobs(prefix=user_path))

    if not blobs:
        return jsonify({"error": "File not found"}), 404

    file_data = blobs[0].download_as_bytes()
    filename = blobs[0].name.split("/")[-1]
    return send_file(BytesIO(file_data), download_name=filename, as_attachment=True)

@storage_bp.route('/storage/users/<user_id>/podcast/<podcast_id>/update', methods=['POST'])
def update_user_podcast(user_id, podcast_id):
    delete_user_podcast(user_id, podcast_id)
    return add_user_podcast(user_id, podcast_id)

@storage_bp.route('/storage/users/<user_id>/podcast/<podcast_id>/delete', methods=['DELETE'])
def delete_user_podcast(user_id, podcast_id):
    bucket = current_app.config['STORAGE']
    user_path = f"users/{user_id}/podcasts/{podcast_id}"
    blobs = list(bucket.list_blobs(prefix=user_path))

    if not blobs:
        return jsonify({"error": "File not found"}), 404

    for blob in blobs:
        blob.delete()

    return jsonify({"success": True, "podcast_id": podcast_id}), 200

# Community book routes
@storage_bp.route('/storage/community/books/add', methods=['POST'])
def add_community_book():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    book_id = request.form.get('book_id')
    if not book_id:
        return jsonify({"error": "No book_id provided"}), 400

    file_ext = os.path.splitext(file.filename)[1]
    filename = secure_filename(f"{book_id}{file_ext}")
    community_path = f"community/{filename}"
    bucket = current_app.config['STORAGE']
    blob = bucket.blob(community_path)
    blob.upload_from_file(file.stream)
    return jsonify({"success": True, "filename": community_path}), 200

@storage_bp.route('/storage/community/books/get', methods=['GET'])
def get_community_books():
    bucket = current_app.config['STORAGE']
    blobs = bucket.list_blobs(prefix="community/")
    
    files = [blob.name for blob in blobs]
    return jsonify({"files": files}), 200

@storage_bp.route('/storage/community/books/<book_id>/get', methods=['GET'])
def get_community_book(book_id):
    bucket = current_app.config['STORAGE']
    community_path = f"community/{book_id}"
    blobs = list(bucket.list_blobs(prefix=community_path))

    if not blobs:
        return jsonify({"error": "File not found"}), 404

    file_data = blobs[0].download_as_bytes()
    filename = blobs[0].name.split("/")[-1]
    return send_file(BytesIO(file_data), download_name=filename, as_attachment=True)



# @storage_bp.route('/storage/users/<user_id>/books/<book_id>/add', methods=['GET'])
# @storage_bp.route('/storage/users/<user_id>/book/<book_id>/get', methods=['GET'])
# @storage_bp.route('/storage/users/<user_id>/book/<book_id>/update', methods=['GET'])
# @storage_bp.route('/storage/users/<user_id>/book/<book_id>/delete', methods=['GET'])

# @storage_bp.route('/storage/users/<user_id>/podcast/<book_id>/add', methods=['GET'])
# @storage_bp.route('/storage/users/<user_id>/podcast/<book_id>/get', methods=['GET'])
# @storage_bp.route('/storage/users/<user_id>/podcast/<book_id>/update', methods=['GET'])
# @storage_bp.route('/storage/users/<user_id>/podcast/<book_id>/delete', methods=['GET'])

# @storage_bp.route('/storage/community/books/add', methods=['GET'])
# @storage_bp.route('/storage/community/books/get', methods=['GET'])
# @storage_bp.route('/storage/community/books/<book_id>/get', methods=['GET'])