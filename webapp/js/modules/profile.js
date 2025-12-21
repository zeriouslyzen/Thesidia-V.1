/**
 * Profile Module
 * Handles profile data fetching, display, edits, and image uploads.
 */

export class ProfilePage {
    constructor(appInstance) {
        this.app = appInstance;
        this.userId = appInstance?.userId || localStorage.getItem('thesidia_user_id');
        this.sessionId = appInstance?.sessionId || localStorage.getItem('thesidia_session_id');

        this.currentCropType = null; // 'profile' or 'banner'
        this.cropCanvas = null;
        this.cropImage = null;
        this.cropContext = null;

        this.init();
    }

    async init() {
        if (!document.querySelector('.profile-page')) return;

        await this.loadProfileData();
        this.setupEventListeners();
        this.loadTimeline();
    }

    async loadProfileData() {
        try {
            const response = await fetch(`/api/users/${this.userId}/profile`);
            if (response.ok) {
                const data = await response.json();
                this.updateUI(data);
            } else {
                this.loadFromLocalStorage();
            }
        } catch (error) {
            console.error('Error fetching profile:', error);
            this.loadFromLocalStorage();
        }
    }

    updateUI(data) {
        if (data.display_name) document.getElementById('profileNameLarge').textContent = data.display_name;
        if (data.username) document.getElementById('profileUsernameLarge').textContent = `@${data.username}`;
        if (data.bio) document.getElementById('profileBio').textContent = data.bio;

        if (data.location) {
            const locEl = document.getElementById('profileLocation');
            if (locEl) locEl.querySelector('span').textContent = data.location;
        }

        if (data.website) {
            const websiteLink = document.getElementById('profileWebsiteLink');
            if (websiteLink) {
                websiteLink.textContent = data.website;
                websiteLink.href = data.website.startsWith('http') ? data.website : `https://${data.website}`;
            }
        }

        if (data.avatar_url) {
            const img = document.getElementById('profilePictureImg');
            if (img) img.src = data.avatar_url;

            // Update header profile pic too
            const headerProfileImg = document.querySelector('#appHeader .profile-btn img');
            if (headerProfileImg) headerProfileImg.src = data.avatar_url;
        }

        if (data.banner_url) {
            const banner = document.getElementById('profileBanner');
            if (banner) {
                let img = banner.querySelector('img');
                if (!img) {
                    img = document.createElement('img');
                    banner.insertBefore(img, banner.firstChild);
                }
                img.src = data.banner_url;
            }
        }

        // Update stats
        if (data.stats) {
            if (data.stats.following !== undefined) document.getElementById('profileFollowingCount').textContent = data.stats.following;
            if (data.stats.followers !== undefined) document.getElementById('profileFollowersCount').textContent = data.stats.followers;
            if (data.stats.posts !== undefined) document.getElementById('profilePostsCount').textContent = data.stats.posts;
        }
    }

    loadFromLocalStorage() {
        const profileData = JSON.parse(localStorage.getItem('profileData') || '{}');
        this.updateUI({
            display_name: profileData.name,
            username: profileData.username,
            bio: profileData.bio,
            location: profileData.location,
            website: profileData.website,
            avatar_url: localStorage.getItem('profileImage'),
            banner_url: localStorage.getItem('profileBanner')
        });
    }

    setupEventListeners() {
        // Edit buttons
        const editBtn = document.getElementById('editProfileBtn');
        if (editBtn) editBtn.addEventListener('click', () => this.openEditModal());

        const closeBtn = document.getElementById('closeEditModal');
        if (closeBtn) closeBtn.addEventListener('click', () => this.closeEditModal());

        const cancelBtn = document.getElementById('cancelEditBtn');
        if (cancelBtn) cancelBtn.addEventListener('click', () => this.closeEditModal());

        const saveBtn = document.getElementById('saveEditBtn');
        if (saveBtn) saveBtn.addEventListener('click', () => this.saveProfile());

        // Image uploads
        const profilePicContainer = document.getElementById('profilePictureLarge');
        if (profilePicContainer) {
            profilePicContainer.addEventListener('click', () => document.getElementById('profilePictureInput').click());
        }

        const profilePicInput = document.getElementById('profilePictureInput');
        if (profilePicInput) {
            profilePicInput.addEventListener('change', (e) => this.handleImageUpload(e.target.files[0], 'profile'));
        }

        const bannerEditBtn = document.getElementById('bannerEditBtn');
        if (bannerEditBtn) {
            bannerEditBtn.addEventListener('click', () => document.getElementById('bannerImageInput').click());
        }

        const bannerImageInput = document.getElementById('bannerImageInput');
        if (bannerImageInput) {
            bannerImageInput.addEventListener('change', (e) => this.handleImageUpload(e.target.files[0], 'banner'));
        }

        // Bio count
        const bioTextarea = document.getElementById('editBio');
        if (bioTextarea) {
            bioTextarea.addEventListener('input', () => this.updateCharCount());
        }

        // Social selection
        document.querySelectorAll('.edit-profile-social-option').forEach(option => {
            option.addEventListener('click', () => {
                document.querySelectorAll('.edit-profile-social-option').forEach(o => o.classList.remove('selected'));
                option.classList.add('selected');
            });
        });

        // Tabs
        document.querySelectorAll('.profile-nav-item').forEach(item => {
            item.addEventListener('click', () => {
                document.querySelectorAll('.profile-nav-item').forEach(i => i.classList.remove('active'));
                item.classList.add('active');
                this.switchTab(item.dataset.tab);
            });
        });

        // Crop modal
        const cancelCropBtn = document.getElementById('cancelCropBtn');
        if (cancelCropBtn) cancelCropBtn.addEventListener('click', () => this.closeCropModal());

        const applyCropBtn = document.getElementById('applyCropBtn');
        if (applyCropBtn) applyCropBtn.addEventListener('click', () => this.applyCrop());
    }

    openEditModal() {
        const modal = document.getElementById('editProfileModal');
        if (!modal) return;

        // Current UI values as defaults
        document.getElementById('editName').value = document.getElementById('profileNameLarge').textContent;
        document.getElementById('editBio').value = document.getElementById('profileBio').textContent;
        document.getElementById('editLocation').value = document.getElementById('profileLocation').querySelector('span').textContent;

        // Placeholder for other fields or load from state
        this.updateCharCount();
        modal.classList.add('open');
    }

    closeEditModal() {
        const modal = document.getElementById('editProfileModal');
        if (modal) modal.classList.remove('open');
    }

    updateCharCount() {
        const bio = document.getElementById('editBio');
        const count = document.getElementById('bioCharCount');
        if (!bio || !count) return;

        const length = bio.value.length;
        const maxLength = 300;
        count.textContent = `${length} / ${maxLength}`;
        count.classList.toggle('warning', length > maxLength * 0.9);
        count.classList.toggle('error', length > maxLength);
    }

    async saveProfile() {
        const name = document.getElementById('editName').value.trim();
        const bio = document.getElementById('editBio').value.trim();
        const location = document.getElementById('editLocation').value.trim();
        const website = document.getElementById('editWebsite')?.value.trim();

        try {
            const response = await fetch('/api/settings/account', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    display_name: name,
                    bio: bio,
                    location: location,
                    website: website,
                    user_id: this.userId,
                    session_id: this.sessionId
                })
            });

            if (response.ok) {
                await this.loadProfileData();
                this.closeEditModal();
            }
        } catch (error) {
            console.error('Error saving profile:', error);
        }
    }

    handleImageUpload(file, type) {
        if (!file) return;
        this.currentCropType = type;
        const reader = new FileReader();
        reader.onload = (e) => {
            const img = new Image();
            img.onload = () => this.openCropModal(img, type);
            img.src = e.target.result;
        };
        reader.readAsDataURL(file);
    }

    openCropModal(image, type) {
        const modal = document.getElementById('cropModal');
        const preview = document.getElementById('cropPreview');
        if (!modal || !preview) return;

        this.cropImage = image;
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');

        if (type === 'banner') {
            canvas.width = 1200;
            canvas.height = 400;
            ctx.drawImage(image, 0, 0, canvas.width, canvas.height);
        } else {
            const size = Math.min(image.width, image.height);
            canvas.width = 400;
            canvas.height = 400;
            const sourceX = (image.width - size) / 2;
            const sourceY = (image.height - size) / 2;
            ctx.drawImage(image, sourceX, sourceY, size, size, 0, 0, canvas.width, canvas.height);
        }

        this.cropCanvas = canvas;
        preview.innerHTML = '';
        preview.appendChild(canvas);
        modal.classList.add('open');
    }

    closeCropModal() {
        const modal = document.getElementById('cropModal');
        if (modal) modal.classList.remove('open');
        this.cropCanvas = null;
        this.cropImage = null;
    }

    async applyCrop() {
        if (!this.cropCanvas) return;
        const dataURL = this.cropCanvas.toDataURL('image/jpeg', 0.9);

        // Temporarily save to local storage until API is ready
        if (this.currentCropType === 'banner') {
            localStorage.setItem('profileBanner', dataURL);
        } else {
            localStorage.setItem('profileImage', dataURL);
        }

        // Ideally here we send to API: /api/profile/upload
        // For now, update UI immediately
        this.loadFromLocalStorage();
        this.closeCropModal();
    }

    switchTab(tab) {
        console.log('Switching to tab:', tab);
        // Implement tab specific data fetching
    }

    loadTimeline() {
        console.log('Loading timeline via API...');
        // Implement post fetching via /api/feed but filtered for user
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}
