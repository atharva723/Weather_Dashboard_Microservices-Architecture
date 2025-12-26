from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

AUTH_URL = 'http://localhost:5001'
WEATHER_URL = 'http://localhost:5002'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'gateway'}), 200

# AUTH ROUTES
@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        resp = requests.post(f'{AUTH_URL}/auth/register', json=request.json, timeout=5)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({'error': 'Auth service unavailable'}), 503

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        resp = requests.post(f'{AUTH_URL}/auth/login', json=request.json, timeout=5)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({'error': 'Auth service unavailable'}), 503

@app.route('/api/auth/verify', methods=['GET'])
def verify():
    try:
        token = request.headers.get('Authorization', '')
        resp = requests.get(f'{AUTH_URL}/auth/verify', headers={'Authorization': token}, timeout=5)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({'error': 'Auth service unavailable'}), 503

# WEATHER ROUTE
@app.route('/api/weather', methods=['GET'])
def weather():
    # Check auth
    token = request.headers.get('Authorization', '')
    if not token:
        return jsonify({'error': 'No token'}), 401
    
    try:
        # Verify token
        auth_resp = requests.get(f'{AUTH_URL}/auth/verify', headers={'Authorization': token}, timeout=5)
        if auth_resp.status_code != 200:
            return jsonify({'error': 'Invalid token'}), 401
        
        # Get weather
        city = request.args.get('city')
        weather_resp = requests.get(f'{WEATHER_URL}/weather?city={city}', timeout=10)
        return jsonify(weather_resp.json()), weather_resp.status_code
        
    except requests.exceptions.ConnectionError:
        return jsonify({'error': 'Service unavailable'}), 503
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print('\n' + '='*50)
    print('🚪 API GATEWAY STARTED')
    print('='*50)
    print('Running on: http://localhost:5000')
    print(f'Auth Service: {AUTH_URL}')
    print(f'Weather Service: {WEATHER_URL}')
    print('='*50 + '\n')
    app.run(port=5000, debug=True, threaded=True)