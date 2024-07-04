from flask import Flask
import os
import firebase_admin
from firebase_admin import credentials, firestore, storage
from flask_session import Session
from flask_socketio import SocketIO
from flask_cors import CORS
socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.secret_key = os.urandom(24)

    


  # Configure server-side session
    app.config['SESSION_TYPE'] = 'filesystem'  # Using the file system to store sessions
    app.config['SESSION_FILE_DIR'] = './.flask_session/'  # Directory to store session files
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_USE_SIGNER'] = True
    app.config['SESSION_KEY_PREFIX'] = 'session:'
    Session(app)





    # Initialize Firebase Admin SDK
    cred = credentials.Certificate(os.path.join(os.getcwd(), 'serviceAccountKey.json'))
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'pthuy-50c34.appspot.com'
    })
    
    # Initialize Firestore and Storage
    app.config['FIRESTORE'] = firestore.client()
    app.config['STORAGE'] = storage.bucket()

    # Register blueprints
    from .routes import main_bp
    from .firebase.auth import auth_bp
    from .firebase.firestore import firestore_bp
    from .firebase.storage import storage_bp
    from .service.tts import speech_bp
    from .service.tsl import translate_bp
    from .service.extract import extract_bp
    from .service.book import book_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(firestore_bp)
    app.register_blueprint(storage_bp)
    app.register_blueprint(speech_bp)
    app.register_blueprint(translate_bp)

    app.register_blueprint(extract_bp)
    app.register_blueprint(book_bp)

    socketio.init_app(app)
    return app
