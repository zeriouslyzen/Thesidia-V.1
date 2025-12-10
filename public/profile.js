// Profile Page Functionality
class ProfilePage {
    constructor() {
        this.currentCropType = null;
        this.userId = null;
        this.sessionId = null;
        this.mockProfiles = [];
        this.profileData = null;
        this.cropCanvas = null;
        this.cropImage = null;
        this.cropContext = null;
        this.init();
    }

    async ensureSession() {
        if (this.sessionId) return;
        try {
            const response = await fetch('/api/user/session', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({})
            });
            const data = await response.json();
            if (data.user_id && data.session_id) {
                this.userId = this.userId || data.user_id;
                this.sessionId = data.session_id;
                localStorage.setItem('thesidia_user_id', this.userId);
                localStorage.setItem('thesidia_session_id', this.sessionId);
            }
        } catch (error) {
            console.warn('Session bootstrap failed (mock mode is okay):', error);
        }
    }

    async loadMockProfiles() {
        try {
            const res = await fetch('/mock-profiles.json');
            const data = await res.json();
            this.mockProfiles = data.profiles || [];
        } catch (error) {
            console.warn('Could not load mock profiles', error);
            this.mockProfiles = [];
        }
    }

    getProfileFromMocks() {
        const targetId = this.getProfileUserId();
        const found = this.mockProfiles.find(p => p.user_id === targetId);
        if (found) return found;
        // Fallback to first mock
        return this.mockProfiles[0] || null;
    }

    stripProtocol(url) {
        return url.replace(/^https?:\/\//, '').replace(/^\/\//, '');
    }

    getDisciplineLabels(domains) {
        const map = {
            'movement': 'Movement Arts',
            'visual': 'Visual Arts',
            'music': 'Music & Sound',
            'sound': 'Music & Sound',
            'craft': 'Craft & Design',
            'design': 'Design',
            'performance': 'Performance',
            'writing': 'Writing',
            'ai': 'AI Systems',
            'systems': 'Systems',
            'physical': 'Physical Training'
        };
        return (domains || []).map(d => map[d] || d).filter(Boolean);
    }
    
    async init() {
        this.userId = this.getProfileUserId();
        this.sessionId = localStorage.getItem('thesidia_session_id');
        
        await this.ensureSession();
        await this.loadMockProfiles();
        this.loadProfileData();
        this.setupEventListeners();
        // Default to portfolio so it is visible in demo
        this.switchTab('portfolio');
    }

    loadProfileData() {
        const profile = this.getProfileFromMocks() || {};
        this.profileData = profile;
        
        document.getElementById('profileNameLarge').textContent = profile.display_name || profile.name || 'User';
        document.getElementById('profileUsernameLarge').textContent = `//${profile.username || 'user'}`;
        document.getElementById('profileBio').textContent = profile.bio || 'Exploring the depths of consciousness and pattern recognition. Building Thesidia.';
        
        if (profile.location) {
            document.getElementById('profileLocation').querySelector('span').textContent = profile.location;
        }
        
        if (profile.website) {
            const websiteLink = document.getElementById('profileWebsiteLink');
            const cleanUrl = this.stripProtocol(profile.website);
            websiteLink.textContent = `//${cleanUrl}`;
            websiteLink.href = profile.website.startsWith('http') ? profile.website : `https://${cleanUrl}`;
        }
        
        const igLink = document.getElementById('profileSocialIG');
        const xLink = document.getElementById('profileSocialX');
        const fbLink = document.getElementById('profileSocialFB');
        if (igLink) {
            igLink.href = profile.ig || profile.socialUrl || '#';
        }
        if (xLink) {
            xLink.href = profile.x || '#';
        }
        if (fbLink) {
            fbLink.href = profile.fb || '#';
        }

        const avatar = profile.avatar_url || localStorage.getItem('profileImage');
        if (avatar) {
            document.getElementById('profilePictureImg').src = avatar;
        }

        // Role
        const roleEl = document.getElementById('profileRole');
        if (roleEl) {
            roleEl.textContent = profile.role || 'Practitioner';
        }

        // Disciplines (show max 2)
        const disciplinesEl = document.getElementById('profileDisciplines');
        if (disciplinesEl) {
            const labels = this.getDisciplineLabels(profile.domains || profile.disciplines || []);
            disciplinesEl.innerHTML = labels.slice(0, 2).map(l => `<span class="profile-discipline-chip">${l}</span>`).join('');
        }

        // Stats
        document.getElementById('profileFollowingCount').textContent = profile.stats?.following ?? '0';
        document.getElementById('profileFollowersCount').textContent = profile.stats?.followers ?? '0';
        document.getElementById('profilePostsCount').textContent = profile.posts ? profile.posts.length : '0';

        // Sidebar sync
        const sidebarName = document.getElementById('sidebarProfileNameProfile');
        const sidebarTag = document.getElementById('sidebarProfileTagProfile');
        if (sidebarName) sidebarName.textContent = profile.display_name || profile.name || 'User';
        if (sidebarTag) sidebarTag.textContent = `//${profile.username || 'user'}`;
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

        // Avatar shape toggle removed (default rectangle)
    }

    openEditModal() {
        const modal = document.getElementById('editProfileModal');
        const profileData = JSON.parse(localStorage.getItem('profileData') || '{}');
        
        // Populate form
        document.getElementById('editName').value = profileData.name || profileData.display_name || '';
        document.getElementById('editUsername').value = profileData.username || '';
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
        document.querySelectorAll('.profile-nav-item').forEach(i => {
            i.classList.toggle('active', i.dataset.tab === tab);
        });
        document.querySelectorAll('.tab-section').forEach(sec => {
            sec.style.display = sec.dataset.tab === tab ? 'block' : 'none';
        });
        if (tab === 'stream') {
            this.loadTimeline();
        } else if (tab === 'portfolio') {
            this.renderPortfolio();
        }
    }

    async loadTimeline() {
        const timeline = document.getElementById('profileTimeline');
        if (!timeline) return;
        
        const posts = this.profileData?.posts || [];
        if (posts.length === 0) {
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
            return;
        }
        
        timeline.innerHTML = '';
        posts.forEach(post => {
            const postElement = this.createPostElement(post);
            timeline.appendChild(postElement);
        });
        
        const postsCountEl = document.getElementById('profilePostsCount');
        if (postsCountEl) {
            postsCountEl.textContent = posts.length;
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
        const avatar = post.avatar || this.profileData?.avatar_url || "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='48' height='48'%3E%3Ccircle cx='24' cy='24' r='24' fill='%23ffffff' fill-opacity='0.1'/%3E%3Ccircle cx='24' cy='18' r='7' fill='%23ffffff' fill-opacity='0.3'/%3E%3Cpath d='M12 46 Q24 38 36 46' stroke='%23ffffff' stroke-width='2' fill='none' stroke-opacity='0.3'/%3E%3C/svg%3E";
        
        div.innerHTML = `
            <div class="profile-post-header">
                <div class="profile-post-avatar">
                    <img src="${avatar}" alt="Profile">
                </div>
                <div class="profile-post-info">
                    <div class="profile-post-author">
                        <span class="profile-post-author-name">${post.authorName || post.author?.display_name || this.profileData?.display_name || 'User'}</span>
                        <span class="profile-post-author-handle">//${post.authorHandle || post.author?.username || this.profileData?.username || 'user'}</span>
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

    renderPortfolio() {
        const profile = this.profileData || {};
        const defaultPortfolio = {
            summary: `${profile.display_name || 'Creator'} focuses on modern, expressive work with tight craft.`,
            reels: [
                { title: 'Kinetic Loop Study', thumb: 'https://images.unsplash.com/photo-1526481280695-3c469c2f77f4?auto=format&fit=crop&w=600&q=60', meta: '00:32' },
                { title: 'Palette Motion', thumb: 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=600&q=60', meta: '00:45' },
                { title: 'Lighting Drill', thumb: 'https://images.unsplash.com/photo-1478720568477-152d9b164e26?auto=format&fit=crop&w=600&q=60', meta: '00:28' },
                { title: 'Texture Study', thumb: 'https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=600&q=60', meta: '00:35' },
                { title: 'Micro-tutorial', thumb: 'https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=600&q=60', meta: '00:40' }
            ],
            origin: profile.origin || `I started with analog experiments, moved into digital motion, and now merge both. I focus on rhythmic timing, minimal palettes, and human-centered pacing.`,
            links: [
                { type: 'Studio', title: 'Studio North', desc: 'Boutique motion & sound lab', url: 'https://example.com' },
                { type: 'Location', title: 'Barcelona Residency', desc: 'Artist-in-residence space', url: 'https://example.com' },
                { type: 'Gym', title: 'Movement Lab', desc: 'Physical prep & conditioning', url: 'https://example.com' }
            ],
            credentials: [
                'Motion Design 10y', 'Analog Processes', 'Lighting Systems', 'Creative Direction', 'Workshop Lead'
            ]
        };

        const portfolio = profile.portfolio || defaultPortfolio;

        const titleEl = document.getElementById('portfolioTitle');
        const subtitleEl = document.getElementById('portfolioSubtitle');
        if (titleEl) titleEl.textContent = `${profile.display_name || 'Creator'} · Portfolio`;
        if (subtitleEl) subtitleEl.textContent = portfolio.summary || defaultPortfolio.summary;

        // Reels
        const reelsTrack = document.getElementById('reelsTrack');
        if (reelsTrack) {
            const reels = portfolio.reels && portfolio.reels.length ? portfolio.reels : defaultPortfolio.reels;
            reelsTrack.innerHTML = reels.map(r => `
                <div class="portfolio-reel-card">
                    <div class="portfolio-reel-thumb">${r.thumb ? `<img src="${r.thumb}" alt="${r.title}" loading="lazy" onerror="this.style.display='none';">` : ''}</div>
                    <div class="portfolio-reel-title">${r.title || ''}</div>
                    <div class="portfolio-reel-meta">${r.meta || ''}</div>
                </div>
            `).join('');

            const trackEl = reelsTrack;
            const prev = document.getElementById('reelsPrev');
            const next = document.getElementById('reelsNext');
            const scrollAmount = 260;
            if (prev && next) {
                prev.onclick = () => trackEl.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
                next.onclick = () => trackEl.scrollBy({ left: scrollAmount, behavior: 'smooth' });
            }
        }

        // Origin
        const originEl = document.getElementById('portfolioOrigin');
        if (originEl) {
            originEl.textContent = portfolio.origin || defaultPortfolio.origin;
        }

        // Links
        const linksContainer = document.getElementById('portfolioLinks');
        const linksWrapper = document.getElementById('portfolioLinksContainer');
        const links = portfolio.links && portfolio.links.length ? portfolio.links : defaultPortfolio.links;
        if (linksContainer && linksWrapper) {
            linksContainer.innerHTML = links.map(l => `
                <a class="portfolio-link-card" href="${l.url || '#'}" target="_blank">
                    <div class="portfolio-link-badge">${l.type || 'Link'}</div>
                    <div class="portfolio-link-title">${l.title || ''}</div>
                    <div class="portfolio-link-desc">${l.desc || ''}</div>
                </a>
            `).join('');
            linksWrapper.style.display = links.length ? 'block' : 'none';
        }

        // Credentials
        const credsEl = document.getElementById('portfolioCredentials');
        const credsWrap = document.getElementById('portfolioCredentialsContainer');
        const creds = portfolio.credentials && portfolio.credentials.length ? portfolio.credentials : defaultPortfolio.credentials;
        if (credsEl && credsWrap) {
            credsEl.innerHTML = creds.map(c => `<span class="portfolio-credential-chip">${c}</span>`).join('');
            credsWrap.style.display = creds.length ? 'block' : 'none';
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

