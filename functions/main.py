from flask import Flask, render_template, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify('hello bbi')

@app.route('/<path:path>')
def catch_all(path):
    return jsonify('hello bbi')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)


# from app import create_app, socketio

# app = create_app()

# if __name__ == '__main__':
#     socketio.run(app, port=4000, debug=True)

