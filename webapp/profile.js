// Profile Page Functionality
class ProfilePage {
    constructor() {
        this.currentCropType = null;
        this.userId = null;
        this.sessionId = null;
        this.init();
    }
    
    async init() {
        // Load user session
        this.userId = localStorage.getItem('thesidia_user_id');
        this.sessionId = localStorage.getItem('thesidia_session_id');
        
        if (!this.sessionId) {
            try {
                const response = await fetch('/api/user/session', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({})
                });
                const data = await response.json();
                if (data.user_id && data.session_id) {
                    this.userId = data.user_id;
                    this.sessionId = data.session_id;
                    localStorage.setItem('thesidia_user_id', this.userId);
                    localStorage.setItem('thesidia_session_id', this.sessionId);
                }
            } catch (error) {
                console.error('Error loading session:', error);
            }
        }
        
        // Load timeline on init
        this.loadTimeline();
        
        // Setup tab switching
        document.querySelectorAll('.profile-nav-item').forEach(item => {
            item.addEventListener('click', () => {
                const tab = item.dataset.tab;
                this.switchTab(tab);
            });
        }); // 'profile' or 'banner'
        this.cropCanvas = null;
        this.cropImage = null;
        this.cropContext = null;
        this.init();
    }

    init() {
        this.loadProfileData();
        this.setupEventListeners();
        this.loadTimeline();
    }

    loadProfileData() {
        // Load from localStorage or use defaults
        const profileData = JSON.parse(localStorage.getItem('profileData') || '{}');
        
        // Set profile data
        document.getElementById('profileNameLarge').textContent = profileData.name || 'Jack Danger';
        document.getElementById('profileUsernameLarge').textContent = `@${profileData.username || 'jacksonadanger'}`;
        document.getElementById('profileBio').textContent = profileData.bio || 'Exploring the depths of consciousness and pattern recognition. Building Thesidia.';
        
        if (profileData.location) {
            document.getElementById('profileLocation').querySelector('span').textContent = profileData.location;
        }
        
        if (profileData.website) {
            const websiteLink = document.getElementById('profileWebsiteLink');
            websiteLink.textContent = profileData.website;
            websiteLink.href = profileData.website.startsWith('http') ? profileData.website : `https://${profileData.website}`;
        }
        
        if (profileData.socialUrl) {
            const socialLink = document.getElementById('profileSocialLink');
            socialLink.href = profileData.socialUrl;
            const socialText = document.getElementById('profileSocialText');
            socialText.textContent = profileData.socialType === 'facebook' ? 'Facebook' : 'Instagram';
        }

        // Load images
        const savedBanner = localStorage.getItem('profileBanner');
        if (savedBanner) {
            const banner = document.getElementById('profileBanner');
            if (!banner.querySelector('img')) {
                const img = document.createElement('img');
                img.src = savedBanner;
                banner.insertBefore(img, banner.firstChild);
            }
        }

        const savedProfilePic = localStorage.getItem('profileImage');
        if (savedProfilePic) {
            document.getElementById('profilePictureImg').src = savedProfilePic;
        }
    }

    setupEventListeners() {
        // Edit profile button
        document.getElementById('editProfileBtn').addEventListener('click', () => this.openEditModal());
        document.getElementById('closeEditModal').addEventListener('click', () => this.closeEditModal());
        document.getElementById('cancelEditBtn').addEventListener('click', () => this.closeEditModal());
        document.getElementById('saveEditBtn').addEventListener('click', () => this.saveProfile());

        // Profile picture edit
        document.getElementById('profilePictureLarge').addEventListener('click', () => {
            document.getElementById('profilePictureInput').click();
        });
        document.getElementById('profilePictureInput').addEventListener('change', (e) => {
            this.handleImageUpload(e.target.files[0], 'profile');
        });

        // Banner edit
        document.getElementById('bannerEditBtn').addEventListener('click', () => {
            document.getElementById('bannerImageInput').click();
        });
        document.getElementById('bannerImageInput').addEventListener('change', (e) => {
            this.handleImageUpload(e.target.files[0], 'banner');
        });

        // Bio character count
        const bioTextarea = document.getElementById('editBio');
        if (bioTextarea) {
            bioTextarea.addEventListener('input', () => this.updateCharCount());
        }

        // Social media selection
        document.querySelectorAll('.edit-profile-social-option').forEach(option => {
            option.addEventListener('click', () => {
                document.querySelectorAll('.edit-profile-social-option').forEach(o => o.classList.remove('selected'));
                option.classList.add('selected');
            });
        });

        // Tab navigation
        document.querySelectorAll('.profile-nav-item').forEach(item => {
            item.addEventListener('click', () => {
                document.querySelectorAll('.profile-nav-item').forEach(i => i.classList.remove('active'));
                item.classList.add('active');
                this.switchTab(item.dataset.tab);
            });
        });

        // Crop modal
        document.getElementById('cancelCropBtn').addEventListener('click', () => this.closeCropModal());
        document.getElementById('applyCropBtn').addEventListener('click', () => this.applyCrop());
    }

    openEditModal() {
        const modal = document.getElementById('editProfileModal');
        const profileData = JSON.parse(localStorage.getItem('profileData') || '{}');
        
        // Populate form
        document.getElementById('editName').value = profileData.name || 'Jack Danger';
        document.getElementById('editUsername').value = profileData.username || 'jacksonadanger';
        document.getElementById('editTag').value = profileData.tag || '';
        document.getElementById('editBio').value = profileData.bio || '';
        document.getElementById('editLocation').value = profileData.location || '';
        document.getElementById('editWebsite').value = profileData.website || '';
        document.getElementById('editSocialUrl').value = profileData.socialUrl || '';
        
        // Set social type
        const socialType = profileData.socialType || 'instagram';
        document.querySelectorAll('.edit-profile-social-option').forEach(o => {
            o.classList.toggle('selected', o.dataset.social === socialType);
        });
        
        this.updateCharCount();
        modal.classList.add('open');
    }

    closeEditModal() {
        document.getElementById('editProfileModal').classList.remove('open');
    }

    updateCharCount() {
        const bio = document.getElementById('editBio');
        const count = document.getElementById('bioCharCount');
        const length = bio.value.length;
        const maxLength = 300;
        
        count.textContent = `${length} / ${maxLength}`;
        count.classList.remove('warning', 'error');
        
        if (length > maxLength * 0.9) {
            count.classList.add('warning');
        }
        if (length > maxLength) {
            count.classList.add('error');
        }
    }

    saveProfile() {
        const profileData = {
            name: document.getElementById('editName').value.trim(),
            username: document.getElementById('editUsername').value.trim(),
            tag: document.getElementById('editTag').value.trim(),
            bio: document.getElementById('editBio').value.trim(),
            location: document.getElementById('editLocation').value.trim(),
            website: document.getElementById('editWebsite').value.trim(),
            socialUrl: document.getElementById('editSocialUrl').value.trim(),
            socialType: document.querySelector('.edit-profile-social-option.selected')?.dataset.social || 'instagram'
        };

        // Validation
        if (profileData.bio.length > 300) {
            alert('Bio must be 300 characters or less');
            return;
        }

        // Save to localStorage
        localStorage.setItem('profileData', JSON.stringify(profileData));
        
        // Update UI
        this.loadProfileData();
        this.closeEditModal();
    }

    handleImageUpload(file, type) {
        if (!file) return;
        
        this.currentCropType = type;
        const reader = new FileReader();
        
        reader.onload = (e) => {
            const img = new Image();
            img.onload = () => {
                this.openCropModal(img, type);
            };
            img.src = e.target.result;
        };
        
        reader.readAsDataURL(file);
    }

    openCropModal(image, type) {
        const modal = document.getElementById('cropModal');
        const preview = document.getElementById('cropPreview');
        
        this.cropImage = image;
        
        // Create canvas
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        
        // Set dimensions based on type
        if (type === 'banner') {
            canvas.width = 1200;
            canvas.height = 400;
            ctx.drawImage(image, 0, 0, canvas.width, canvas.height);
        } else {
            // Profile picture - square crop
            const size = Math.min(image.width, image.height);
            canvas.width = 400;
            canvas.height = 400;
            
            // Center crop
            const sourceX = (image.width - size) / 2;
            const sourceY = (image.height - size) / 2;
            
            ctx.drawImage(
                image,
                sourceX, sourceY, size, size,
                0, 0, canvas.width, canvas.height
            );
        }
        
        this.cropCanvas = canvas;
        this.cropContext = ctx;
        
        preview.innerHTML = '';
        preview.appendChild(canvas);
        modal.classList.add('open');
    }

    closeCropModal() {
        document.getElementById('cropModal').classList.remove('open');
        this.cropCanvas = null;
        this.cropImage = null;
        this.cropContext = null;
    }

    applyCrop() {
        if (!this.cropCanvas) return;
        
        const dataURL = this.cropCanvas.toDataURL('image/jpeg', 0.9);
        
        if (this.currentCropType === 'banner') {
            // Update banner
            const banner = document.getElementById('profileBanner');
            let img = banner.querySelector('img');
            if (!img) {
                img = document.createElement('img');
                banner.insertBefore(img, banner.firstChild);
            }
            img.src = dataURL;
            localStorage.setItem('profileBanner', dataURL);
        } else {
            // Update profile picture
            document.getElementById('profilePictureImg').src = dataURL;
            localStorage.setItem('profileImage', dataURL);
            
            // Also update header profile picture
            const headerProfile = document.getElementById('headerProfilePicture');
            if (headerProfile) {
                const headerImg = headerProfile.querySelector('img');
                if (headerImg) {
                    headerImg.src = dataURL;
                }
            }
        }
        
        this.closeCropModal();
    }

    switchTab(tab) {
        // Load different content based on tab
        console.log('Switching to tab:', tab);
        // TODO: Implement tab switching logic
    }

    async loadTimeline() {
        // Load user's posts from API
        const timeline = document.getElementById('profileTimeline');
        if (!timeline) return;
        
        // Show loading state
        timeline.innerHTML = '<div class="profile-loading">Loading posts...</div>';
        
        try {
            const userId = localStorage.getItem('thesidia_user_id');
            const sessionId = localStorage.getItem('thesidia_session_id');
            const profileUserId = this.getProfileUserId() || userId;
            
            // Fetch user posts
            const response = await fetch(`/api/posts?user_id=${profileUserId}&limit=50`);
            const data = await response.json();
            
            if (data.posts && data.posts.length > 0) {
                timeline.innerHTML = '';
                data.posts.forEach(post => {
                    const postElement = this.createPostElement(post);
                    timeline.appendChild(postElement);
                });
                
                // Update post count
                const postsCountEl = document.getElementById('profilePostsCount');
                if (postsCountEl) {
                    postsCountEl.textContent = data.posts.length;
                }
            } else {
                timeline.innerHTML = `
                    <div class="profile-empty">
                        <div class="profile-empty-icon">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                            </svg>
                        </div>
                        <p>No posts yet. Start sharing your thoughts!</p>
                    </div>
                `;
            }
        } catch (error) {
            console.error('Error loading timeline:', error);
            timeline.innerHTML = '<div class="profile-error">Error loading posts. Please try again.</div>';
        }
    }
    
    getProfileUserId() {
        // Get user ID from URL or use current user
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get('user_id') || localStorage.getItem('thesidia_user_id');
    }

    createPostElement(post) {
        const div = document.createElement('div');
        div.className = 'profile-post';
        
        const isPinned = post.pinned || false;
        
        div.innerHTML = `
            <div class="profile-post-header">
                <div class="profile-post-avatar">
                    <img src="${post.avatar || '/profile-image.jpg'}" alt="Profile">
                </div>
                <div class="profile-post-info">
                    <div class="profile-post-author">
                        <span class="profile-post-author-name">${post.authorName || 'Jack Danger'}</span>
                        <span class="profile-post-author-handle">@${post.authorHandle || 'jacksonadanger'}</span>
                        ${isPinned ? '<span class="profile-post-pinned"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 17v5M9 10V6a3 3 0 0 1 3-3h0a3 3 0 0 1 3 3v4M9 10H6a2 2 0 0 0-2 2v7a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-7a2 2 0 0 0-2-2h-3M9 10h6"/></svg> Pinned</span>' : ''}
                    </div>
                    <div class="profile-post-content">${this.escapeHtml(post.content || '')}</div>
                    <div class="profile-post-actions">
                        <button class="profile-post-action">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                            </svg>
                            <span>${post.replies || 0}</span>
                        </button>
                        <button class="profile-post-action">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
                            </svg>
                            <span>${post.reposts || 0}</span>
                        </button>
                        <button class="profile-post-action">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
                            </svg>
                            <span>${post.likes || 0}</span>
                        </button>
                        <button class="profile-post-action pin-action ${isPinned ? 'pinned' : ''}" data-post-id="${post.id}" onclick="profilePage.togglePin('${post.id}')">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M12 17v5M9 10V6a3 3 0 0 1 3-3h0a3 3 0 0 1 3 3v4M9 10H6a2 2 0 0 0-2 2v7a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-7a2 2 0 0 0-2-2h-3M9 10h6"/>
                            </svg>
                            <span>Pin</span>
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        return div;
    }

    togglePin(postId) {
        const posts = JSON.parse(localStorage.getItem('profilePosts') || '[]');
        const post = posts.find(p => p.id === postId);
        
        if (post) {
            // Unpin all other posts
            posts.forEach(p => {
                if (p.id !== postId) {
                    p.pinned = false;
                }
            });
            
            // Toggle this post
            post.pinned = !post.pinned;
            localStorage.setItem('profilePosts', JSON.stringify(posts));
            this.loadTimeline();
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize profile page when DOM is ready
let profilePage;
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        profilePage = new ProfilePage();
    });
} else {
    profilePage = new ProfilePage();
}

