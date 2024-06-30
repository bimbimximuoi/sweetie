from flask import Blueprint, request, jsonify, session, redirect, url_for
from .extract_txt import extract_text_from_txt
from .extract_mobi import extract_text_from_mobi, extract_cover_image_from_mobi, extract_mobi_metadata
from .extract_pdf import extract_text_from_pdf, extract_cover_image_from_pdf, extract_pdf_metadata
from .extract_epub import extract_text_from_epub, extract_cover_image_from_epub, extract_epub_metadata
from app.models import Metadata, TextData, to_base64

api_bp = Blueprint('api_bp', __name__)

# This will be assigned in app.py
socketio = None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'txt', 'pdf', 'mobi', 'epub'}

def extract_text(file):
    filename = file.filename.lower()
    if filename.endswith('.txt'):
        return extract_text_from_txt(file, update_progress=extract_progress)
    elif filename.endswith('.pdf'):
        return extract_text_from_pdf(file, update_progress=extract_progress)
    elif filename.endswith('.mobi'):
        return extract_text_from_mobi(file, update_progress=extract_progress)
    elif filename.endswith('.epub'):
        return extract_text_from_epub(file, update_progress=extract_progress)
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

def extract_progress(current, total):
    extract = (current / total) * 100
    if socketio:
        socketio.emit('extract_progress', {'progress': extract})
    print(f"Extract progress: {extract}%")  # Debugging print

@api_bp.route('/extract_book', methods=['POST'])
def extract_book():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        texts = extract_text(file)
        file.seek(0)  # Reset file pointer to the beginning
        cover_image = extract_cover_image(file)
        file.seek(0)  # Reset file pointer to the beginning again
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
            }
        }

        return jsonify(response), 200
    else:
        return jsonify({'error': 'Invalid file format'}), 400
