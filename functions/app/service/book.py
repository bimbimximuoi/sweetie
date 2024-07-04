from flask import Blueprint, request, jsonify, current_app, session, redirect, url_for
from .extract import *
from .models import Metadata, TextData, to_base64
from werkzeug.utils import secure_filename
from firebase_admin import firestore
from tqdm import tqdm
from .. import socketio

book_bp = Blueprint('book_bp', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'txt', 'pdf', 'mobi', 'epub'}

def extract_text(file, update_progress=None):
    filename = file.filename.lower()
    file.seek(0)
    if filename.endswith('.txt'):
        return extract_text_from_txt(file, update_progress=update_progress)
    elif filename.endswith('.pdf'):
        return extract_text_from_pdf(file, update_progress=update_progress)
    elif filename.endswith('.mobi'):
        return extract_text_from_mobi(file, update_progress=update_progress)
    elif filename.endswith('.epub'):
        return extract_text_from_epub(file, update_progress=update_progress)
    else:
        return {'error': 'Unsupported file format'}

def extract_cover_image(file):
    file.seek(0)
    filename = file.filename.lower()
    if filename.endswith('.pdf'):
        return extract_cover_image_from_pdf(file)
    elif filename.endswith('.mobi'):
        return extract_cover_image_from_mobi(file)
    elif filename.endswith('.epub'):
        return extract_cover_image_from_epub(file)
    else:
        return None

def extract_metadata(file):
    file.seek(0)
    filename = file.filename.lower()
    if filename.endswith('.pdf'):
        return extract_pdf_metadata(file)
    elif filename.endswith('.mobi'):
        return extract_mobi_metadata(file)
    elif filename.endswith('.epub'):
        return extract_epub_metadata(file)
    else:
        return {}

@book_bp.route('/book/extract', methods=['POST'])
def extract_book():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            bucket = current_app.config['STORAGE']
            blob = bucket.blob(filename)
            blob.upload_from_file(file.stream)
            file.seek(0)  # Reset file pointer to the beginning after upload

            def update_progress(current, total):
                progress = (current / total) * 100
                socketio.emit('progress', {'progress': progress}, to=session.get('socketio_id'))

            total_size = file.content_length
            texts = extract_text(file, update_progress=update_progress)
            file.seek(0)
            cover_image = extract_cover_image(file)
            file.seek(0)
            metadata_dict = extract_metadata(file)

            metadata = Metadata(
                title=metadata_dict.get("title", "Unknown Title"),
                authors=metadata_dict.get("authors", []),
                subject=metadata_dict.get("subject", "Unknown Subject"),
                keywords=metadata_dict.get("keywords", "Unknown Keywords")
            )

            text_data = TextData(
                texts=texts,
                cover_image=to_base64(cover_image) if cover_image else None,
                metadata=metadata
            )

            response = {
                'texts': text_data.texts,
                'cover_image': text_data.cover_image,
                'metadata': {
                    'title': text_data.metadata.title,
                    'authors': text_data.metadata.authors,
                    'subject': text_data.metadata.subject,
                    'keywords': text_data.metadata.keywords
                },
                'storage_url': blob.public_url
            }

            session['book_data'] = response

            # Emit a success event to the client with a redirect URL
            socketio.emit('upload_success', {'redirect_url': url_for('main_bp.book_detail')}, to=session.get('socketio_id'))
            return jsonify({'success': True}), 200
        else:
            return jsonify({'error': 'Invalid file format'}), 400
    except Exception as e:
        current_app.logger.error(f"Error extracting book: {str(e)}")
        return jsonify({'error': 'Internal Server Error'}), 500

@book_bp.route('/book/save', methods=['POST'])
def save_book():
    if 'user' not in session:
        return jsonify({'error': 'not_logged_in'}), 401

    user = session['user']
    try:
        book_data = request.get_json().get('book_data')
    except Exception as e:
        return jsonify({'error': 'Invalid JSON data'}), 400

    if not book_data:
        return jsonify({'error': 'No book data provided'}), 400

    try:
        db = current_app.config['FIRESTORE']
        books_ref = db.collection('books')
        book_ref = books_ref.document()

        book_info = {
            'title': book_data['metadata']['title'],
            'authors': book_data['metadata']['authors'],
            'subject': book_data['metadata']['subject'],
            'keywords': book_data['metadata']['keywords'],
            'cover_image': book_data['cover_image'],
            'texts': book_data['texts'],
            'storage_url': book_data.get('storage_url'),
            'user_id': user['uid']
        }

        book_ref.set(book_info)
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@book_bp.route('/api/book/publish', methods=['POST'])
def book_publish_api():
    if 'user' not in session:
        return jsonify({'error': 'not_logged_in'}), 401

    user = session['user']
    book_data = request.get_json()

    db = current_app.config['FIRESTORE']
    publish_ref = db.collection('published_books').document()
    
    book_info = {
        'title': book_data['title'],
        'authors': book_data['authors'],
        'subject': book_data['subject'],
        'keywords': book_data['keywords'],
        'cover_image': book_data['cover_image'],
        'texts': book_data['texts'],
        'storage_url': book_data.get('storage_url'),
        'user_id': user['uid'],
        'created_date': firestore.SERVER_TIMESTAMP,
        'public': book_data['public']
    }

    publish_ref.set(book_info)
    return jsonify({'success': True}), 200
