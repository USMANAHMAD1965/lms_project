// API Base URL
const API_URL = 'http://localhost:5000/api';

// Helper function for API calls
async function apiCall(endpoint, method = 'GET', data = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json',
        }
    };
    
    const token = localStorage.getItem('access_token');
    if (token) {
        options.headers['Authorization'] = `Bearer ${token}`;
    }
    
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(`${API_URL}${endpoint}`, options);
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'Something went wrong');
        }
        
        return result;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Show alert message
function showAlert(message, type = 'success') {
    const alertDiv = document.getElementById('alert');
    if (alertDiv) {
        alertDiv.textContent = message;
        alertDiv.className = `alert alert-${type}`;
        alertDiv.style.display = 'block';
        setTimeout(() => {
            alertDiv.style.display = 'none';
        }, 3000);
    } else {
        alert(message);
    }
}

// Check authentication status
function checkAuth() {
    const token = localStorage.getItem('access_token');
    const user = localStorage.getItem('user');
    
    if (!token || !user) {
        window.location.href = '/pages/login.html';
        return false;
    }
    
    return true;
}

// Logout function - Fixed
async function logout() {
    try {
        const token = localStorage.getItem('access_token');
        if (token) {
            await fetch(`${API_URL}/auth/logout`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });
        }
    } catch (error) {
        console.error('Logout error:', error);
    } finally {
        // Always clear local storage regardless of API response
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        window.location.href = '/index.html';
    }
}

// Make logout available globally
window.logout = logout;

// Load user profile
async function loadProfile() {
    try {
        const userData = await apiCall('/auth/profile');
        const user = JSON.parse(localStorage.getItem('user'));
        
        if (document.getElementById('profile-name')) {
            document.getElementById('profile-name').textContent = userData.name;
            document.getElementById('profile-email').textContent = userData.email;
            document.getElementById('profile-role').textContent = userData.role;
            document.getElementById('profile-bio').textContent = userData.bio || 'No bio added yet';
            
            // Fill form for editing
            if (document.getElementById('edit-name')) {
                document.getElementById('edit-name').value = userData.name;
                document.getElementById('edit-bio').value = userData.bio || '';
            }
        }
        
    } catch (error) {
        showAlert('Failed to load profile: ' + error.message, 'error');
    }
}

// Update profile
async function updateProfile(event) {
    if (event) event.preventDefault();
    
    const name = document.getElementById('edit-name')?.value;
    const bio = document.getElementById('edit-bio')?.value;
    
    if (!name) return;
    
    try {
        const result = await apiCall('/auth/profile', 'PUT', { name, bio });
        showAlert('Profile updated successfully!');
        setTimeout(() => {
            location.reload();
        }, 1500);
    } catch (error) {
        showAlert('Failed to update profile: ' + error.message, 'error');
    }
}

// Event listeners for auth pages
if (document.getElementById('register-form')) {
    document.getElementById('register-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const name = document.getElementById('name').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const role = document.getElementById('role').value;
        
        try {
            const result = await apiCall('/auth/register', 'POST', {
                name,
                email,
                password,
                role
            });
            
            showAlert('Registration successful! Please login.');
            setTimeout(() => {
                window.location.href = '/pages/login.html';
            }, 2000);
        } catch (error) {
            showAlert(error.message, 'error');
        }
    });
}

if (document.getElementById('login-form')) {
    document.getElementById('login-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        
        try {
            const result = await apiCall('/auth/login', 'POST', {
                email,
                password
            });
            
            localStorage.setItem('access_token', result.access_token);
            localStorage.setItem('user', JSON.stringify(result.user));
            
            showAlert('Login successful!');
            setTimeout(() => {
                window.location.href = '/pages/dashboard.html';
            }, 1000);
        } catch (error) {
            showAlert(error.message, 'error');
        }
    });
}

// Add logout button handler to all pages
document.addEventListener('DOMContentLoaded', function() {
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            logout();
        });
    }
});