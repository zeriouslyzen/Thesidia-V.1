/**
 * Navigation Module
 * Handles sidebar toggling, gestures, and active state management.
 */

export class Navigation {
    constructor(appInstance) {
        this.app = appInstance;
        this.sidebar = document.getElementById('leftSidebar');
        this.menuBtn = document.getElementById('menuBtn');
        this.overlay = document.getElementById('overlay');
    }

    init() {
        if (!this.sidebar || !this.menuBtn) return;

        this.menuBtn.addEventListener('click', () => this.toggleSidebar());
        if (this.overlay) {
            this.overlay.addEventListener('click', () => this.closeSidebar());
        }

        this.setupSwipeGestures();
        this.setupKeyboardShortcuts();
        this.highlightActiveNavItem();
    }

    toggleSidebar() {
        const isOpen = this.sidebar.classList.contains('open');
        if (isOpen) {
            this.closeSidebar();
        } else {
            this.openSidebar();
        }
    }

    openSidebar() {
        this.sidebar.classList.add('open');
        if (this.overlay) this.overlay.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    closeSidebar() {
        this.sidebar.classList.remove('open');
        if (this.overlay) this.overlay.classList.remove('active');
        document.body.style.overflow = '';
    }

    setupSwipeGestures() {
        let touchStartX = 0;
        let touchStartY = 0;

        document.addEventListener('touchstart', (e) => {
            touchStartX = e.touches[0].clientX;
            touchStartY = e.touches[0].clientY;
        }, { passive: true });

        document.addEventListener('touchend', (e) => {
            if (!touchStartX) return;
            const touchEndX = e.changedTouches[0].clientX;
            const touchEndY = e.changedTouches[0].clientY;
            const deltaX = touchEndX - touchStartX;
            const deltaY = Math.abs(touchEndY - touchStartY);

            if (Math.abs(deltaX) > 50 && Math.abs(deltaX) > deltaY) {
                if (deltaX > 0 && !this.sidebar.classList.contains('open')) {
                    this.openSidebar();
                } else if (deltaX < 0 && this.sidebar.classList.contains('open')) {
                    this.closeSidebar();
                }
            }
            touchStartX = 0;
        }, { passive: true });
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.sidebar.classList.contains('open')) {
                this.closeSidebar();
            }
        });
    }

    highlightActiveNavItem() {
        const path = window.location.pathname;
        let activeId = '';

        if (path === '/' || path.includes('index.html')) activeId = 'navThesidia';
        else if (path.includes('stream')) activeId = 'navStream';
        else if (path.includes('profile')) activeId = 'navProfile';
        else if (path.includes('archive')) activeId = 'navArchive';

        if (activeId) {
            const activeItem = document.getElementById(activeId);
            if (activeItem) activeItem.classList.add('active');
        }
    }
}
