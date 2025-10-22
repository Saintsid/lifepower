const API_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:8002/api' 
    : '/api';

function getToken() {
    return localStorage.getItem('token');
}

function saveToken(token) {
    localStorage.setItem('token', token);
}

function removeToken() {
    localStorage.removeItem('token');
}

async function apiRequest(endpoint, options = {}) {
    const token = getToken();
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    const response = await fetch(`${API_URL}${endpoint}`, {
        ...options,
        headers
    });
    
    // Не делаем редирект на login, если уже на странице входа
    if (response.status === 401) {
        const currentPath = window.location.pathname;
        if (currentPath !== '/login.html' && currentPath !== '/register.html') {
            removeToken();
            window.location.href = '/login.html';
        }
    }
    
    return response;
}

async function getCurrentUser() {
    const token = getToken();
    if (!token) return null;
    
    try {
        const response = await apiRequest('/me');
        if (response.ok) {
            return await response.json();
        }
    } catch (e) {
        console.error('Failed to get current user', e);
    }
    return null;
}

function logout() {
    removeToken();
    window.location.href = '/login.html';
}

