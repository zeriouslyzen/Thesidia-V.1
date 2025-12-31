// Authentication Page JavaScript

// In local development, we want to disable the login flow entirely and
// just bounce users back into the main app. This keeps production auth
// behavior intact while removing friction during dev.
const IS_DEV_ENV = (typeof window !== 'undefined') &&
    (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');

class AuthPage {
    constructor() {
        this.currentTab = 'phone';
        this.verificationId = null;
        this.init();
    }
    
    init() {
        // If running on localhost, skip the auth UI and return to app
        if (IS_DEV_ENV) {
            window.location.href = '/';
            return;
        }

        this.setupTabs();
        this.setupPhoneAuth();
        this.setupEmailAuth();
        this.checkExistingSession();
    }
    
    checkExistingSession() {
        // Check if user is already logged in
        const userId = localStorage.getItem('thesidia_user_id');
        const sessionId = localStorage.getItem('thesidia_session_id');
        
        if (userId && sessionId) {
            // Redirect to main app
            window.location.href = '/';
        }
    }
    
    setupTabs() {
        const tabs = document.querySelectorAll('.auth-tab');
        const forms = document.querySelectorAll('.auth-form');
        
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const tabName = tab.dataset.tab;
                
                // Update active tab
                tabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                
                // Update active form
                forms.forEach(f => f.classList.remove('active'));
                document.getElementById(`${tabName}Form`).classList.add('active');
                
                this.currentTab = tabName;
                this.hideMessages();
            });
        });
    }
    
    setupPhoneAuth() {
        const sendCodeBtn = document.getElementById('sendCodeBtn');
        const verifyCodeBtn = document.getElementById('verifyCodeBtn');
        const resendCodeBtn = document.getElementById('resendCodeBtn');
        const phoneForm = document.getElementById('phoneForm');
        
        sendCodeBtn.addEventListener('click', async () => {
            const countryCode = document.getElementById('countryCode').value;
            const phoneNumber = document.getElementById('phoneNumber').value;
            
            if (!phoneNumber) {
                this.showError('Please enter a phone number');
                return;
            }
            
            const fullPhone = countryCode + phoneNumber.replace(/\D/g, '');
            
            sendCodeBtn.disabled = true;
            sendCodeBtn.innerHTML = '<span class="loading-spinner"></span>Sending...';
            
            try {
                const response = await fetch('/api/auth/phone/send', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ phone: fullPhone })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    this.verificationId = data.verification_id;
                    this.showSuccess('Verification code sent!');
                    
                    // Show verification input
                    document.getElementById('verificationGroup').style.display = 'block';
                    sendCodeBtn.style.display = 'none';
                    verifyCodeBtn.style.display = 'block';
                    document.getElementById('verificationCode').focus();
                } else {
                    this.showError(data.error || 'Failed to send verification code');
                    sendCodeBtn.disabled = false;
                    sendCodeBtn.textContent = 'Send Verification Code';
                }
            } catch (error) {
                this.showError('Network error. Please try again.');
                sendCodeBtn.disabled = false;
                sendCodeBtn.textContent = 'Send Verification Code';
            }
        });
        
        resendCodeBtn.addEventListener('click', async () => {
            const countryCode = document.getElementById('countryCode').value;
            const phoneNumber = document.getElementById('phoneNumber').value;
            const fullPhone = countryCode + phoneNumber.replace(/\D/g, '');
            
            resendCodeBtn.disabled = true;
            resendCodeBtn.textContent = 'Sending...';
            
            try {
                const response = await fetch('/api/auth/phone/send', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ phone: fullPhone })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    this.verificationId = data.verification_id;
                    this.showSuccess('New code sent!');
                } else {
                    this.showError(data.error || 'Failed to resend code');
                }
            } catch (error) {
                this.showError('Network error. Please try again.');
            } finally {
                resendCodeBtn.disabled = false;
                resendCodeBtn.textContent = 'Resend';
            }
        });
        
        phoneForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const code = document.getElementById('verificationCode').value;
            
            if (!code || code.length !== 6) {
                this.showError('Please enter the 6-digit verification code');
                return;
            }
            
            verifyCodeBtn.disabled = true;
            verifyCodeBtn.innerHTML = '<span class="loading-spinner"></span>Verifying...';
            
            try {
                const response = await fetch('/api/auth/phone/verify', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        verification_id: this.verificationId,
                        code: code
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // Store session
                    localStorage.setItem('thesidia_user_id', data.user_id);
                    localStorage.setItem('thesidia_session_id', data.session_id);
                    
                    // Redirect to app
                    window.location.href = '/';
                } else {
                    this.showError(data.error || 'Invalid verification code');
                    verifyCodeBtn.disabled = false;
                    verifyCodeBtn.textContent = 'Verify & Sign In';
                }
            } catch (error) {
                this.showError('Network error. Please try again.');
                verifyCodeBtn.disabled = false;
                verifyCodeBtn.textContent = 'Verify & Sign In';
            }
        });
    }
    
    setupEmailAuth() {
        const emailForm = document.getElementById('emailForm');
        const emailSubmitBtn = document.getElementById('emailSubmitBtn');
        
        emailForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const email = document.getElementById('emailInput').value;
            const password = document.getElementById('passwordInput').value;
            
            if (!email || !password) {
                this.showError('Please enter email and password');
                return;
            }
            
            emailSubmitBtn.disabled = true;
            emailSubmitBtn.innerHTML = '<span class="loading-spinner"></span>Signing in...';
            
            try {
                const response = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password })
                });
                
                const data = await response.json();
                
                if (data.user_id) {
                    // Store session
                    localStorage.setItem('thesidia_user_id', data.user_id);
                    localStorage.setItem('thesidia_session_id', data.session_id);
                    if (data.token) {
                        localStorage.setItem('thesidia_token', data.token);
                    }
                    
                    // Redirect to app
                    window.location.href = '/';
                } else {
                    this.showError(data.error || 'Invalid email or password');
                    emailSubmitBtn.disabled = false;
                    emailSubmitBtn.textContent = 'Sign In';
                }
            } catch (error) {
                this.showError('Network error. Please try again.');
                emailSubmitBtn.disabled = false;
                emailSubmitBtn.textContent = 'Sign In';
            }
        });
    }
    
    showError(message) {
        const errorEl = document.getElementById('errorMessage');
        errorEl.textContent = message;
        errorEl.classList.add('show');
        
        const successEl = document.getElementById('successMessage');
        successEl.classList.remove('show');
        
        setTimeout(() => {
            errorEl.classList.remove('show');
        }, 5000);
    }
    
    showSuccess(message) {
        const successEl = document.getElementById('successMessage');
        successEl.textContent = message;
        successEl.classList.add('show');
        
        const errorEl = document.getElementById('errorMessage');
        errorEl.classList.remove('show');
        
        setTimeout(() => {
            successEl.classList.remove('show');
        }, 3000);
    }
    
    hideMessages() {
        document.getElementById('errorMessage').classList.remove('show');
        document.getElementById('successMessage').classList.remove('show');
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new AuthPage();
    });
} else {
    new AuthPage();
}

