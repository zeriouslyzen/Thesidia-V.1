/**
 * Katanx Landing Page
 * Animations, interactions, and particle effects
 */

(function() {
    'use strict';

    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    function init() {
        // Initialize core features
        initScrollAnimations();
        initSmoothScroll();
        initWidgetInteractions();
        
        // Initialize particles (can be disabled for performance)
        if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            initParticles();
        }
    }

    /**
     * Particle Background Effect
     * Optimized for performance with reduced particle count on mobile
     */
    function initParticles() {
        const canvas = document.getElementById('landingParticles');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        let particles = [];
        let animationFrameId;
        let isPaused = false;

        function resizeCanvas() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }

        function createParticle() {
            return {
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height,
                radius: Math.random() * 1.5 + 0.5,
                speedX: (Math.random() - 0.5) * 0.5,
                speedY: (Math.random() - 0.5) * 0.5,
                opacity: Math.random() * 0.5 + 0.2
            };
        }

        function initParticleArray() {
            // Reduce particle count on mobile for better performance
            const isMobile = window.innerWidth < 768;
            const density = isMobile ? 20000 : 15000;
            const particleCount = Math.floor((canvas.width * canvas.height) / density);
            particles = [];
            for (let i = 0; i < particleCount; i++) {
                particles.push(createParticle());
            }
        }

        function drawParticles() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#ffffff';

            particles.forEach(particle => {
                ctx.beginPath();
                ctx.arc(particle.x, particle.y, particle.radius, 0, Math.PI * 2);
                ctx.globalAlpha = particle.opacity;
                ctx.fill();
                ctx.globalAlpha = 1;
            });
        }

        function updateParticles() {
            particles.forEach(particle => {
                particle.x += particle.speedX;
                particle.y += particle.speedY;

                // Wrap around edges
                if (particle.x < 0) particle.x = canvas.width;
                if (particle.x > canvas.width) particle.x = 0;
                if (particle.y < 0) particle.y = canvas.height;
                if (particle.y > canvas.height) particle.y = 0;
            });
        }

        function animate() {
            if (isPaused) return;
            updateParticles();
            drawParticles();
            animationFrameId = requestAnimationFrame(animate);
        }

        function start() {
            resizeCanvas();
            initParticleArray();
            isPaused = false;
            animate();
        }

        function pause() {
            isPaused = true;
            if (animationFrameId) {
                cancelAnimationFrame(animationFrameId);
            }
        }

        // Pause when page is not visible (performance optimization)
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                pause();
            } else {
                start();
            }
        });

        // Handle resize with throttling
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                pause();
                start();
            }, 250);
        });

        start();
    }

    /**
     * Scroll-triggered Animations using Intersection Observer
     * Optimized with performance considerations
     */
    function initScrollAnimations() {
        // Check if IntersectionObserver is supported
        if (!('IntersectionObserver' in window)) {
            // Fallback: show all elements immediately
            document.querySelectorAll('.landing-widget, .landing-frontier-card, .landing-story-item').forEach(el => {
                el.classList.add('visible');
            });
            return;
        }

        const observerOptions = {
            root: null,
            rootMargin: '0px 0px -100px 0px',
            threshold: 0.1
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    // Unobserve after animation to improve performance
                    observer.unobserve(entry.target);
                }
            });
        }, observerOptions);

        // Observe widgets
        document.querySelectorAll('.landing-widget').forEach(widget => {
            observer.observe(widget);
        });

        // Observe frontier cards
        document.querySelectorAll('.landing-frontier-card').forEach(card => {
            observer.observe(card);
        });

        // Observe story items
        document.querySelectorAll('.landing-story-item').forEach(item => {
            observer.observe(item);
        });
    }

    /**
     * Smooth Scroll for Anchor Links
     */
    function initSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                const href = this.getAttribute('href');
                if (href === '#') return;

                const target = document.querySelector(href);
                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }

    /**
     * Widget Interactions
     */
    function initWidgetInteractions() {
        const widgets = document.querySelectorAll('.landing-widget');

        widgets.forEach(widget => {
            // Add hover effect enhancement
            widget.addEventListener('mouseenter', function() {
                this.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
            });

            // Pattern widget specific animation
            if (widget.dataset.widget === 'pattern') {
                const svg = widget.querySelector('.landing-pattern-svg');
                if (svg) {
                    widget.addEventListener('mouseenter', () => {
                        const lines = svg.querySelectorAll('.landing-pattern-line');
                        lines.forEach((line, index) => {
                            setTimeout(() => {
                                line.style.opacity = '0.6';
                                line.style.transition = 'opacity 0.3s ease';
                            }, index * 50);
                        });
                    });

                    widget.addEventListener('mouseleave', () => {
                        const lines = svg.querySelectorAll('.landing-pattern-line');
                        lines.forEach(line => {
                            line.style.opacity = '0.3';
                        });
                    });
                }
            }

            // Research widget flow animation
            if (widget.dataset.widget === 'research') {
                widget.addEventListener('mouseenter', () => {
                    const flow = widget.querySelector('.landing-research-flow');
                    if (flow) {
                        flow.style.animation = 'none';
                        setTimeout(() => {
                            flow.style.animation = '';
                        }, 10);
                    }
                });
            }

            // Community widget grid animation
            if (widget.dataset.widget === 'community') {
                widget.addEventListener('mouseenter', () => {
                    const placeholders = widget.querySelectorAll('.landing-creator-placeholder');
                    placeholders.forEach((placeholder, index) => {
                        setTimeout(() => {
                            placeholder.style.transform = 'scale(1.05)';
                            placeholder.style.transition = 'transform 0.2s ease';
                        }, index * 50);
                    });
                });

                widget.addEventListener('mouseleave', () => {
                    const placeholders = widget.querySelectorAll('.landing-creator-placeholder');
                    placeholders.forEach(placeholder => {
                        placeholder.style.transform = 'scale(1)';
                    });
                });
            }
        });
    }

    /**
     * Performance optimization: Reduce motion for users who prefer it
     * Also optimize for low-end devices
     */
    function applyPerformanceOptimizations() {
        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        const isLowEndDevice = navigator.hardwareConcurrency && navigator.hardwareConcurrency < 4;

        if (prefersReducedMotion || isLowEndDevice) {
            // Disable animations for users who prefer reduced motion or low-end devices
            document.documentElement.style.setProperty('--transition', 'none');
            document.querySelectorAll('.landing-widget, .landing-frontier-card, .landing-story-item').forEach(el => {
                el.style.animation = 'none';
            });

            // Disable particle animation on low-end devices
            if (isLowEndDevice) {
                const canvas = document.getElementById('landingParticles');
                if (canvas) {
                    canvas.style.display = 'none';
                }
            }
        }
    }

    // Apply optimizations on init
    applyPerformanceOptimizations();

})();

