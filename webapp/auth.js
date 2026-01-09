// Authentication Page JavaScript

// In local development, enable mock testing mode
const IS_DEV_ENV = (typeof window !== 'undefined') &&
    (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');
const MOCK_MODE = IS_DEV_ENV; // Enable mock mode in dev

class AuthPage {
    constructor() {
        this.currentTab = 'phone';
        this.verificationId = null;
        this.mockMode = MOCK_MODE;
        this.init();
    }
    
    init() {
        // Show mock mode indicator
        if (this.mockMode) {
            this.showMockModeIndicator();
        }

        this.setupTabs();
        this.setupPhoneAuth();
        this.setupEmailAuth();
        this.setupOAuthMock();
        this.checkExistingSession();
    }
    
    showMockModeIndicator() {
        // Show indicator in header
        const headerIndicator = document.getElementById('mockModeIndicator');
        if (headerIndicator) {
            headerIndicator.style.display = 'block';
        }
        
        // Also show floating indicator
        const indicator = document.createElement('div');
        indicator.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            background: rgba(255, 193, 7, 0.2);
            border: 1px solid rgba(255, 193, 7, 0.5);
            color: #ffc107;
            padding: 8px 16px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
            z-index: 10000;
            font-family: monospace;
        `;
        indicator.textContent = '🧪 MOCK MODE';
        document.body.appendChild(indicator);
    }
    
    checkExistingSession() {
        // Check if user is already logged in
        // In mock mode, allow viewing auth page even if logged in
        // (users can test different accounts or see the UI)
        const userId = localStorage.getItem('thesidia_user_id');
        const sessionId = localStorage.getItem('thesidia_session_id');
        
        if (userId && sessionId && !this.mockMode) {
            // Only redirect in production mode if already logged in
            window.location.href = '/';
        } else if (userId && sessionId && this.mockMode) {
            // In mock mode, show a message that user is logged in
            const existingSessionMsg = document.createElement('div');
            existingSessionMsg.style.cssText = `
                background: rgba(0, 255, 0, 0.1);
                border: 1px solid rgba(0, 255, 0, 0.3);
                color: #00ff00;
                padding: 12px;
                margin-bottom: 16px;
                border-radius: 4px;
                font-size: 13px;
            `;
            existingSessionMsg.innerHTML = `
                ✓ You're already logged in (User: ${userId.substring(0, 12)}...)
                <br><small>You can sign in with a different account or continue to <a href="/" style="color: #00ff00; text-decoration: underline;">main app</a></small>
            `;
            const errorMsg = document.getElementById('errorMessage');
            if (errorMsg && errorMsg.parentNode) {
                errorMsg.parentNode.insertBefore(existingSessionMsg, errorMsg);
            }
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
                    
                    // In mock mode, show the code
                    if (this.mockMode && data.mock_code) {
                        this.showSuccess(`Verification code sent! Mock code: ${data.mock_code} (check console)`);
                        console.log(`📱 MOCK SMS CODE for ${fullPhone}: ${data.mock_code}`);
                    } else {
                        this.showSuccess('Verification code sent!');
                    }
                    
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
                // Try login first
                let response = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password })
                });
                
                let data = await response.json();
                
                // If login fails, try registration (in mock mode)
                if (!data.user_id && response.status === 401) {
                    if (this.mockMode) {
                        // Try to register
                        response = await fetch('/api/auth/register', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ email, password })
                        });
                        data = await response.json();
                    }
                }
                
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
    
    setupOAuthMock() {
        if (!this.mockMode) return;
        
        // In mock mode, intercept OAuth buttons and show mock flow
        const oauthButtons = document.querySelectorAll('.social-btn');
        oauthButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const provider = btn.id.replace('Btn', '').replace('google', 'Google').replace('twitter', 'Twitter').replace('github', 'GitHub').replace('apple', 'Apple');
                this.showSuccess(`🧪 Mock OAuth: ${provider} login would proceed here. In production, this redirects to ${provider}.`);
                
                // Simulate OAuth success after a delay
                setTimeout(() => {
                    // Create a mock user session
                    const mockUserId = `user_${Date.now()}`;
                    const mockSessionId = `session_${Date.now()}`;
                    localStorage.setItem('thesidia_user_id', mockUserId);
                    localStorage.setItem('thesidia_session_id', mockSessionId);
                    localStorage.setItem('thesidia_oauth_provider', provider.toLowerCase());
                    window.location.href = '/';
                }, 1500);
            });
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

