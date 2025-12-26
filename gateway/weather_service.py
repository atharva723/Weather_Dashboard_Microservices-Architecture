from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from datetime import datetime

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

WEATHER_CODES = {
    0: {'name': 'Clear', 'icon': '01d', 'video': 'clear'},
    1: {'name': 'Clear', 'icon': '02d', 'video': 'clear'},
    2: {'name': 'Clouds', 'icon': '03d', 'video': 'clouds'},
    3: {'name': 'Clouds', 'icon': '04d', 'video': 'clouds'},
    45: {'name': 'Mist', 'icon': '50d', 'video': 'mist'},
    48: {'name': 'Mist', 'icon': '50d', 'video': 'mist'},
    51: {'name': 'Drizzle', 'icon': '09d', 'video': 'rain'},
    53: {'name': 'Drizzle', 'icon': '09d', 'video': 'rain'},
    55: {'name': 'Drizzle', 'icon': '09d', 'video': 'rain'},
    61: {'name': 'Rain', 'icon': '10d', 'video': 'rain'},
    63: {'name': 'Rain', 'icon': '10d', 'video': 'rain'},
    65: {'name': 'Rain', 'icon': '10d', 'video': 'rain'},
    71: {'name': 'Snow', 'icon': '13d', 'video': 'snow'},
    73: {'name': 'Snow', 'icon': '13d', 'video': 'snow'},
    75: {'name': 'Snow', 'icon': '13d', 'video': 'snow'},
    80: {'name': 'Rain', 'icon': '09d', 'video': 'rain'},
    81: {'name': 'Rain', 'icon': '09d', 'video': 'rain'},
    82: {'name': 'Rain', 'icon': '09d', 'video': 'rain'},
    95: {'name': 'Thunderstorm', 'icon': '11d', 'video': 'thunderstorm'},
    96: {'name': 'Thunderstorm', 'icon': '11d', 'video': 'thunderstorm'},
}

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'weather'}), 200

@app.route('/weather', methods=['GET'])
def get_weather():
    city = request.args.get('city')
    
    if not city:
        return jsonify({'error': 'City required'}), 400
    
    try:
        # Get coordinates
        geo_url = f'https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1'
        geo_resp = requests.get(geo_url, timeout=5)
        geo_data = geo_resp.json()
        
        if 'results' not in geo_data:
            return jsonify({'error': 'City not found'}), 404
        
        loc = geo_data['results'][0]
        lat = loc['latitude']
        lon = loc['longitude']
        
        # Get weather
        weather_url = f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m,wind_direction_10m&hourly=temperature_2m,weather_code&daily=temperature_2m_max,weather_code,uv_index_max&timezone=auto'
        
        weather_resp = requests.get(weather_url, timeout=5)
        weather_data = weather_resp.json()
        
        current = weather_data['current']
        code = current['weather_code']
        info = WEATHER_CODES.get(code, WEATHER_CODES[0])
        
        # Build response
        result = {
            'city': loc['name'],
            'country': loc.get('country', ''),
            'temp': round(current['temperature_2m']),
            'feels_like': round(current['apparent_temperature']),
            'description': info['name'],
            'humidity': current['relative_humidity_2m'],
            'visibility': 10,
            'wind_speed': round(current['wind_speed_10m'] * 0.621371),
            'wind_deg': current['wind_direction_10m'],
            'precipitation': round(current['precipitation'] * 0.0393701, 2),
            'icon': info['icon'],
            'condition': info['video'],
            'uv_index': round(weather_data['daily']['uv_index_max'][0])
        }
        
        # Hourly
        result['hourly'] = []
        for i in range(min(6, len(weather_data['hourly']['time']))):
            h_code = weather_data['hourly']['weather_code'][i]
            h_info = WEATHER_CODES.get(h_code, WEATHER_CODES[0])
            result['hourly'].append({
                'time': datetime.fromisoformat(weather_data['hourly']['time'][i]).strftime('%H:%M'),
                'temp': round(weather_data['hourly']['temperature_2m'][i]),
                'icon': h_info['icon']
            })
        
        # Daily
        result['daily'] = []
        for i in range(min(6, len(weather_data['daily']['time']))):
            d_code = weather_data['daily']['weather_code'][i]
            d_info = WEATHER_CODES.get(d_code, WEATHER_CODES[0])
            date_obj = datetime.fromisoformat(weather_data['daily']['time'][i])
            result['daily'].append({
                'day': date_obj.strftime('%a'),
                'date': date_obj.strftime('%d/%m'),
                'temp': round(weather_data['daily']['temperature_2m_max'][i]),
                'icon': d_info['icon']
            })
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f'Error: {e}')
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print('\n' + '='*50)
    print('🌤️  WEATHER SERVICE STARTED')
    print('='*50)
    print('Running on: http://localhost:5002')
    print('='*50 + '\n')
    app.run(port=5002, debug=True, threaded=True)