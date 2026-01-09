/**
 * KIM Safe Integration Wrapper
 * Ensures KIM integrates safely with existing Katanx functionality
 */

(function() {
    'use strict';
    
    // Check if we're on a page that should have KIM
    const KIM_ENABLED_PAGES = ['stream', 'stream.html', 'kim-sidebar.html', 'kim.html'];
    const currentPage = window.location.pathname.split('/').pop();
    
    if (!KIM_ENABLED_PAGES.includes(currentPage)) {
        console.log('KIM: Not enabled on this page');
        return;
    }
    
    // Wait for DOM to be fully loaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initKIM);
    } else {
        // DOM already loaded
        initKIM();
    }
    
    function initKIM() {
        // Check if KIM elements exist
        const kimPanel = document.getElementById('kimSidebarPanel');
        const kimToggleBtn = document.getElementById('kimToggleBtn');
        
        if (!kimPanel || !kimToggleBtn) {
            console.log('KIM: Elements not found, KIM disabled');
            return;
        }
        
        // Check if Socket.IO is available
        if (typeof io === 'undefined') {
            console.error('KIM: Socket.IO not loaded');
            return;
        }
        
        // Check if KIMCrypto is available
        if (typeof KIMCrypto === 'undefined') {
            console.error('KIM: KIMCrypto not loaded');
            return;
        }
        
        // Initialize KIM with error handling
        try {
            // Ensure KIM panel starts hidden - remove open class, let CSS handle visibility
            kimPanel.classList.remove('open');
            // CSS .kim-sidebar-panel:not(.open) will handle visibility
            
            // Set up safe toggle handler
            setupSafeToggle(kimToggleBtn, kimPanel);
            
            // Set up safe close handler
            const kimPanelClose = document.getElementById('kimPanelClose');
            if (kimPanelClose) {
                setupSafeClose(kimPanelClose, kimPanel, kimToggleBtn);
            }
            
            // Handle Escape key safely (don't conflict with other panels)
            setupSafeEscapeHandler(kimPanel);
            
            // Handle click outside safely
            setupSafeClickOutside(kimPanel, kimToggleBtn);
            
            // Prevent conflicts with notepad panel
            preventPanelConflicts(kimPanel);
            
            console.log('KIM: Safe integration initialized');
        } catch (error) {
            console.error('KIM: Initialization error:', error);
            // Hide KIM if initialization fails
            if (kimPanel) {
                kimPanel.style.display = 'none';
            }
            if (kimToggleBtn) {
                kimToggleBtn.style.display = 'none';
            }
        }
    }
    
    function setupSafeToggle(toggleBtn, panel) {
        if (!toggleBtn || !panel) return;
        
        // Remove any existing handlers
        const newToggleBtn = toggleBtn.cloneNode(true);
        toggleBtn.parentNode.replaceChild(newToggleBtn, toggleBtn);
        
        newToggleBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            console.log('KIM: Toggle button clicked');

            // Close other panels first (notepad)
            const notepadPanel = document.getElementById('starNotepadPanel');
            if (notepadPanel && notepadPanel.classList.contains('open')) {
                notepadPanel.classList.remove('open');
            }

            // Toggle KIM panel
            const isOpen = panel.classList.contains('open');
            if (isOpen) {
                closeKIMPanel(panel, newToggleBtn);
            } else {
                openKIMPanel(panel, newToggleBtn);
            }
        });
    }
    
    function setupSafeClose(closeBtn, panel, toggleBtn) {
        if (!closeBtn || !panel) return;
        
        closeBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            closeKIMPanel(panel, toggleBtn);
        });
    }
    
    function setupSafeEscapeHandler(panel) {
        // Use a unique handler that checks for KIM panel specifically
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && panel && panel.classList.contains('open')) {
                // Only close if KIM is open and no other modal is active
                const hasActiveModal = document.querySelector('.modal.active, .dialog.active');
                if (!hasActiveModal) {
                    e.stopPropagation(); // Prevent other handlers from firing
                    closeKIMPanel(panel, document.getElementById('kimToggleBtn'));
                }
            }
        }, true); // Use capture phase to handle before other handlers
    }
    
    function setupSafeClickOutside(panel, toggleBtn) {
        document.addEventListener('click', function(e) {
            if (!panel || !panel.classList.contains('open')) return;
            
            // Don't close if clicking inside panel or toggle button
            if (panel.contains(e.target) || (toggleBtn && toggleBtn.contains(e.target))) {
                return;
            }
            
            // Don't close if clicking on other interactive elements
            if (e.target.closest('button, a, input, textarea, select')) {
                // Check if it's notepad button
                const notepadBtn = e.target.closest('#starNotepadBtn');
                if (notepadBtn) {
                    // Close KIM when opening notepad
                    closeKIMPanel(panel, toggleBtn);
                }
                return;
            }
            
            // Close KIM panel
            closeKIMPanel(panel, toggleBtn);
        });
    }
    
    function preventPanelConflicts(kimPanel) {
        // No conflicts to prevent - notepad removed, KIM is the only panel
        console.log('KIM: No panel conflicts to monitor');
    }
    
    function openKIMPanel(panel, toggleBtn) {
        if (!panel) return;

        panel.classList.add('open');
        // CSS .kim-sidebar-panel.open will handle visibility and positioning

        if (toggleBtn) {
            toggleBtn.classList.add('active');
        }

        // Prevent body scroll when KIM is open
        document.body.style.overflow = 'hidden';
        
        // Focus on input if available
        setTimeout(() => {
            const nicknameInput = document.getElementById('kim-nickname-input');
            const messageInput = document.getElementById('kim-message-input');
            const inputToFocus = nicknameInput && !nicknameInput.closest('.hidden') 
                ? nicknameInput 
                : messageInput;
            if (inputToFocus) {
                inputToFocus.focus();
            }
        }, 100);
    }
    
    function closeKIMPanel(panel, toggleBtn) {
        if (!panel) return;
        
        panel.classList.remove('open');
        panel.style.visibility = 'hidden';
        
        if (toggleBtn) {
            toggleBtn.classList.remove('active');
        }
        
        // Restore body scroll
        document.body.style.overflow = '';
    }
    
    // Expose safe API for external use
    window.KIMIntegration = {
        open: function() {
            const panel = document.getElementById('kimSidebarPanel');
            const toggleBtn = document.getElementById('kimToggleBtn');
            if (panel) openKIMPanel(panel, toggleBtn);
        },
        close: function() {
            const panel = document.getElementById('kimSidebarPanel');
            const toggleBtn = document.getElementById('kimToggleBtn');
            if (panel) closeKIMPanel(panel, toggleBtn);
        },
        toggle: function() {
            const panel = document.getElementById('kimSidebarPanel');
            const toggleBtn = document.getElementById('kimToggleBtn');
            if (panel) {
                if (panel.classList.contains('open')) {
                    closeKIMPanel(panel, toggleBtn);
                } else {
                    openKIMPanel(panel, toggleBtn);
                }
            }
        }
    };
})();

