// Profile Page Functionality
class ProfilePage {
    constructor() {
        this.currentCropType = null; // 'profile' or 'banner'
        this.cropCanvas = null;
        this.cropImage = null;
        this.cropContext = null;
        this.init();
    }

    init() {
        this.userId = this.getQueryParam('user_id');
        this.loadProfileData();
        this.setupEventListeners();
        this.loadTimeline();
    }

    getQueryParam(name) {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get(name);
    }

    async loadProfileData() {
        if (this.userId) {
            try {
                const response = await fetch('/mock-profiles.json');
                const data = await response.json();
                const profile = data.profiles.find(p => p.user_id === this.userId);

                if (profile) {
                    this.renderProfile(profile);
                    this.mockPosts = profile.posts || [];
                    this.loadTimeline();
                    return;
                }
            } catch (error) {
                console.error('Error loading mock profile:', error);
            }
        }

        // Load from localStorage or use defaults
        const profileData = JSON.parse(localStorage.getItem('profileData') || '{}');
        this.renderProfile({
            display_name: profileData.name || 'Jack Danger',
            username: profileData.username || 'jacksonadanger',
            bio: profileData.bio || 'Exploring the depths of consciousness and pattern recognition. Building Thesidia.',
            location: profileData.location || 'San Francisco, CA',
            website: profileData.website || 'thesidia.com',
            avatar_url: localStorage.getItem('profileImage'),
            banner_url: localStorage.getItem('profileBanner')
        });
    }

    renderProfile(data) {
        // Basic Info
        const nameEl = document.getElementById('profileNameLarge');
        const userEl = document.getElementById('profileUsernameLarge');
        const bioEl = document.getElementById('profileBio');
        const roleEl = document.getElementById('profileRole');
        const disciplinesEl = document.getElementById('profileDisciplines');

        if (nameEl) nameEl.textContent = data.display_name || data.name;
        if (userEl) userEl.textContent = `@${data.username}`;
        if (bioEl) bioEl.textContent = data.bio;
        if (roleEl) roleEl.textContent = data.role || 'Practitioner';

        // Domains / Disciplines
        if (disciplinesEl && data.domains) {
            disciplinesEl.innerHTML = data.domains.map(d =>
                `<span class="profile-discipline-chip">${d.charAt(0).toUpperCase() + d.slice(1)}</span>`
            ).join('');
        }

        // Meta (Location/Website)
        const locEl = document.getElementById('profileLocation');
        if (locEl && data.location) {
            locEl.innerHTML = `<span>${data.location}</span>`;
        }

        const webLink = document.getElementById('profileWebsiteLink');
        if (webLink && data.website) {
            webLink.textContent = data.website.replace(/^https?:\/\//, '');
            webLink.href = data.website.startsWith('http') ? data.website : `https://${data.website}`;
        }

        // Stats
        const stats = data.stats || { friends: 0, fans: 0, resonating: 0, cuts: 0 };
        const friendsCount = document.getElementById('profileFriendsCount');
        const fansCount = document.getElementById('profileFansCount');
        const resonatingCount = document.getElementById('profileResonatingCount');
        const cutsCount = document.getElementById('profileCutsCount');

        if (friendsCount) friendsCount.textContent = this.formatNumber(stats.friends);
        if (fansCount) fansCount.textContent = this.formatNumber(stats.fans);
        if (resonatingCount) resonatingCount.textContent = this.formatNumber(stats.resonating);
        if (cutsCount) cutsCount.textContent = this.formatNumber(stats.cuts || 0);

        // Images
        if (data.banner_url) {
            const banner = document.getElementById('profileBanner');
            if (banner) {
                banner.innerHTML = `<img src="${data.banner_url}" alt="Banner">`;
                if (!this.userId) {
                    banner.innerHTML += `
                        <div class="profile-banner-edit" id="bannerEditBtn">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
                                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
                            </svg>
                            <span>Edit banner</span>
                        </div>
                    `;
                    document.getElementById('bannerEditBtn').addEventListener('click', () => {
                        document.getElementById('bannerImageInput').click();
                    });
                }
            }
        }

        const avatarImg = document.getElementById('profilePictureImg');
        if (avatarImg && data.avatar_url) {
            avatarImg.src = data.avatar_url;
        }

        // Portfolio Deep Dive
        if (data.portfolio) {
            this.renderPortfolio(data.portfolio);
        }

        // UI Controls
        const editBtn = document.getElementById('editProfileBtn');
        if (this.userId && editBtn) {
            editBtn.style.display = 'none';
            const bannerEdit = document.getElementById('bannerEditBtn');
            if (bannerEdit) bannerEdit.style.display = 'none';
        } else if (editBtn) {
            editBtn.style.display = 'block';
        }
    }

    renderPortfolio(portfolio) {
        // Reading List
        const readingList = document.getElementById('portfolioReading');
        if (readingList && portfolio.reading) {
            readingList.innerHTML = portfolio.reading.map(book => `
                <div class="reading-item">
                    <img src="${book.image}" alt="${book.title}" class="reading-cover">
                    <div class="reading-info">
                        <div class="reading-title">${book.title}</div>
                        <div class="reading-author">${book.author}</div>
                    </div>
                </div>
            `).join('');
        }

        // Credentials
        const credsList = document.getElementById('portfolioCredentials');
        if (credsList && portfolio.credentials) {
            credsList.innerHTML = portfolio.credentials.map(cred =>
                `<div class="credential-chip">${cred}</div>`
            ).join('');
        }
    }

    formatNumber(num) {
        if (typeof num !== 'number') return num;
        if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
        if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
        return num;
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

    loadTimeline() {
        const timeline = document.getElementById('profileTimeline');
        let posts = [];

        if (this.userId && this.mockPosts) {
            posts = this.mockPosts;
        } else {
            posts = JSON.parse(localStorage.getItem('profilePosts') || '[]');
        }

        if (posts.length === 0) {
            timeline.innerHTML = '<div class="profile-empty"><p>No posts yet.</p></div>';
            return;
        }

        timeline.innerHTML = '';
        posts.forEach(post => {
            const postElement = this.createPostElement(post);
            timeline.appendChild(postElement);
        });
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

