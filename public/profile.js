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
        this.disciplineData = {
            martial: ['Kung Fu', 'Shaolin Arts', 'Qigong', 'Neigong', 'Karate', 'Taekwondo', 'Jeet Kune Do', 'Budo systems', 'Boxing', 'Muay Thai', 'Wrestling', 'Jiu-Jitsu', 'Weapons arts', 'Internal martial arts'],
            movement: ['Dance', 'Parkour', 'Freerunning', 'Acrobatics', 'Gymnastics', 'Capoeira', 'Yoga', 'Contemporary movement', 'Flow arts'],
            visual: ['Drawing', 'Painting', 'Sculpture', 'Calligraphy', 'Photography', 'Film', 'Animation', 'Architecture', 'Design', 'Crafts'],
            internal: ['Meditation', 'Pranayama', 'Breathwork', 'Qigong', 'Yoga', 'Shamanic practices', 'Ritual arts', 'Mystical arts'],
            performance: ['Theater', 'Spoken word', 'Poetry', 'Singing', 'Music', 'Ritual performance', 'Martial dance'],
            healing: ['Traditional Chinese Medicine', 'Acupuncture', 'Acupressure', 'Herbalism', 'Massage', 'Bodywork', 'Thai massage', 'Physical therapy', 'Energetic healing'],
            intellectual: ['Philosophy', 'Science', 'Mathematics', 'Language', 'Linguistics', 'Systems thinking', 'Strategy', 'Game theory'],
            creative: ['Invention', 'Engineering', 'Architecture', 'Programming', 'Alchemy', 'Machine-building', 'Mechanism design'],
            social: ['Rhetoric', 'Diplomacy', 'Teaching', 'Leadership', 'Community building', 'Psychosocial development']
        };
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
        const ttLink = document.getElementById('profileSocialTT');
        const lnLink = document.getElementById('profileSocialLN');
        if (igLink) igLink.href = profile.ig || profile.socialUrl || '#';
        if (xLink) xLink.href = profile.x || '#';
        if (fbLink) fbLink.href = profile.fb || '#';
        if (ttLink) ttLink.href = profile.tt || '#';
        if (lnLink) lnLink.href = profile.ln || profile.linkedin || '#';

        const avatar = profile.avatar_url || localStorage.getItem('profileImage');
        if (avatar) {
            document.getElementById('profilePictureImg').src = avatar;
        }

        // Role
        const roleEl = document.getElementById('profileRole');
        if (roleEl) {
            roleEl.textContent = profile.role || 'Practitioner';
        }

        // Disciplines (show max 2 as chips)
        const disciplinesEl = document.getElementById('profileDisciplines');
        if (disciplinesEl) {
            const savedData = JSON.parse(localStorage.getItem('profileData') || '{}');
            const disciplines = savedData.disciplines || this.getDisciplineLabels(profile.domains || []) || [];
            disciplinesEl.innerHTML = disciplines.slice(0, 2).map(l => `<span class="profile-discipline-chip">${l}</span>`).join('');
        }

        // Metrics labels and counts
        const savedData = JSON.parse(localStorage.getItem('profileData') || '{}');
        const friendsEl = document.getElementById('profileStatFriends');
        const fansEl = document.getElementById('profileStatFans');
        const resonatingEl = document.getElementById('profileStatResonating');
        const cutsEl = document.getElementById('profileStatCuts');
        
        if (friendsEl) {
            const labelEl = friendsEl.querySelector('span:last-child');
            if (labelEl) labelEl.textContent = savedData.metric1 || 'Friends';
            const countEl = document.getElementById('profileFriendsCount');
            if (countEl) countEl.textContent = savedData.friendsCount || profile.stats?.friends || '0';
        }
        if (fansEl) {
            const labelEl = fansEl.querySelector('span:last-child');
            if (labelEl) labelEl.textContent = savedData.metric2 || 'Fans';
            const countEl = document.getElementById('profileFansCount');
            if (countEl) countEl.textContent = savedData.fansCount || profile.stats?.fans || '0';
        }
        if (resonatingEl) {
            const labelEl = resonatingEl.querySelector('span:last-child');
            if (labelEl) labelEl.textContent = savedData.metric3 || 'Resonating';
            const countEl = document.getElementById('profileResonatingCount');
            if (countEl) countEl.textContent = savedData.resonatingCount || profile.stats?.resonating || '0';
        }
        if (cutsEl) {
            const labelEl = cutsEl.querySelector('span:last-child');
            if (labelEl) labelEl.textContent = savedData.metric4 || 'Cuts';
            const countEl = document.getElementById('profileCutsCount');
            if (countEl) countEl.textContent = savedData.cutsCount || profile.stats?.cuts || '0';
        }

        // Setup metric click handlers
        this.setupMetricPopouts();

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

        // Discipline dropdowns
        const categorySelect = document.getElementById('editDisciplineCategory');
        const subSelect = document.getElementById('editDisciplineSub');
        const disciplinesContainer = document.getElementById('editDisciplinesContainer');
        
        if (categorySelect && subSelect) {
            categorySelect.addEventListener('change', (e) => {
                const category = e.target.value;
                subSelect.innerHTML = '<option value="">Select discipline</option>';
                subSelect.disabled = !category;
                
                if (category && this.disciplineData[category]) {
                    this.disciplineData[category].forEach(sub => {
                        const option = document.createElement('option');
                        option.value = sub;
                        option.textContent = sub;
                        subSelect.appendChild(option);
                    });
                }
            });
            
            subSelect.addEventListener('change', (e) => {
                const value = e.target.value;
                if (value) {
                    const category = categorySelect.value;
                    const categoryCount = Array.from(disciplinesContainer.children).filter(tag => 
                        tag.dataset.category === category
                    ).length;
                    
                    if (categoryCount < 2 && disciplinesContainer.children.length < 4) {
                        this.addDisciplineTag(value, category);
                        subSelect.value = '';
                    } else if (categoryCount >= 2) {
                        alert('Maximum 2 disciplines per category');
                        subSelect.value = '';
                    }
                }
            });
        }

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
        const profile = this.profileData || {};
        
        // Populate form
        document.getElementById('editName').value = profileData.name || profile.display_name || profile.name || '';
        document.getElementById('editUsername').value = profileData.username || profile.username || '';
        document.getElementById('editTag').value = profileData.tag || '';
        document.getElementById('editBio').value = profileData.bio || profile.bio || '';
        document.getElementById('editLocation').value = profileData.location || profile.location || '';
        document.getElementById('editWebsite').value = profileData.website || profile.website || '';
        
        // Populate social media
        const igEl = document.getElementById('editSocialIG');
        const xEl = document.getElementById('editSocialX');
        const fbEl = document.getElementById('editSocialFB');
        const ttEl = document.getElementById('editSocialTT');
        const lnEl = document.getElementById('editSocialLN');
        if (igEl) igEl.value = profileData.ig || profile.ig || '';
        if (xEl) xEl.value = profileData.x || profile.x || '';
        if (fbEl) fbEl.value = profileData.fb || profile.fb || '';
        if (ttEl) ttEl.value = profileData.tt || profile.tt || '';
        if (lnEl) lnEl.value = profileData.ln || profile.ln || profile.linkedin || '';
        
        // Populate disciplines (clear first to remove leftovers)
        const disciplinesContainer = document.getElementById('editDisciplinesContainer');
        if (disciplinesContainer) {
            // Always clear first to remove any leftover tags
            disciplinesContainer.innerHTML = '';
            const disciplines = profileData.disciplines || this.getDisciplineLabels(profile.domains || []) || [];
            disciplines.forEach(d => {
                if (typeof d === 'string') {
                    // Find category for this discipline
                    let category = '';
                    for (const [cat, subs] of Object.entries(this.disciplineData)) {
                        if (subs.includes(d)) {
                            category = cat;
                            break;
                        }
                    }
                    this.addDisciplineTag(d, category);
                }
            });
        }
        
        // Reset discipline dropdowns
        const categorySelect = document.getElementById('editDisciplineCategory');
        const subSelect = document.getElementById('editDisciplineSub');
        if (categorySelect) categorySelect.value = '';
        if (subSelect) {
            subSelect.innerHTML = '<option value="">Select discipline</option>';
            subSelect.disabled = true;
        }
        
        // Populate metrics
        const metric1 = document.getElementById('editMetric1');
        const metric2 = document.getElementById('editMetric2');
        const metric3 = document.getElementById('editMetric3');
        const metric4 = document.getElementById('editMetric4');
        if (metric1) metric1.value = profileData.metric1 || 'Friends';
        if (metric2) metric2.value = profileData.metric2 || 'Fans';
        if (metric3) metric3.value = profileData.metric3 || 'Resonating';
        if (metric4) metric4.value = profileData.metric4 || 'Cuts';
        
        this.updateCharCount();
        modal.classList.add('open');
    }

    addDisciplineTag(value, category = '') {
        const container = document.getElementById('editDisciplinesContainer');
        if (!container) return;
        
        // Check if already added
        const existing = Array.from(container.children).some(tag => 
            tag.querySelector('span')?.textContent === value
        );
        if (existing) return;
        
        const tag = document.createElement('div');
        tag.className = 'edit-profile-discipline-tag';
        tag.dataset.category = category;
        tag.innerHTML = `
            <span>${this.escapeHtml(value)}</span>
            <button type="button" onclick="this.parentElement.remove()" aria-label="Remove">×</button>
        `;
        container.appendChild(tag);
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
        const disciplinesContainer = document.getElementById('editDisciplinesContainer');
        const disciplines = Array.from(disciplinesContainer?.children || []).map(tag => {
            const text = tag.querySelector('span')?.textContent || '';
            return text.trim();
        }).filter(Boolean);

        const profileData = {
            name: document.getElementById('editName').value.trim(),
            username: document.getElementById('editUsername').value.trim(),
            tag: document.getElementById('editTag').value.trim(),
            bio: document.getElementById('editBio').value.trim(),
            location: document.getElementById('editLocation').value.trim(),
            website: document.getElementById('editWebsite').value.trim(),
            ig: document.getElementById('editSocialIG')?.value.trim() || '',
            x: document.getElementById('editSocialX')?.value.trim() || '',
            fb: document.getElementById('editSocialFB')?.value.trim() || '',
            tt: document.getElementById('editSocialTT')?.value.trim() || '',
            ln: document.getElementById('editSocialLN')?.value.trim() || '',
            disciplines: disciplines,
            metric1: document.getElementById('editMetric1')?.value.trim() || 'Friends',
            metric2: document.getElementById('editMetric2')?.value.trim() || 'Fans',
            metric3: document.getElementById('editMetric3')?.value.trim() || 'Resonating',
            metric4: document.getElementById('editMetric4')?.value.trim() || 'Cuts'
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
            sec.classList.toggle('hidden', sec.dataset.tab !== tab);
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
                { title: 'Kinetic Loop Study', thumb: 'https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?auto=format&fit=crop&w=600&q=80', meta: '00:32' },
                { title: 'Chromatic Motion', thumb: 'https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=600&q=80', meta: '00:45' },
                { title: 'Lightfield Drift', thumb: 'https://images.unsplash.com/photo-1501004318641-b39e6451bec6?auto=format&fit=crop&w=600&q=80', meta: '00:28' },
                { title: 'Texture Bloom', thumb: 'https://images.unsplash.com/photo-1487412947147-5cebf100ffc2?auto=format&fit=crop&w=600&q=80', meta: '00:35' },
                { title: 'Micro Tutorial', thumb: 'https://images.unsplash.com/photo-1458530970867-aaa3700e966d?auto=format&fit=crop&w=600&q=80', meta: '00:40' }
            ],
            origin: {
                paragraphs: [
                    'I started with analog experiments, moved into digital motion, and now merge both. I focus on rhythmic timing, minimal palettes, and human-centered pacing.',
                    'The journey began in a small studio where I learned the fundamentals of motion through frame-by-frame animation. Over the years, I\'ve developed a unique approach that combines traditional techniques with modern digital tools, always prioritizing the emotional impact of movement.'
                ],
                images: [
                    'https://images.unsplash.com/photo-1526481280695-3c469c2f77f4?auto=format&fit=crop&w=300&q=80',
                    'https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=300&q=80'
                ]
            },
            education: {
                cert: { title: 'Motion Design Certification', org: 'School of Visual Arts', url: 'https://example.com/cert' },
                university: { title: 'BFA in Digital Media', org: 'Art Institute', url: 'https://example.com/uni' }
            },
            services: [
                { title: 'Motion Direction', desc: 'Full creative direction for motion projects' },
                { title: 'Workshop Facilitation', desc: 'Teaching kinetic design principles' }
            ],
            resume: { name: 'Aurora_Vale_CV.pdf', url: 'https://example.com/resume.pdf', uploaded: '2024-01-15' },
            reading: [
                { title: 'The Art of Looking Sideways', author: 'Alan Fletcher', url: 'https://example.com/book1', image: 'https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&w=300&q=80' },
                { title: 'Steal Like an Artist', author: 'Austin Kleon', url: 'https://example.com/book2', image: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=300&q=80' },
                { title: 'The Design of Everyday Things', author: 'Don Norman', url: 'https://example.com/book3', image: 'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?auto=format&fit=crop&w=300&q=80' },
                { title: 'Thinking, Fast and Slow', author: 'Daniel Kahneman', url: 'https://example.com/book4', image: 'https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=300&q=80' }
            ],
            disciplines: [
                'Vinyasa Yoga',
                'Meditation',
                'Breathwork',
                'Movement Flow'
            ],
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
            const defaultReelThumb = 'https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?auto=format&fit=crop&w=600&q=80';
            const reels = portfolio.reels && portfolio.reels.length ? portfolio.reels : defaultPortfolio.reels;
            reelsTrack.innerHTML = reels.map(r => `
                <div class="portfolio-reel-card">
                    <div class="portfolio-reel-thumb">${r.thumb || defaultReelThumb ? `<img src="${r.thumb || defaultReelThumb}" alt="${r.title}" loading="lazy" onerror="this.src='${defaultReelThumb}'; this.onerror=null;">` : ''}</div>
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

        // Origin with paragraphs and images
        const originEl = document.getElementById('portfolioOrigin');
        if (originEl) {
            const origin = portfolio.origin || defaultPortfolio.origin;
            const paragraphs = typeof origin === 'string' ? [origin] : (origin.paragraphs || defaultPortfolio.origin.paragraphs);
            const images = typeof origin === 'string' ? [] : (origin.images || defaultPortfolio.origin.images);
            
            let html = '';
            paragraphs.forEach((para, idx) => {
                html += `<p>${this.escapeHtml(para)}</p>`;
                // Insert images after first paragraph
                if (idx === 0 && images.length > 0) {
                    html += '<div class="portfolio-origin-images">';
                    images.forEach(img => {
                        html += `<img class="portfolio-origin-image" src="${img}" alt="Origin story" loading="lazy" onerror="this.style.display='none';">`;
                    });
                    html += '</div>';
                }
            });
            originEl.innerHTML = html;
            
            // Add click handlers for images
            originEl.querySelectorAll('.portfolio-origin-image').forEach(img => {
                img.addEventListener('click', () => this.openImagePopup(img.src));
            });
        }

        // Education
        const educationEl = document.getElementById('portfolioEducation');
        const educationWrap = document.getElementById('portfolioEducationContainer');
        if (educationEl && educationWrap) {
            const edu = portfolio.education || defaultPortfolio.education;
            if (edu && (edu.cert || edu.university)) {
                let html = '';
                if (edu.cert) {
                    html += `
                        <div class="portfolio-education-item">
                            <div class="portfolio-education-item-icon">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M22 10v6M2 10l10-5 10 5-10 5z"/>
                                    <path d="M6 12v5c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2v-5"/>
                                </svg>
                            </div>
                            <div class="portfolio-education-item-content">
                                <div class="portfolio-education-item-title">
                                    <a href="${edu.cert.url || '#'}" target="_blank">${this.escapeHtml(edu.cert.title)}</a>
                                </div>
                                <div class="portfolio-education-item-desc">${this.escapeHtml(edu.cert.org)}</div>
                            </div>
                        </div>
                    `;
                }
                if (edu.university) {
                    html += `
                        <div class="portfolio-education-item">
                            <div class="portfolio-education-item-icon">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
                                    <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
                                </svg>
                            </div>
                            <div class="portfolio-education-item-content">
                                <div class="portfolio-education-item-title">
                                    <a href="${edu.university.url || '#'}" target="_blank">${this.escapeHtml(edu.university.title)}</a>
                                </div>
                                <div class="portfolio-education-item-desc">${this.escapeHtml(edu.university.org)}</div>
                            </div>
                        </div>
                    `;
                }
                educationEl.innerHTML = html;
                educationWrap.style.display = 'block';
            } else {
                educationWrap.style.display = 'none';
            }
        }

        // Services
        const servicesEl = document.getElementById('portfolioServices');
        const servicesWrap = document.getElementById('portfolioServicesContainer');
        if (servicesEl && servicesWrap) {
            const services = portfolio.services || defaultPortfolio.services;
            if (services && services.length > 0) {
                servicesEl.innerHTML = services.slice(0, 2).map(s => `
                    <div class="portfolio-service-card">
                        <div class="portfolio-service-title">${this.escapeHtml(s.title)}</div>
                        <div class="portfolio-service-desc">${this.escapeHtml(s.desc)}</div>
                    </div>
                `).join('');
                servicesWrap.style.display = 'block';
            } else {
                servicesWrap.style.display = 'none';
            }
        }

        // Resume
        const resumeEl = document.getElementById('portfolioResume');
        const resumeWrap = document.getElementById('portfolioResumeContainer');
        if (resumeEl && resumeWrap) {
            const resume = portfolio.resume || defaultPortfolio.resume;
            if (resume && resume.name) {
                resumeEl.innerHTML = `
                    <div class="portfolio-resume-icon">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                            <polyline points="14 2 14 8 20 8"/>
                            <line x1="16" y1="13" x2="8" y2="13"/>
                            <line x1="16" y1="17" x2="8" y2="17"/>
                            <polyline points="10 9 9 9 8 9"/>
                        </svg>
                    </div>
                    <div class="portfolio-resume-info">
                        <div class="portfolio-resume-name">
                            <a href="${resume.url || '#'}" target="_blank">${this.escapeHtml(resume.name)}</a>
                        </div>
                        <div class="portfolio-resume-meta">Uploaded ${resume.uploaded || 'recently'}</div>
                    </div>
                    <button class="portfolio-resume-upload" onclick="document.getElementById('resumeUploadInput')?.click()">Upload new</button>
                `;
                resumeWrap.style.display = 'block';
            } else {
                resumeEl.innerHTML = `
                    <div class="portfolio-resume-icon">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12"/>
                        </svg>
                    </div>
                    <div class="portfolio-resume-info">
                        <div class="portfolio-resume-name">No resume uploaded</div>
                        <div class="portfolio-resume-meta">Upload your CV or resume</div>
                    </div>
                    <button class="portfolio-resume-upload" onclick="document.getElementById('resumeUploadInput')?.click()">Upload</button>
                `;
                resumeWrap.style.display = 'block';
            }
        }

        // Reading
        const readingEl = document.getElementById('portfolioReading');
        const readingWrap = document.getElementById('portfolioReadingContainer');
        if (readingEl && readingWrap) {
            const reading = portfolio.reading || defaultPortfolio.reading;
            if (reading && reading.length > 0) {
                readingEl.innerHTML = reading.slice(0, 4).map(r => `
                    <a href="${r.url || '#'}" target="_blank" class="portfolio-reading-item">
                        <div class="portfolio-reading-cover">
                            ${r.image ? `<img src="${r.image}" alt="${this.escapeHtml(r.title)}" loading="lazy" onerror="this.style.display='none';">` : ''}
                        </div>
                        <div class="portfolio-reading-title">${this.escapeHtml(r.title)}</div>
                        <div class="portfolio-reading-author">${this.escapeHtml(r.author)}</div>
                    </a>
                `).join('');
                readingWrap.style.display = 'block';
            } else {
                readingWrap.style.display = 'none';
            }
        }

        // Mind-Body Disciplines
        const disciplinesEl = document.getElementById('portfolioDisciplines');
        const disciplinesWrap = document.getElementById('portfolioDisciplinesContainer');
        if (disciplinesEl && disciplinesWrap) {
            const disciplines = portfolio.disciplines || defaultPortfolio.disciplines;
            if (disciplines && disciplines.length > 0) {
                disciplinesEl.innerHTML = disciplines.slice(0, 4).map(d => `
                    <div class="portfolio-discipline-chip">${this.escapeHtml(d)}</div>
                `).join('');
                disciplinesWrap.style.display = 'block';
            } else {
                disciplinesWrap.style.display = 'none';
            }
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

        // Setup edit button handlers
        this.setupPortfolioEditHandlers();
        
        // Setup image popup handlers
        this.setupImagePopup();
    }

    openImagePopup(src) {
        const modal = document.getElementById('imagePopupModal');
        const img = document.getElementById('imagePopupImg');
        if (modal && img) {
            img.src = src;
            modal.classList.add('open');
        }
    }

    setupImagePopup() {
        const modal = document.getElementById('imagePopupModal');
        const closeBtn = document.getElementById('imagePopupCloseBtn');
        const backdrop = document.getElementById('imagePopupClose');
        
        const close = () => modal?.classList.remove('open');
        
        if (closeBtn) closeBtn.addEventListener('click', close);
        if (backdrop) backdrop.addEventListener('click', close);
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && modal?.classList.contains('open')) close();
        });
    }

    setupMetricPopouts() {
        const friendsStat = document.getElementById('profileStatFriends');
        const fansStat = document.getElementById('profileStatFans');
        const resonatingStat = document.getElementById('profileStatResonating');
        const cutsStat = document.getElementById('profileStatCuts');
        
        if (friendsStat) friendsStat.addEventListener('click', () => this.openMetricPopout('friends'));
        if (fansStat) fansStat.addEventListener('click', () => this.openMetricPopout('fans'));
        if (resonatingStat) resonatingStat.addEventListener('click', () => this.openMetricPopout('resonating'));
        if (cutsStat) cutsStat.addEventListener('click', () => this.openMetricPopout('cuts'));

        const modal = document.getElementById('metricPopoutModal');
        const closeBtn = document.getElementById('metricPopoutCloseBtn');
        const backdrop = document.getElementById('metricPopoutClose');
        
        const close = () => modal?.classList.remove('open');
        
        if (closeBtn) closeBtn.addEventListener('click', close);
        if (backdrop) backdrop.addEventListener('click', close);
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && modal?.classList.contains('open')) close();
        });
    }

    openMetricPopout(type) {
        const modal = document.getElementById('metricPopoutModal');
        const titleEl = document.getElementById('metricPopoutTitle');
        const bodyEl = document.getElementById('metricPopoutBody');
        
        if (!modal || !titleEl || !bodyEl) return;

        const titles = {
            friends: 'Friends',
            fans: 'Fans',
            resonating: 'Resonating',
            cuts: 'Cuts'
        };

        titleEl.textContent = titles[type] || type;
        bodyEl.innerHTML = this.renderMetricContent(type);
        modal.classList.add('open');
    }

    renderMetricContent(type) {
        const mockProfiles = this.mockProfiles.slice(0, 10);
        
        if (type === 'friends') {
            const top5 = mockProfiles.slice(0, 5);
            const others = mockProfiles.slice(5);
            
            return `
                <div class="metric-popout-section">
                    <div class="metric-popout-section-title">Top 5 Friends</div>
                    <div class="metric-popout-profiles">
                        ${top5.map(p => this.renderProfileCard(p)).join('')}
                    </div>
                </div>
                ${others.length > 0 ? `
                <div class="metric-popout-section">
                    <div class="metric-popout-section-title">Others You Interact With</div>
                    <div class="metric-popout-profiles">
                        ${others.map(p => this.renderProfileCard(p)).join('')}
                    </div>
                </div>
                ` : ''}
            `;
        } else if (type === 'fans') {
            const top5 = mockProfiles.slice(0, 5);
            return `
                <div class="metric-popout-section">
                    <div class="metric-popout-section-title">Top 5 Fans</div>
                    <div class="metric-popout-profiles">
                        ${top5.map(p => this.renderProfileCard(p)).join('')}
                    </div>
                </div>
            `;
        } else if (type === 'resonating') {
            return `
                <div class="metric-popout-section">
                    <div class="metric-popout-section-title">People Who Resonate With You</div>
                    <div style="padding: 20px; text-align: center; color: var(--text-secondary);">
                        This shows people who have resonated with your content via resonate likes.
                    </div>
                </div>
            `;
        } else if (type === 'cuts') {
            const top5 = mockProfiles.slice(0, 5);
            return `
                <div class="metric-popout-section">
                    <div class="metric-popout-section-title">Your Top 5 Cuts</div>
                    <div class="metric-popout-profiles">
                        ${top5.map(p => this.renderProfileCard(p)).join('')}
                    </div>
                </div>
            `;
        }
        return '';
    }

    renderProfileCard(profile) {
        const avatar = profile.avatar_url || 'data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'40\' height=\'40\'%3E%3Crect width=\'40\' height=\'40\' rx=\'8\' fill=\'%23ffffff\' fill-opacity=\'0.06\'/%3E%3C/svg%3E';
        const name = profile.display_name || profile.name || 'User';
        const handle = profile.username || 'user';
        const userId = profile.user_id || '';
        
        return `
            <a href="/profile.html?user_id=${userId}" class="metric-popout-profile-card" onclick="document.getElementById('metricPopoutModal')?.classList.remove('open')">
                <div class="metric-popout-profile-avatar">
                    <img src="${avatar}" alt="${this.escapeHtml(name)}" onerror="this.src='data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'40\' height=\'40\'%3E%3Crect width=\'40\' height=\'40\' rx=\'8\' fill=\'%23ffffff\' fill-opacity=\'0.06\'/%3E%3C/svg%3E'">
                </div>
                <div class="metric-popout-profile-info">
                    <div class="metric-popout-profile-name">${this.escapeHtml(name)}</div>
                    <div class="metric-popout-profile-handle">//${this.escapeHtml(handle)}</div>
                </div>
            </a>
        `;
    }

    setupPortfolioEditHandlers() {
        document.querySelectorAll('.portfolio-edit-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const section = e.currentTarget.dataset.section;
                console.log('Edit section:', section);
                // TODO: Open edit modal for section
            });
        });
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

