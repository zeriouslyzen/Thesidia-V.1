/**
 * Profile Customization
 * Handles differences between own profile view vs others' profile view
 */

import { OnboardingUtils } from './utils.js';

export class ProfileCustomization {
    constructor() {
        this.isInitialized = false;
        this.customizationSettings = null;
    }
    
    /**
     * Initialize profile customization
     */
    init() {
        if (!OnboardingUtils.isEnabled()) {
            return;
        }
        
        if (this.isInitialized) {
            return;
        }
        
        try {
            this.customizationSettings = OnboardingUtils.getProfileCustomization();
            this.detectProfileContext();
            this.setupCustomizationUI();
            this.isInitialized = true;
        } catch (error) {
            console.error('[ProfileCustomization] Error:', error);
        }
    }
    
    /**
     * Detect if viewing own profile or someone else's
     */
    detectProfileContext() {
        // Try to get profile user ID from page
        const profileUserId = this.getProfileUserId();
        const currentUserId = OnboardingUtils.getCurrentUserId();
        
        const isOwn = profileUserId && currentUserId && profileUserId === currentUserId;
        
        if (isOwn) {
            this.showOwnProfileView();
        } else {
            this.showOthersProfileView();
        }
    }
    
    /**
     * Get profile user ID from page
     */
    getProfileUserId() {
        // Try multiple methods to detect profile user
        // Method 1: Check URL params
        const urlParams = new URLSearchParams(window.location.search);
        const userId = urlParams.get('user_id') || urlParams.get('id');
        if (userId) return userId;
        
        // Method 2: Check data attributes
        const profileElement = document.querySelector('[data-user-id]');
        if (profileElement) {
            return profileElement.getAttribute('data-user-id');
        }
        
        // Method 3: Check localStorage (if profile page stores it)
        const storedUserId = localStorage.getItem('viewing_profile_user_id');
        if (storedUserId) return storedUserId;
        
        // Method 4: Assume own profile if on /profile without params
        if (window.location.pathname.includes('profile') && 
            !window.location.search.includes('user_id') &&
            !window.location.search.includes('id')) {
            return OnboardingUtils.getCurrentUserId();
        }
        
        return null;
    }
    
    /**
     * Show own profile view (with edit controls and private sections)
     */
    showOwnProfileView() {
        // Add edit button if not present
        this.addEditButton();
        
        // Show private sections
        this.showPrivateSections();
        
        // Add customization panel
        this.addCustomizationPanel();
        
        // Add preview toggle
        this.addPreviewToggle();
        
        // Hide follow/message buttons (if present)
        this.hidePublicActions();
    }
    
    /**
     * Show others' profile view (public only)
     */
    showOthersProfileView() {
        // Hide edit controls
        this.hideEditControls();
        
        // Hide private sections
        this.hidePrivateSections();
        
        // Show follow/message buttons
        this.showPublicActions();
        
        // Apply custom layout if user has one
        this.applyCustomLayout();
    }
    
    /**
     * Add edit button to profile
     */
    addEditButton() {
        if (document.querySelector('.onboarding-profile-edit-btn')) {
            return; // Already added
        }
        
        const profileInfo = document.querySelector('.profile-info, .profile-header');
        if (!profileInfo) return;
        
        const editBtn = document.createElement('button');
        editBtn.className = 'onboarding-profile-edit-btn';
        editBtn.textContent = 'Edit Profile';
        editBtn.onclick = () => this.openEditModal();
        
        // Insert after profile name or at end of profile info
        const nameElement = profileInfo.querySelector('.profile-name-large, .profile-username-large');
        if (nameElement && nameElement.parentNode) {
            nameElement.parentNode.insertBefore(editBtn, nameElement.nextSibling);
        } else {
            profileInfo.appendChild(editBtn);
        }
    }
    
    /**
     * Show private sections
     */
    showPrivateSections() {
        // Create private sections container if it doesn't exist
        let privateContainer = document.querySelector('.onboarding-private-sections');
        if (!privateContainer) {
            privateContainer = document.createElement('div');
            privateContainer.className = 'onboarding-private-sections';
            
            // Add sections
            const sections = [
                { id: 'drafts', title: 'Drafts', icon: '📝' },
                { id: 'analytics', title: 'Analytics', icon: '📊' },
                { id: 'saved', title: 'Saved Posts', icon: '🔖' },
                { id: 'settings', title: 'Settings', icon: '⚙️' }
            ];
            
            sections.forEach(section => {
                const sectionEl = document.createElement('div');
                sectionEl.className = `onboarding-private-section onboarding-private-${section.id}`;
                sectionEl.innerHTML = `
                    <div class="onboarding-private-section-header">
                        <span>${section.icon}</span>
                        <span>${section.title}</span>
                    </div>
                    <div class="onboarding-private-section-content">
                        ${this.getPrivateSectionContent(section.id)}
                    </div>
                `;
                privateContainer.appendChild(sectionEl);
            });
            
            // Insert after profile info
            const profileInfo = document.querySelector('.profile-info, .profile-header');
            if (profileInfo && profileInfo.parentNode) {
                profileInfo.parentNode.insertBefore(privateContainer, profileInfo.nextSibling);
            }
        }
        
        privateContainer.style.display = 'block';
    }
    
    /**
     * Get content for private section
     */
    getPrivateSectionContent(sectionId) {
        switch (sectionId) {
            case 'drafts':
                return '<p>Your unpublished posts will appear here.</p>';
            case 'analytics':
                return '<p>View your post performance and engagement metrics.</p>';
            case 'saved':
                return '<p>Posts you\'ve saved for later will appear here.</p>';
            case 'settings':
                return '<p>Manage your account settings and preferences.</p>';
            default:
                return '';
        }
    }
    
    /**
     * Hide private sections
     */
    hidePrivateSections() {
        const privateContainer = document.querySelector('.onboarding-private-sections');
        if (privateContainer) {
            privateContainer.style.display = 'none';
        }
    }
    
    /**
     * Add customization panel
     */
    addCustomizationPanel() {
        if (document.querySelector('.onboarding-customization-panel')) {
            return;
        }
        
        const panel = document.createElement('div');
        panel.className = 'onboarding-customization-panel';
        panel.innerHTML = `
            <div class="onboarding-customization-header">
                <h4>Customize Profile Layout</h4>
                <button class="onboarding-customization-close" onclick="this.closest('.onboarding-customization-panel').style.display='none'">×</button>
            </div>
            <div class="onboarding-customization-content">
                <div class="onboarding-customization-option">
                    <label>
                        <input type="checkbox" id="showBio" checked>
                        Show Bio
                    </label>
                </div>
                <div class="onboarding-customization-option">
                    <label>
                        <input type="checkbox" id="showStats" checked>
                        Show Stats
                    </label>
                </div>
                <div class="onboarding-customization-option">
                    <label>
                        <input type="checkbox" id="showSocialLinks" checked>
                        Show Social Links
                    </label>
                </div>
                <button class="onboarding-btn-primary onboarding-save-customization-btn">
                    Save Layout
                </button>
            </div>
        `;
        
        // Insert at end of profile page
        const profilePage = document.querySelector('.profile-page');
        if (profilePage) {
            profilePage.appendChild(panel);
        }
        
        // Attach event listener to save button
        const saveBtn = panel.querySelector('.onboarding-save-customization-btn');
        if (saveBtn) {
            saveBtn.addEventListener('click', () => this.saveCustomization());
        }
        
        // Load saved settings
        this.loadCustomizationSettings();
    }
    
    /**
     * Add preview toggle
     */
    addPreviewToggle() {
        if (document.querySelector('.onboarding-preview-toggle')) {
            return;
        }
        
        const toggle = document.createElement('button');
        toggle.className = 'onboarding-preview-toggle';
        toggle.textContent = '👁️ Preview Public View';
        toggle.onclick = () => this.togglePreview();
        
        const editBtn = document.querySelector('.onboarding-profile-edit-btn');
        if (editBtn) {
            editBtn.parentNode.insertBefore(toggle, editBtn.nextSibling);
        }
    }
    
    /**
     * Toggle preview mode
     */
    togglePreview() {
        const isPreview = document.body.classList.toggle('onboarding-preview-mode');
        const toggle = document.querySelector('.onboarding-preview-toggle');
        if (toggle) {
            toggle.textContent = isPreview ? '👁️ Exit Preview' : '👁️ Preview Public View';
        }
        
        if (isPreview) {
            this.showOthersProfileView();
        } else {
            this.showOwnProfileView();
        }
    }
    
    /**
     * Hide edit controls
     */
    hideEditControls() {
        const editBtn = document.querySelector('.onboarding-profile-edit-btn');
        if (editBtn) editBtn.style.display = 'none';
        
        const previewToggle = document.querySelector('.onboarding-preview-toggle');
        if (previewToggle) previewToggle.style.display = 'none';
        
        const customizationPanel = document.querySelector('.onboarding-customization-panel');
        if (customizationPanel) customizationPanel.style.display = 'none';
    }
    
    /**
     * Show public actions (follow, message)
     */
    showPublicActions() {
        // These would typically be part of the existing profile UI
        // We just ensure they're visible
        const followBtn = document.querySelector('.follow-btn, [data-action="follow"]');
        if (followBtn) followBtn.style.display = 'block';
    }
    
    /**
     * Hide public actions
     */
    hidePublicActions() {
        const followBtn = document.querySelector('.follow-btn, [data-action="follow"]');
        if (followBtn) followBtn.style.display = 'none';
    }
    
    /**
     * Apply custom layout
     */
    applyCustomLayout() {
        const settings = this.customizationSettings;
        if (!settings || !settings.layout) return;
        
        // Apply visibility settings
        if (settings.hideBio) {
            const bio = document.querySelector('.profile-bio');
            if (bio) bio.style.display = 'none';
        }
        
        if (settings.hideStats) {
            const stats = document.querySelector('.profile-stats');
            if (stats) stats.style.display = 'none';
        }
    }
    
    /**
     * Load customization settings
     */
    loadCustomizationSettings() {
        const settings = OnboardingUtils.getProfileCustomization();
        if (!settings) return;
        
        if (settings.showBio !== undefined) {
            const checkbox = document.getElementById('showBio');
            if (checkbox) checkbox.checked = settings.showBio;
        }
        
        if (settings.showStats !== undefined) {
            const checkbox = document.getElementById('showStats');
            if (checkbox) checkbox.checked = settings.showStats;
        }
        
        if (settings.showSocialLinks !== undefined) {
            const checkbox = document.getElementById('showSocialLinks');
            if (checkbox) checkbox.checked = settings.showSocialLinks;
        }
    }
    
    /**
     * Save customization settings
     */
    saveCustomization() {
        const settings = {
            showBio: document.getElementById('showBio')?.checked ?? true,
            showStats: document.getElementById('showStats')?.checked ?? true,
            showSocialLinks: document.getElementById('showSocialLinks')?.checked ?? true,
            layout: 'default'
        };
        
        OnboardingUtils.saveProfileCustomization(settings);
        this.customizationSettings = settings;
        
        // Show success message
        const panel = document.querySelector('.onboarding-customization-panel');
        if (panel) {
            const success = document.createElement('div');
            success.className = 'onboarding-customization-success';
            success.textContent = 'Layout saved!';
            panel.appendChild(success);
            setTimeout(() => success.remove(), 2000);
        }
    }
    
    /**
     * Open edit modal
     */
    openEditModal() {
        // This would open a modal for editing profile
        // For now, just show a message
        alert('Profile edit modal would open here. This is a placeholder for the actual edit functionality.');
    }
    
    /**
     * Setup customization UI
     */
    setupCustomizationUI() {
        // Check if we're on profile page
        if (OnboardingUtils.getCurrentPage() !== 'profile') {
            return;
        }
        
        // Wait for profile to load
        OnboardingUtils.waitForElement('.profile-page, .profile-info', 3000)
            .then(() => {
                this.detectProfileContext();
            })
            .catch(() => {
                // Profile not found - that's okay
            });
    }
}

// Make available globally for inline onclick handlers
window.profileCustomization = null;
window.ProfileCustomization = ProfileCustomization;

