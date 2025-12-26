const API = 'http://localhost:5000/api';
let token = localStorage.getItem('token');
let user = null;

// DOM Elements
const greetingPage = document.getElementById('greetingPage');
const mainContainer = document.getElementById('mainContainer');
const getStartedBtn = document.getElementById('getStartedBtn');
const cityInput = document.getElementById('cityInput');
const searchBtn = document.getElementById('searchBtn');
const weatherContent = document.getElementById('weatherContent');
const bgVideo = document.getElementById('bg-video');

// Weather videos
const videos = {
    'clear': 'clear.mp4',
    'clouds': 'clouds.mp4',
    'rain': 'rain.mp4',
    'thunderstorm': 'thunderstorm.mp4',
    'snow': 'snow.mp4',
    'mist': 'mist.mp4'
};

// Check auth on load
if (token) {
    verifyToken();
}

// Get Started
getStartedBtn.addEventListener('click', () => {
    if (token) {
        showDashboard();
    } else {
        showLogin();
    }
});

// Search
searchBtn.addEventListener('click', searchWeather);
cityInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') searchWeather();
});

function showDashboard() {
    greetingPage.classList.add('fade-out');
    setTimeout(() => {
        greetingPage.style.display = 'none';
        mainContainer.style.display = 'block';
        bgVideo.style.opacity = '1';
        
        if (user) {
            document.getElementById('userInfo').style.display = 'flex';
            document.getElementById('userName').textContent = user.name;
        }
    }, 800);
}

function showLogin() {
    const modal = document.createElement('div');
    modal.className = 'auth-modal show';
    modal.innerHTML = `
        <div class="auth-modal-content">
            <h2>Login</h2>
            <input type="email" id="email" placeholder="Email" class="auth-input">
            <input type="password" id="password" placeholder="Password" class="auth-input">
            <button onclick="login()" class="auth-btn">Login</button>
            <p class="auth-demo">Demo: admin@weather.com / admin123</p>
            <button onclick="closeModal()" class="close-modal">×</button>
        </div>
    `;
    document.body.appendChild(modal);
}

function closeModal() {
    const modal = document.querySelector('.auth-modal');
    if (modal) modal.remove();
}

async function login() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    
    try {
        const res = await fetch(`${API}/auth/login`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({email, password})
        });
        
        const data = await res.json();
        
        if (res.ok) {
            token = data.token;
            user = data.user;
            localStorage.setItem('token', token);
            closeModal();
            showDashboard();
        } else {
            alert(data.error || 'Login failed');
        }
    } catch (err) {
        alert('Error: ' + err.message);
    }
}

async function verifyToken() {
    try {
        const res = await fetch(`${API}/auth/verify`, {
            headers: {'Authorization': `Bearer ${token}`}
        });
        
        if (res.ok) {
            const data = await res.json();
            user = {email: data.email, name: data.email.split('@')[0]};
        } else {
            localStorage.removeItem('token');
            token = null;
        }
    } catch (err) {
        console.error('Verify failed:', err);
    }
}

function logout() {
    localStorage.removeItem('token');
    token = null;
    user = null;
    location.reload();
}

async function searchWeather() {
    const city = cityInput.value.trim();
    
    if (!city) {
        alert('Enter a city');
        return;
    }
    
    if (!token) {
        alert('Please login first');
        showLogin();
        return;
    }
    
    try {
        searchBtn.textContent = 'Loading...';
        searchBtn.disabled = true;
        
        const res = await fetch(`${API}/weather?city=${city}`, {
            headers: {'Authorization': `Bearer ${token}`}
        });
        
        const data = await res.json();
        
        if (res.ok) {
            updateUI(data);
            updateVideo(data.condition);
            weatherContent.style.display = 'grid';
        } else {
            alert(data.error || 'Failed to get weather');
        }
    } catch (err) {
        alert('Error: ' + err.message);
    } finally {
        searchBtn.textContent = 'Search';
        searchBtn.disabled = false;
    }
}

function updateUI(data) {
    document.getElementById('cityName').textContent = `${data.city}, ${data.country}`;
    document.getElementById('mainTemp').textContent = `${data.temp}°`;
    document.getElementById('mainIcon').src = `http://openweathermap.org/img/wn/${data.icon}@4x.png`;
    document.getElementById('weatherDesc').textContent = data.description;
    document.getElementById('weatherNote').textContent = `Current weather in ${data.city}`;
    
    document.getElementById('feelsLike').textContent = `${data.feels_like}°`;
    document.getElementById('precipitation').textContent = `${data.precipitation}"`;
    document.getElementById('visibility').textContent = `${data.visibility} mi`;
    document.getElementById('humidity').textContent = `${data.humidity}%`;
    document.getElementById('dewPoint').textContent = `Dew point: ${data.feels_like - 3}°`;
    
    // Hourly
    const hourlyHTML = data.hourly.map((h, i) => `
        <div class="hourly-item">
            <div class="hourly-time">${i === 0 ? 'Now' : h.time}</div>
            <div class="hourly-temp">${h.temp}°</div>
            <img src="http://openweathermap.org/img/wn/${h.icon}@2x.png">
        </div>
    `).join('');
    document.getElementById('hourlyForecast').innerHTML = hourlyHTML;
    
    // Daily
    const dailyHTML = data.daily.map((d, i) => `
        <div class="daily-item">
            <div class="daily-day">${i === 0 ? 'Today' : d.day}</div>
            <div class="daily-date">${d.date}</div>
            <img src="http://openweathermap.org/img/wn/${d.icon}@2x.png">
            <div class="daily-temp">${d.temp}°</div>
        </div>
    `).join('');
    document.getElementById('dailyForecast').innerHTML = dailyHTML;
    
    document.getElementById('uvIndex').textContent = data.uv_index;
    document.querySelector('.uv-indicator').style.left = `${(data.uv_index / 11) * 100}%`;
    
    document.getElementById('windSpeed').textContent = data.wind_speed;
    document.getElementById('gustSpeed').textContent = Math.round(data.wind_speed * 1.5);
    document.getElementById('compass-line').style.transform = `rotate(${data.wind_deg}deg)`;
}

function updateVideo(condition) {
    const video = videos[condition] || 'clear.mp4';
    const src = `/static/videos/${video}`;
    
    if (bgVideo.src !== src) {
        bgVideo.style.opacity = '0';
        setTimeout(() => {
            bgVideo.src = src;
            bgVideo.load();
            bgVideo.play();
            bgVideo.style.opacity = '1';
        }, 300);
    }
}