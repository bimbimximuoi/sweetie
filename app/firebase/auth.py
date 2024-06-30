from flask import Blueprint, request, jsonify, session, current_app
from firebase_admin import auth
import firebase_admin
from firebase_admin import credentials

auth_bp = Blueprint('auth_bp', __name__)

# Initialize Firebase Admin SDK (assuming you've already configured the credentials)
if not firebase_admin._apps:
    cred = credentials.Certificate("path/to/your/serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

@auth_bp.route('/auth/signout', methods=['GET'])
def sign_out():
    session.pop('user', None)
    return jsonify({"success": True}), 200

@auth_bp.route('/auth/signin/email', methods=['POST'])
def signin_with_email_and_password():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    try:
        user = auth.get_user_by_email(email)
        # Assuming you have a custom authentication mechanism to verify password
        if custom_password_verify(user.uid, password):
            session['user'] = {
                'uid': user.uid,
                'email': user.email,
                'name': user.display_name
            }
            return jsonify({"success": True, "uid": user.uid}), 200
        else:
            return jsonify({"success": False, "error": "Invalid credentials"}), 401
    except auth.AuthError:
        return jsonify({"success": False, "error": "User not found"}), 404

@auth_bp.route('/auth/signup/email', methods=['POST'])
def signup_with_email_and_password():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    try:
        user = auth.create_user(
            email=email,
            password=password,
            display_name=name
        )
        session['user'] = {
            'uid': user.uid,
            'email': user.email,
            'name': user.display_name
        }
        return jsonify({"success": True, "uid": user.uid}), 200
    except auth.AuthError as e:
        return jsonify({"success": False, "error": str(e)}), 400

@auth_bp.route('/auth/signin/google', methods=['POST'])
def signin_with_google():
    data = request.get_json()
    id_token = data.get('idToken')
    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        user_info = auth.get_user(uid)

        session['user'] = {
            'uid': uid,
            'email': user_info.email,
            'avatar': user_info.photo_url,
            'name': user_info.display_name
        }

        # Add user to Firestore if not already added
        db = current_app.config['FIRESTORE']
        user_ref = db.collection('users').document(uid)
        if not user_ref.get().exists:
            user_ref.set({
                'uid': uid,
                'email': user_info.email,
                'avatar': user_info.photo_url,
                'name': user_info.display_name
            })

        return jsonify({"success": True, "uid": uid}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 401

@auth_bp.route('/auth/user/detail', methods=['GET'])
def get_user_detail():
    user = session.get('user')
    if user:
        return jsonify({"success": True, "user": user}), 200
    else:
        return jsonify({"success": False, "error": "User not logged in"}), 401

@auth_bp.route('/auth/user/check', methods=['GET'])
def check_login_status():
    if 'user' in session:
        return jsonify({'logged_in': True}), 200
    else:
        return jsonify({'logged_in': False}), 200

# Placeholder for custom password verification function
def custom_password_verify(uid, password):
    # Implement your custom password verification logic here
    # This function should return True if the password is correct, False otherwise
    pass




# @auth_bp.route('/auth/signout', methods=['GET'])
# @auth_bp.route('/auth/signin/email', methods=['GET'])
# @auth_bp.route('/auth/signup/email', methods=['GET'])
# @auth_bp.route('/auth/signin/google', methods=['GET'])
# @auth_bp.route('/auth/user/detail', methods=['GET'])
# @auth_bp.route('/auth/user/check', methods=['GET'])
