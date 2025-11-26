// Settings Page JavaScript
// Handles form submission, validation, and real-time updates

class SettingsPage {
    constructor(pageType) {
        this.pageType = pageType; // 'account', 'security', 'privacy', 'notifications', 'content', 'advanced'
        this.userId = null;
        this.sessionId = null;
        this.settings = null;
        this.init();
    }
    
    async init() {
        // Get user session
        await this.loadUserSession();
        
        // Load settings
        await this.loadSettings();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Populate form
        this.populateForm();
    }
    
    async loadUserSession() {
        try {
            this.sessionId = localStorage.getItem('thesidia_session_id');
            this.userId = localStorage.getItem('thesidia_user_id');
            
            if (!this.sessionId) {
                const response = await fetch('/api/user/session', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({})
                });
                const data = await response.json();
                this.userId = data.user_id;
                this.sessionId = data.session_id;
                localStorage.setItem('thesidia_session_id', this.sessionId);
                localStorage.setItem('thesidia_user_id', this.userId);
            }
        } catch (error) {
            console.error('Error loading user session:', error);
        }
    }
    
    async loadSettings() {
        try {
            const response = await fetch(`/api/settings?user_id=${this.userId}&session_id=${this.sessionId}`);
            if (response.ok) {
                this.settings = await response.json();
            }
        } catch (error) {
            console.error('Error loading settings:', error);
        }
    }
    
    setupEventListeners() {
        // Account page
        if (this.pageType === 'account') {
            const saveBtn = document.getElementById('saveBtn');
            if (saveBtn) {
                saveBtn.addEventListener('click', () => this.saveAccountSettings());
            }
            
            const avatarInput = document.getElementById('avatarInput');
            if (avatarInput) {
                avatarInput.addEventListener('change', (e) => this.handleAvatarUpload(e));
            }
            
            const bioTextarea = document.getElementById('bio');
            if (bioTextarea) {
                bioTextarea.addEventListener('input', () => this.updateCharCount());
            }
        }
        
        // Security page
        if (this.pageType === 'security') {
            const changePasswordBtn = document.getElementById('changePasswordBtn');
            if (changePasswordBtn) {
                changePasswordBtn.addEventListener('click', () => this.changePassword());
            }
            
            const newPasswordInput = document.getElementById('newPassword');
            if (newPasswordInput) {
                newPasswordInput.addEventListener('input', () => this.checkPasswordStrength());
            }
            
            const deleteAccountBtn = document.getElementById('deleteAccountBtn');
            if (deleteAccountBtn) {
                deleteAccountBtn.addEventListener('click', () => this.deleteAccount());
            }
            
            const twoFactorEnabled = document.getElementById('twoFactorEnabled');
            if (twoFactorEnabled) {
                twoFactorEnabled.addEventListener('change', () => this.toggleTwoFactor());
            }
        }
        
        // Privacy page
        if (this.pageType === 'privacy') {
            const savePrivacyBtn = document.getElementById('savePrivacyBtn');
            if (savePrivacyBtn) {
                savePrivacyBtn.addEventListener('click', () => this.savePrivacySettings());
            }
            
            const blockUserBtn = document.getElementById('blockUserBtn');
            if (blockUserBtn) {
                blockUserBtn.addEventListener('click', () => this.blockUser());
            }
            
            const muteUserBtn = document.getElementById('muteUserBtn');
            if (muteUserBtn) {
                muteUserBtn.addEventListener('click', () => this.muteUser());
            }
        }
        
        // Notifications page
        if (this.pageType === 'notifications') {
            const saveNotificationsBtn = document.getElementById('saveNotificationsBtn');
            if (saveNotificationsBtn) {
                saveNotificationsBtn.addEventListener('click', () => this.saveNotificationSettings());
            }
        }
        
        // Content page
        if (this.pageType === 'content') {
            const saveContentBtn = document.getElementById('saveContentBtn');
            if (saveContentBtn) {
                saveContentBtn.addEventListener('click', () => this.saveContentSettings());
            }
        }
        
        // Advanced page
        if (this.pageType === 'advanced') {
            const exportDataBtn = document.getElementById('exportDataBtn');
            if (exportDataBtn) {
                exportDataBtn.addEventListener('click', () => this.exportData());
            }
        }
    }
    
    populateForm() {
        if (!this.settings) return;
        
        // Account page
        if (this.pageType === 'account') {
            const username = document.getElementById('username');
            const email = document.getElementById('email');
            const phoneNumber = document.getElementById('phoneNumber');
            const displayName = document.getElementById('displayName');
            const bio = document.getElementById('bio');
            const location = document.getElementById('location');
            const website = document.getElementById('website');
            const avatarPreview = document.getElementById('avatarPreview');
            
            if (username) username.value = this.settings.account?.username || '';
            if (email) email.value = this.settings.account?.email || '';
            if (phoneNumber) phoneNumber.value = this.settings.account?.phone_number || '';
            if (displayName) displayName.value = this.settings.account?.display_name || '';
            if (bio) bio.value = this.settings.account?.bio || '';
            if (location) location.value = this.settings.account?.location || '';
            if (website) website.value = this.settings.account?.website || '';
            if (avatarPreview && this.settings.account?.avatar_url) {
                avatarPreview.src = this.settings.account.avatar_url;
            }
            
            this.updateCharCount();
        }
        
        // Privacy page
        if (this.pageType === 'privacy') {
            const profileVisibility = document.getElementById('profileVisibility');
            const privateAccount = document.getElementById('privateAccount');
            const showOnlineStatus = document.getElementById('showOnlineStatus');
            const dmEnabled = document.getElementById('dmEnabled');
            
            if (profileVisibility) profileVisibility.value = this.settings.privacy?.profile_visibility || 'public';
            if (privateAccount) privateAccount.checked = this.settings.privacy?.private_account ?? false;
            if (showOnlineStatus) showOnlineStatus.checked = this.settings.privacy?.show_online_status ?? true;
            if (dmEnabled) dmEnabled.checked = this.settings.privacy?.dm_enabled ?? true;
            
            // Load blocked and muted users
            this.loadBlockedUsers();
            this.loadMutedUsers();
        }
        
        // Notifications page
        if (this.pageType === 'notifications') {
            const emailEnabled = document.getElementById('emailEnabled');
            const pushEnabled = document.getElementById('pushEnabled');
            const mentionsEnabled = document.getElementById('mentionsEnabled');
            const followsEnabled = document.getElementById('followsEnabled');
            const likesEnabled = document.getElementById('likesEnabled');
            const commentsEnabled = document.getElementById('commentsEnabled');
            const repostsEnabled = document.getElementById('repostsEnabled');
            
            if (emailEnabled) emailEnabled.checked = this.settings.notifications?.email_enabled ?? false;
            if (pushEnabled) pushEnabled.checked = this.settings.notifications?.push_enabled ?? true;
            if (mentionsEnabled) mentionsEnabled.checked = this.settings.notifications?.mentions ?? true;
            if (followsEnabled) followsEnabled.checked = this.settings.notifications?.follows ?? true;
            if (likesEnabled) likesEnabled.checked = this.settings.notifications?.likes ?? true;
            if (commentsEnabled) commentsEnabled.checked = this.settings.notifications?.comments ?? true;
            if (repostsEnabled) repostsEnabled.checked = this.settings.notifications?.reposts ?? false;
        }
        
        // Content page
        if (this.pageType === 'content') {
            const autoPlayVideos = document.getElementById('autoPlayVideos');
            const contentFilter = document.getElementById('contentFilter');
            const language = document.getElementById('language');
            const timezone = document.getElementById('timezone');
            
            if (autoPlayVideos) autoPlayVideos.checked = this.settings.content?.auto_play_videos ?? false;
            if (contentFilter) contentFilter.value = this.settings.content?.content_filter || 'moderate';
            if (language) language.value = this.settings.content?.language || 'en';
            if (timezone) timezone.value = this.settings.content?.timezone || 'UTC';
        }
    }
    
    async saveAccountSettings() {
        const username = document.getElementById('username')?.value || '';
        const email = document.getElementById('email')?.value || '';
        const phoneNumber = document.getElementById('phoneNumber')?.value || '';
        const displayName = document.getElementById('displayName')?.value || '';
        const bio = document.getElementById('bio')?.value || '';
        const location = document.getElementById('location')?.value || '';
        const website = document.getElementById('website')?.value || '';
        
        try {
            const response = await fetch('/api/settings/account', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: this.userId,
                    session_id: this.sessionId,
                    username: username,
                    email: email,
                    phone_number: phoneNumber,
                    display_name: displayName,
                    bio: bio,
                    location: location,
                    website: website
                })
            });
            
            if (response.ok) {
                this.showSuccess('Account settings saved successfully!');
                await this.loadSettings();
            } else {
                const error = await response.json();
                this.showError(error.error || 'Failed to save settings');
            }
        } catch (error) {
            this.showError('Error saving settings: ' + error.message);
        }
    }
    
    async changePassword() {
        const currentPassword = document.getElementById('currentPassword')?.value || '';
        const newPassword = document.getElementById('newPassword')?.value || '';
        const confirmPassword = document.getElementById('confirmPassword')?.value || '';
        
        if (!currentPassword || !newPassword) {
            this.showError('Please fill in all password fields');
            return;
        }
        
        if (newPassword !== confirmPassword) {
            this.showError('New passwords do not match');
            return;
        }
        
        try {
            const response = await fetch('/api/settings/security', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: this.userId,
                    session_id: this.sessionId,
                    current_password: currentPassword,
                    new_password: newPassword
                })
            });
            
            if (response.ok) {
                this.showSuccess('Password changed successfully!');
                document.getElementById('currentPassword').value = '';
                document.getElementById('newPassword').value = '';
                document.getElementById('confirmPassword').value = '';
            } else {
                const error = await response.json();
                this.showError(error.error || 'Failed to change password');
            }
        } catch (error) {
            this.showError('Error changing password: ' + error.message);
        }
    }
    
    async savePrivacySettings() {
        const profileVisibility = document.getElementById('profileVisibility')?.value || 'public';
        const privateAccount = document.getElementById('privateAccount')?.checked ?? false;
        const showOnlineStatus = document.getElementById('showOnlineStatus')?.checked ?? true;
        const dmEnabled = document.getElementById('dmEnabled')?.checked ?? true;
        
        try {
            const response = await fetch('/api/settings/privacy', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: this.userId,
                    session_id: this.sessionId,
                    profile_visibility: profileVisibility,
                    private_account: privateAccount,
                    show_online_status: showOnlineStatus,
                    dm_enabled: dmEnabled
                })
            });
            
            if (response.ok) {
                this.showSuccess('Privacy settings saved successfully!');
            } else {
                const error = await response.json();
                this.showError(error.error || 'Failed to save settings');
            }
        } catch (error) {
            this.showError('Error saving settings: ' + error.message);
        }
    }
    
    async saveNotificationSettings() {
        const emailEnabled = document.getElementById('emailEnabled')?.checked ?? false;
        const pushEnabled = document.getElementById('pushEnabled')?.checked ?? true;
        const mentions = document.getElementById('mentionsEnabled')?.checked ?? true;
        const follows = document.getElementById('followsEnabled')?.checked ?? true;
        const likes = document.getElementById('likesEnabled')?.checked ?? true;
        const comments = document.getElementById('commentsEnabled')?.checked ?? true;
        const reposts = document.getElementById('repostsEnabled')?.checked ?? false;
        
        try {
            const response = await fetch('/api/settings/notifications', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: this.userId,
                    session_id: this.sessionId,
                    email_enabled: emailEnabled,
                    push_enabled: pushEnabled,
                    mentions: mentions,
                    follows: follows,
                    likes: likes,
                    comments: comments,
                    reposts: reposts
                })
            });
            
            if (response.ok) {
                this.showSuccess('Notification settings saved successfully!');
            } else {
                const error = await response.json();
                this.showError(error.error || 'Failed to save settings');
            }
        } catch (error) {
            this.showError('Error saving settings: ' + error.message);
        }
    }
    
    async saveContentSettings() {
        const autoPlayVideos = document.getElementById('autoPlayVideos')?.checked ?? false;
        const contentFilter = document.getElementById('contentFilter')?.value || 'moderate';
        const language = document.getElementById('language')?.value || 'en';
        const timezone = document.getElementById('timezone')?.value || 'UTC';
        
        try {
            const response = await fetch('/api/settings/content', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: this.userId,
                    session_id: this.sessionId,
                    auto_play_videos: autoPlayVideos,
                    content_filter: contentFilter,
                    language: language,
                    timezone: timezone
                })
            });
            
            if (response.ok) {
                this.showSuccess('Content settings saved successfully!');
            } else {
                const error = await response.json();
                this.showError(error.error || 'Failed to save settings');
            }
        } catch (error) {
            this.showError('Error saving settings: ' + error.message);
        }
    }
    
    async exportData() {
        try {
            const response = await fetch(`/api/user/export?user_id=${this.userId}&session_id=${this.sessionId}`);
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `thesidia_export_${new Date().toISOString().split('T')[0]}.json`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
                this.showSuccess('Data exported successfully!');
            } else {
                this.showError('Failed to export data');
            }
        } catch (error) {
            this.showError('Error exporting data: ' + error.message);
        }
    }
    
    async deleteAccount() {
        const password = document.getElementById('deleteConfirmPassword')?.value || '';
        
        if (!confirm('Are you sure you want to delete your account? This action cannot be undone. All your data will be permanently deleted.')) {
            return;
        }
        
        try {
            const response = await fetch('/api/settings/delete-account', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: this.userId,
                    session_id: this.sessionId,
                    password: password
                })
            });
            
            if (response.ok) {
                alert('Account deleted successfully. You will be redirected to the home page.');
                localStorage.clear();
                window.location.href = '/';
            } else {
                const error = await response.json();
                const errorEl = document.getElementById('deleteAccountError');
                if (errorEl) {
                    errorEl.textContent = error.error || 'Failed to delete account';
                } else {
                    this.showError(error.error || 'Failed to delete account');
                }
            }
        } catch (error) {
            this.showError('Error deleting account: ' + error.message);
        }
    }
    
    async toggleTwoFactor() {
        const enabled = document.getElementById('twoFactorEnabled')?.checked ?? false;
        
        try {
            const response = await fetch('/api/settings/security', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: this.userId,
                    session_id: this.sessionId,
                    two_factor_enabled: enabled
                })
            });
            
            if (response.ok) {
                this.showSuccess(enabled ? 'Two-factor authentication enabled' : 'Two-factor authentication disabled');
            } else {
                const error = await response.json();
                this.showError(error.error || 'Failed to update 2FA setting');
                // Revert checkbox
                const checkbox = document.getElementById('twoFactorEnabled');
                if (checkbox) checkbox.checked = !enabled;
            }
        } catch (error) {
            this.showError('Error updating 2FA: ' + error.message);
            // Revert checkbox
            const checkbox = document.getElementById('twoFactorEnabled');
            if (checkbox) checkbox.checked = !enabled;
        }
    }
    
    async blockUser() {
        const username = document.getElementById('blockUserInput')?.value?.trim() || '';
        if (!username) {
            this.showError('Please enter a username to block');
            return;
        }
        
        try {
            const response = await fetch(`/api/users/${encodeURIComponent(username)}/block`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: this.userId,
                    session_id: this.sessionId
                })
            });
            
            if (response.ok) {
                this.showSuccess(`User ${username} blocked successfully`);
                document.getElementById('blockUserInput').value = '';
                await this.loadBlockedUsers();
            } else {
                const error = await response.json();
                this.showError(error.error || 'Failed to block user');
            }
        } catch (error) {
            this.showError('Error blocking user: ' + error.message);
        }
    }
    
    async muteUser() {
        const username = document.getElementById('muteUserInput')?.value?.trim() || '';
        if (!username) {
            this.showError('Please enter a username to mute');
            return;
        }
        
        try {
            const response = await fetch(`/api/users/${encodeURIComponent(username)}/mute`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: this.userId,
                    session_id: this.sessionId
                })
            });
            
            if (response.ok) {
                this.showSuccess(`User ${username} muted successfully`);
                document.getElementById('muteUserInput').value = '';
                await this.loadMutedUsers();
            } else {
                const error = await response.json();
                this.showError(error.error || 'Failed to mute user');
            }
        } catch (error) {
            this.showError('Error muting user: ' + error.message);
        }
    }
    
    async loadBlockedUsers() {
        if (!this.settings) return;
        
        const blockedList = document.getElementById('blockedUsersList');
        if (!blockedList) return;
        
        const blocked = this.settings.privacy?.blocked_users || [];
        if (blocked.length === 0) {
            blockedList.innerHTML = '<p class="form-help">No blocked users</p>';
            return;
        }
        
        blockedList.innerHTML = blocked.map(userId => `
            <div class="session-item">
                <div class="session-info">
                    <div class="session-title">${userId}</div>
                </div>
                <button class="btn" onclick="settingsPage.unblockUser('${userId}')">Unblock</button>
            </div>
        `).join('');
    }
    
    async loadMutedUsers() {
        if (!this.settings) return;
        
        const mutedList = document.getElementById('mutedUsersList');
        if (!mutedList) return;
        
        const muted = this.settings.privacy?.muted_users || [];
        if (muted.length === 0) {
            mutedList.innerHTML = '<p class="form-help">No muted users</p>';
            return;
        }
        
        mutedList.innerHTML = muted.map(userId => `
            <div class="session-item">
                <div class="session-info">
                    <div class="session-title">${userId}</div>
                </div>
                <button class="btn" onclick="settingsPage.unmuteUser('${userId}')">Unmute</button>
            </div>
        `).join('');
    }
    
    async unblockUser(userId) {
        // TODO: Implement unblock endpoint
        this.showError('Unblock functionality not yet implemented');
    }
    
    async unmuteUser(userId) {
        // TODO: Implement unmute endpoint
        this.showError('Unmute functionality not yet implemented');
    }
    
    handleAvatarUpload(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        if (file.size > 5 * 1024 * 1024) {
            this.showError('Image size must be less than 5MB');
            return;
        }
        
        const reader = new FileReader();
        reader.onload = (e) => {
            const avatarPreview = document.getElementById('avatarPreview');
            if (avatarPreview) {
                avatarPreview.src = e.target.result;
            }
        };
        reader.readAsDataURL(file);
        
        // TODO: Upload to server
    }
    
    updateCharCount() {
        const bio = document.getElementById('bio');
        const charCount = document.getElementById('bioCharCount');
        if (bio && charCount) {
            charCount.textContent = bio.value.length;
        }
    }
    
    checkPasswordStrength() {
        const password = document.getElementById('newPassword')?.value || '';
        const strengthBar = document.getElementById('passwordStrengthBar');
        
        if (!strengthBar) return;
        
        let strength = 0;
        if (password.length >= 12) strength += 0.33;
        if (/[a-zA-Z]/.test(password) && /[0-9]/.test(password)) strength += 0.33;
        if (/[^a-zA-Z0-9]/.test(password)) strength += 0.34;
        
        strengthBar.className = 'password-strength-bar';
        if (strength < 0.5) {
            strengthBar.classList.add('password-strength-weak');
            strengthBar.style.width = '33%';
        } else if (strength < 0.8) {
            strengthBar.classList.add('password-strength-medium');
            strengthBar.style.width = '66%';
        } else {
            strengthBar.classList.add('password-strength-strong');
            strengthBar.style.width = '100%';
        }
    }
    
    showSuccess(message) {
        const successMsg = document.getElementById('successMessage');
        if (successMsg) {
            successMsg.textContent = message;
            successMsg.classList.add('show');
            setTimeout(() => successMsg.classList.remove('show'), 3000);
        }
    }
    
    showError(message) {
        alert(message); // TODO: Replace with better error display
    }
}

// Export for use in HTML
window.SettingsPage = SettingsPage;

