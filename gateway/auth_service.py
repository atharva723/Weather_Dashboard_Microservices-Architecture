from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

SECRET_KEY = 'weather-dashboard-secret-2024'

# Simple user database
users = {
    'admin@weather.com': {
        'password': generate_password_hash('admin123'),
        'name': 'Admin User'
    }
}

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'auth'}), 200

@app.route('/auth/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    
    if email in users:
        return jsonify({'error': 'User exists'}), 409
    
    users[email] = {
        'password': generate_password_hash(password),
        'name': name
    }
    
    return jsonify({'message': 'User registered', 'email': email}), 201

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    user = users.get(email)
    if not user or not check_password_hash(user['password'], password):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    token = jwt.encode({
        'email': email,
        'name': user['name'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, SECRET_KEY)
    
    return jsonify({
        'token': token,
        'user': {'email': email, 'name': user['name']}
    }), 200

@app.route('/auth/verify', methods=['GET'])
def verify():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return jsonify({'valid': True, 'email': data['email']}), 200
    except:
        return jsonify({'error': 'Invalid token'}), 401

if __name__ == '__main__':
    print('\n' + '='*50)
    print('🔐 AUTH SERVICE STARTED')
    print('='*50)
    print('Running on: http://localhost:5001')
    print('='*50 + '\n')
    app.run(port=5001, debug=True, threaded=True)