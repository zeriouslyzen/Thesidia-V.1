// Global Navigation Handler
(function() {
    'use strict';
    
    function initNavigation() {
        const menuBtn = document.getElementById('menuBtn');
        const globalNav = document.getElementById('globalNav');
        
        if (!menuBtn || !globalNav) return;
        
        // Toggle navigation menu
        menuBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            globalNav.classList.toggle('open');
        });
        
        // Close nav when clicking outside
        document.addEventListener('click', (e) => {
            if (!globalNav.contains(e.target) && !menuBtn.contains(e.target)) {
                globalNav.classList.remove('open');
            }
        });
        
        // Set active nav item based on current page
        setActiveNavItem();
    }
    
    function setActiveNavItem() {
        const navItems = document.querySelectorAll('.nav-item');
        const currentPath = window.location.pathname;
        
        navItems.forEach(item => {
            const href = item.getAttribute('href');
            // Remove active class first
            item.classList.remove('active');
            
            // Check if this is the current page
            if (href === currentPath || 
                (currentPath === '/' && (href === '/' || href === '/contexts.html')) ||
                (currentPath === '/contexts.html' && href === '/')) {
                item.classList.add('active');
            }
        });
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initNavigation);
    } else {
        initNavigation();
    }
})();

