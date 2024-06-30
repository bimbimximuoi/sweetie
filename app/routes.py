from flask import Blueprint, render_template, session, redirect, url_for, current_app, jsonify, flash

main_bp = Blueprint('main_bp', __name__)

@main_bp.route('/')
def welcome():
    return render_template('flowbite.html')

@main_bp.route('/base')
def base():
    return render_template('base.html')

@main_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@main_bp.route('/signin')
def signin():
    return render_template('signin.html')

@main_bp.route('/signup')
def signup():
    return render_template('signup.html')

@main_bp.route('/detail')
def detail():
    return render_template('detail.html')

@main_bp.route('/book')
def book():
    return render_template('book.html')


@main_bp.route('/book/publish', methods=['GET'])
def book_publish():
    book_data = session.get('book_data')
    if not book_data:
        return redirect(url_for('main_bp.book'))
    return render_template('book-publish.html', book_data=book_data)


@main_bp.route('/book/detail', methods=['GET'])
def book_detail():
    book_data = session.get('book_data')
    if not book_data:
        return redirect(url_for('main_bp.book'))
    return render_template('book-detail.html', book_data=book_data)

@main_bp.route('/book/translate', methods=['GET'])
def book_translate():
    book_data = session.get('book_data')
    if not book_data:
        return redirect(url_for('main_bp.book'))
    return render_template('book-translate.html', book_data=book_data)

@main_bp.route('/book/speech', methods=['GET'])
def book_speech():
    book_data = session.get('book_data')
    if not book_data:
        return redirect(url_for('main_bp.book'))
    return render_template('book-speech.html', book_data=book_data)


@main_bp.route('/book/upload', methods=['GET'])
def book_upload():
    book_data = session.get('book_data')
    user_id = session.get('user')['uid'] if 'user' in session else None
    if not book_data:
        return redirect(url_for('main_bp.book'))
    if not user_id:
        flash('Please sign in to upload to cloud')
        return redirect(url_for('main_bp.signin'))  # Redirect to sign in if user is not logged in
    return render_template('book-upload.html', book_data=book_data, user_id=user_id)

@main_bp.route('/book/read', methods=['GET'])
def book_read():
    book_data = session.get('book_data')
    if not book_data:
        return redirect(url_for('main_bp.book'))
    return render_template('book-read.html', book_data=book_data)

@main_bp.route('/book/load/<book_id>', methods=['GET'])
def book_load(book_id):
    db = current_app.config['FIRESTORE']
    book_ref = db.collection('published_books').document(book_id)
    book_doc = book_ref.get()

    if book_doc.exists:
        book_data = book_doc.to_dict().get('book_data', {})
        # Transform the data structure to include metadata
        transformed_book_data = {
            'metadata': {
                'title': book_data.get('metadata', {}).get('title', 'Unknown Title'),
                'authors': book_data.get('metadata', {}).get('authors', ['Unknown Authors']),
                'subject': book_data.get('metadata', {}).get('subject', 'Unknown Subject'),
                'keywords': book_data.get('metadata', {}).get('keywords', 'Unknown Keywords'),
            },
            'cover_image': book_data.get('cover_image', 'None'),
            'texts': book_data.get('texts', {}),
            'storage_url': book_data.get('storage_url', ''),
            'user_id': book_data.get('user_id', 'Unknown User'),
            'created_date': book_data.get('created_date', 'Unknown Date'),
            'public': book_data.get('public', False)
        }
        session['book_data'] = transformed_book_data
        return redirect(url_for('main_bp.book_read'))
    else:
        return jsonify({'error': 'Book not found'}), 404



@main_bp.route('/user', methods=['GET'])
@main_bp.route('/user/<identifier>', methods=['GET'])
def user(identifier=None):
    db = current_app.config['FIRESTORE']

    # Get current user id from session if identifier is not provided
    if identifier is None:
        user_data = session.get('user')
        if not user_data:
            return redirect(url_for('main_bp.signin'))
        user_id = user_data['uid']
    else:
        # Determine if identifier is an email or user_id
        if '@' in identifier:
            # Fetch user by email
            users_ref = db.collection('users').where('email', '==', identifier)
            user_docs = users_ref.stream()
            user_doc = next(user_docs, None)  # Get the first matching document
            if not user_doc:
                return jsonify({'error': 'User not found'}), 404
            user_id = user_doc.id
            user_data = user_doc.to_dict()
        else:
            # Fetch user by user_id
            user_ref = db.collection('users').document(identifier)
            user_doc = user_ref.get()
            if not user_doc.exists:
                return jsonify({'error': 'User not found'}), 404
            user_id = identifier
            user_data = user_doc.to_dict()

    # Fetch user's published books
    published_books_ref = db.collection('published_books').where('user_id', '==', user_id)
    published_books_docs = published_books_ref.stream()
    published_books = []
    for doc in published_books_docs:
        book_data = doc.to_dict().get('book_data', {})
        book_data['id'] = doc.id
        if 'metadata' not in book_data:
            book_data['metadata'] = {}  # Ensure metadata exists
        published_books.append(book_data)
        
    # Fetch user's books
    books_ref = db.collection('books').where('user_id', '==', user_id)
    books_docs = books_ref.stream()
    books = []
    for doc in books_docs:
        book_data = doc.to_dict().get('book_data', {})
        book_data['id'] = doc.id  # Add the document ID
        if 'metadata' not in book_data:
            book_data['metadata'] = {}  # Ensure metadata exists
        books.append(book_data)

    # Fetch user's files from storage
    bucket = current_app.config['STORAGE']
    blobs = bucket.list_blobs(prefix=f"users/{user_id}/books/")
    user_files = [blob.name for blob in blobs]

    return render_template('user.html', user_data=user_data, published_books=published_books, books=books, user_files=user_files)




@main_bp.route('/community/books', methods=['GET'])
def community_books():
    db = current_app.config['FIRESTORE']
    published_books_ref = db.collection('published_books')
    books = []

    # Fetch all published books
    docs = published_books_ref.stream()
    for doc in docs:
        book_data = doc.to_dict()
        book_data['id'] = doc.id  # Include the document ID
        books.append(book_data)

    return render_template('community-books.html', books=books)


