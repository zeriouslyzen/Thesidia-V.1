/**
 * Katanx Landing Page - Advanced Interactive Experience
 * Enterprise-level animations, AI demos, and interactive features
 */

(function() {
    'use strict';

    // Global state management
    const state = {
        isLoaded: false,
        animations: new Map(),
        observers: new Map(),
        canvases: new Map(),
        timers: new Set()
    };

    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    function init() {
        if (state.isLoaded) return;
        state.isLoaded = true;

        // Initialize all systems
        initPerformanceMonitoring();
        initCanvasSystems();
        initAnimationSystems();
        initInteractionSystems();
        initAISystems();
        initResponsiveSystems();

        // Start render loop
        requestAnimationFrame(render);

        console.log('🚀 Katanx Landing Page initialized');
    }

    // Performance monitoring
    function initPerformanceMonitoring() {
        if ('performance' in window && 'mark' in performance) {
            performance.mark('landing-init-start');
        }

        // Monitor memory usage
        if ('memory' in performance) {
            setInterval(() => {
                const memInfo = performance.memory;
                console.log(`Memory: ${Math.round(memInfo.usedJSHeapSize / 1048576)}MB used`);
            }, 10000);
        }
    }

    // Canvas systems
    function initCanvasSystems() {
        // Hero canvas
        const heroCanvas = document.getElementById('heroCanvas');
        if (heroCanvas) {
            const system = new CanvasParticleSystem(heroCanvas, {
                particleCount: 100,
                colors: ['#00d4ff', '#ff6b6b', '#4ecdc4'],
                connectionDistance: 120,
                speed: 0.3
            });
            state.canvases.set('hero', system);
        }

        // AI demo canvas
        const aiCanvas = document.getElementById('aiDemoCanvas');
        if (aiCanvas) {
            const system = new AIVisualizationSystem(aiCanvas);
            state.canvases.set('ai', system);
        }
    }

    // Animation systems
    function initAnimationSystems() {
        // Scroll-triggered animations
        initScrollAnimations();

        // Floating animations
        initFloatingAnimations();

        // Typewriter effects
        initTypewriterEffects();
    }

    // Interaction systems
    function initInteractionSystems() {
        // Card hover effects
        initCardInteractions();

        // Navigation effects
        initNavigationEffects();

        // Button interactions
        initButtonEffects();
    }

    // AI systems
    function initAISystems() {
        // AI demo interaction
        initAIDemo();

        // Pattern visualization
        initPatternVisualization();
    }

    // Responsive systems
    function initResponsiveSystems() {
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(handleResize, 250);
        });

        function handleResize() {
            // Update canvas sizes
            state.canvases.forEach(system => {
                if (system.resize) system.resize();
            });

            // Reinitialize scroll animations
            initScrollAnimations();
        }
    }

    // Main render loop
    function render(timestamp) {
        // Update all canvas systems
        state.canvases.forEach(system => {
            if (system.update && system.draw) {
                system.update(timestamp);
                system.draw();
            }
        });

        // Update animations
        updateAnimations(timestamp);

        requestAnimationFrame(render);
    }

    function updateAnimations(timestamp) {
        state.animations.forEach((animation, key) => {
            if (animation.update) {
                animation.update(timestamp);
            }
        });
    }

    // Canvas Particle System
    class CanvasParticleSystem {
        constructor(canvas, options = {}) {
            this.canvas = canvas;
            this.ctx = canvas.getContext('2d');
            this.options = {
                particleCount: 50,
                colors: ['#00d4ff', '#ff6b6b', '#4ecdc4'],
                connectionDistance: 100,
                speed: 0.5,
                ...options
            };

            this.particles = [];
            this.animationId = null;

            this.resize();
            this.initParticles();
            this.start();
        }

        resize() {
            const rect = this.canvas.getBoundingClientRect();
            this.canvas.width = rect.width * window.devicePixelRatio;
            this.canvas.height = rect.height * window.devicePixelRatio;
            this.ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
            this.canvas.style.width = rect.width + 'px';
            this.canvas.style.height = rect.height + 'px';
        }

        initParticles() {
            this.particles = [];
            for (let i = 0; i < this.options.particleCount; i++) {
                this.particles.push({
                    x: Math.random() * this.canvas.offsetWidth,
                    y: Math.random() * this.canvas.offsetHeight,
                    vx: (Math.random() - 0.5) * this.options.speed,
                    vy: (Math.random() - 0.5) * this.options.speed,
                    radius: Math.random() * 2 + 1,
                    alpha: Math.random() * 0.5 + 0.1,
                    color: this.options.colors[Math.floor(Math.random() * this.options.colors.length)]
                });
            }
        }

        update() {
            this.particles.forEach(particle => {
                particle.x += particle.vx;
                particle.y += particle.vy;

                // Bounce off edges
                if (particle.x < 0 || particle.x > this.canvas.offsetWidth) particle.vx *= -1;
                if (particle.y < 0 || particle.y > this.canvas.offsetHeight) particle.vy *= -1;
            });
        }

        draw() {
            this.ctx.clearRect(0, 0, this.canvas.offsetWidth, this.canvas.offsetHeight);

            // Draw particles
            this.particles.forEach(particle => {
                this.ctx.beginPath();
                this.ctx.arc(particle.x, particle.y, particle.radius, 0, Math.PI * 2);
                this.ctx.fillStyle = particle.color;
                this.ctx.globalAlpha = particle.alpha;
                this.ctx.fill();
                this.ctx.globalAlpha = 1;
            });

            // Draw connections
            this.ctx.strokeStyle = 'rgba(0, 212, 255, 0.1)';
            this.ctx.lineWidth = 0.5;

            for (let i = 0; i < this.particles.length; i++) {
                for (let j = i + 1; j < this.particles.length; j++) {
                    const dx = this.particles[i].x - this.particles[j].x;
                    const dy = this.particles[i].y - this.particles[j].y;
                    const dist = Math.sqrt(dx * dx + dy * dy);

                    if (dist < this.options.connectionDistance) {
                        this.ctx.beginPath();
                        this.ctx.moveTo(this.particles[i].x, this.particles[i].y);
                        this.ctx.lineTo(this.particles[j].x, this.particles[j].y);
                        this.ctx.stroke();
                    }
                }
            }
        }

        start() {
            if (this.animationId) cancelAnimationFrame(this.animationId);
            this.animate();
        }

        animate() {
            this.update();
            this.draw();
            this.animationId = requestAnimationFrame(() => this.animate());
        }

        destroy() {
            if (this.animationId) {
                cancelAnimationFrame(this.animationId);
            }
        }
    }

    // AI Visualization System
    class AIVisualizationSystem {
        constructor(canvas) {
            this.canvas = canvas;
            this.ctx = canvas.getContext('2d');
            this.nodes = [];
            this.connections = [];
            this.thinking = false;

            this.resize();
            this.initNodes();
        }

        resize() {
            const rect = this.canvas.getBoundingClientRect();
            this.canvas.width = rect.width;
            this.canvas.height = rect.height;
        }

        initNodes() {
            this.nodes = [];
            const centerX = this.canvas.width / 2;
            const centerY = this.canvas.height / 2;
            const radius = Math.min(this.canvas.width, this.canvas.height) * 0.3;

            // Create nodes in a circle
            for (let i = 0; i < 8; i++) {
                const angle = (i / 8) * Math.PI * 2 - Math.PI / 2;
                this.nodes.push({
                    x: centerX + Math.cos(angle) * radius,
                    y: centerY + Math.sin(angle) * radius,
                    radius: 8,
                    active: false,
                    pulse: 0
                });
            }

            // Central node
            this.nodes.push({
                x: centerX,
                y: centerY,
                radius: 12,
                active: true,
                pulse: 0
            });
        }

        startThinking() {
            this.thinking = true;
            this.nodes.forEach((node, i) => {
                setTimeout(() => {
                    node.active = true;
                    setTimeout(() => {
                        node.active = false;
                    }, 2000);
                }, i * 200);
            });

            setTimeout(() => {
                this.thinking = false;
            }, 3000);
        }

        update(timestamp) {
            this.nodes.forEach(node => {
                if (node.active) {
                    node.pulse = Math.sin(timestamp * 0.01) * 0.5 + 0.5;
                    node.radius = 8 + node.pulse * 4;
                } else {
                    node.radius = 8;
                    node.pulse = 0;
                }
            });
        }

        draw() {
            this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

            // Draw connections
            this.ctx.strokeStyle = this.thinking ? 'rgba(0, 212, 255, 0.6)' : 'rgba(0, 212, 255, 0.2)';
            this.ctx.lineWidth = this.thinking ? 2 : 1;

            const centerNode = this.nodes[this.nodes.length - 1];
            this.nodes.slice(0, -1).forEach(node => {
                this.ctx.beginPath();
                this.ctx.moveTo(centerNode.x, centerNode.y);
                this.ctx.lineTo(node.x, node.y);
                this.ctx.stroke();
            });

            // Draw nodes
            this.nodes.forEach(node => {
                this.ctx.beginPath();
                this.ctx.arc(node.x, node.y, node.radius, 0, Math.PI * 2);
                this.ctx.fillStyle = node.active ? '#00d4ff' : 'rgba(0, 212, 255, 0.5)';
                this.ctx.fill();

                if (node.active) {
                    this.ctx.beginPath();
                    this.ctx.arc(node.x, node.y, node.radius + 4, 0, Math.PI * 2);
                    this.ctx.strokeStyle = 'rgba(0, 212, 255, 0.3)';
                    this.ctx.stroke();
                }
            });
        }
    }

    // Scroll animations
    function initScrollAnimations() {
        // Clear existing observers
        state.observers.forEach(observer => observer.disconnect());
        state.observers.clear();

        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -100px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in', 'visible');

                    // Add stagger effect for grid items
                    if (entry.target.classList.contains('grid-card')) {
                        const cards = Array.from(entry.target.parentElement.children);
                        const index = cards.indexOf(entry.target);
                        entry.target.style.animationDelay = `${index * 0.1}s`;
                    }

                    observer.unobserve(entry.target);
                }
            });
        }, observerOptions);

        document.querySelectorAll('.grid-card, .section-header, .hero-stats, .capability-item').forEach(el => {
            el.classList.remove('fade-in', 'visible');
            observer.observe(el);
        });

        state.observers.set('scroll', observer);
    }

    // Floating animations
    function initFloatingAnimations() {
        document.querySelectorAll('.grid-card').forEach((card, index) => {
            const animation = {
                element: card,
                startTime: Date.now() + index * 1000,
                duration: 4000,
                update: function(timestamp) {
                    const elapsed = (timestamp - this.startTime) % this.duration;
                    const progress = elapsed / this.duration;
                    const yOffset = Math.sin(progress * Math.PI * 2) * 5;

                    this.element.style.transform = `translateY(${yOffset}px)`;
                }
            };

            state.animations.set(`float-${index}`, animation);
        });
    }

    // Typewriter effects
    function initTypewriterEffects() {
        const elements = document.querySelectorAll('[data-typewriter]');

        elements.forEach(element => {
            const text = element.textContent;
            element.textContent = '';
            element.style.borderRight = '2px solid #00d4ff';

            let i = 0;
            const timer = setInterval(() => {
                if (i < text.length) {
                    element.textContent += text.charAt(i);
                    i++;
                } else {
                    clearInterval(timer);
                    element.style.borderRight = 'none';
                    state.timers.delete(timer);
                }
            }, 50);

            state.timers.add(timer);
        });
    }

    // Card interactions
    function initCardInteractions() {
        document.querySelectorAll('.grid-card').forEach(card => {
            card.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-10px) scale(1.02)';
                this.style.boxShadow = '0 20px 40px rgba(0, 212, 255, 0.2)';

                // Add particle effect
                createParticleBurst(this);
            });

            card.addEventListener('mouseleave', function() {
                this.style.transform = '';
                this.style.boxShadow = '';
            });
        });
    }

    // Particle burst effect
    function createParticleBurst(element) {
        const rect = element.getBoundingClientRect();
        const centerX = rect.left + rect.width / 2;
        const centerY = rect.top + rect.height / 2;

        for (let i = 0; i < 10; i++) {
            const particle = document.createElement('div');
            particle.style.cssText = `
                position: fixed;
                width: 4px;
                height: 4px;
                background: #00d4ff;
                border-radius: 50%;
                pointer-events: none;
                z-index: 1000;
                left: ${centerX}px;
                top: ${centerY}px;
                animation: particleBurst 1s ease-out forwards;
            `;

            const angle = (i / 10) * Math.PI * 2;
            const distance = 50 + Math.random() * 50;
            particle.style.setProperty('--tx', Math.cos(angle) * distance + 'px');
            particle.style.setProperty('--ty', Math.sin(angle) * distance + 'px');

            document.body.appendChild(particle);

            setTimeout(() => {
                document.body.removeChild(particle);
            }, 1000);
        }

        // Add CSS animation if not exists
        if (!document.getElementById('particleBurstStyle')) {
            const style = document.createElement('style');
            style.id = 'particleBurstStyle';
            style.textContent = `
                @keyframes particleBurst {
                    0% {
                        opacity: 1;
                        transform: translate(0, 0) scale(1);
                    }
                    100% {
                        opacity: 0;
                        transform: translate(var(--tx), var(--ty)) scale(0);
                    }
                }
            `;
            document.head.appendChild(style);
        }
    }

    // Navigation effects
    function initNavigationEffects() {
        const nav = document.querySelector('.nav');

        window.addEventListener('scroll', () => {
            if (window.scrollY > 100) {
                nav.style.background = 'rgba(0, 0, 0, 0.9)';
                nav.style.backdropFilter = 'blur(20px)';
            } else {
                nav.style.background = 'rgba(0, 0, 0, 0.8)';
            }
        });
    }

    // Button effects
    function initButtonEffects() {
        document.querySelectorAll('.cta-primary, .cta-secondary').forEach(button => {
            button.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-2px)';
            });

            button.addEventListener('mouseleave', function() {
                this.style.transform = '';
            });
        });
    }

    // AI demo
    function initAIDemo() {
        const input = document.getElementById('demoInput');
        const submit = document.getElementById('demoSubmit');
        const text = document.getElementById('demoText');
        const canvas = document.getElementById('aiDemoCanvas');

        if (!input || !submit || !text) return;

        const aiSystem = state.canvases.get('ai');

        const responses = [
            "Analyzing patterns across human development disciplines...",
            "I detect structural similarities between martial arts and leadership theory...",
            "Cross-domain analysis reveals isomorphic patterns in quantum physics and traditional medicine...",
            "Searching knowledge bases for interdisciplinary connections...",
            "Synthesis complete. Here are the emergent patterns..."
        ];

        function simulateAIResponse() {
            const query = input.value.trim();
            if (!query) return;

            // Start thinking animation
            if (aiSystem) aiSystem.startThinking();

            text.textContent = "🧠 Processing your question...";
            input.disabled = true;
            submit.disabled = true;

            setTimeout(() => {
                const response = responses[Math.floor(Math.random() * responses.length)];
                text.textContent = response;
                input.disabled = false;
                submit.disabled = false;
                input.value = '';
            }, 2500);
        }

        submit.addEventListener('click', simulateAIResponse);
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') simulateAIResponse();
        });
    }

    // Pattern visualization
    function initPatternVisualization() {
        // This would initialize more complex pattern visualizations
        // For now, it's a placeholder for future expansion
    }

    // Cleanup on page unload
    window.addEventListener('beforeunload', () => {
        // Clear timers
        state.timers.forEach(timer => clearInterval(timer));
        state.timers.clear();

        // Disconnect observers
        state.observers.forEach(observer => observer.disconnect());
        state.observers.clear();

        // Destroy canvas systems
        state.canvases.forEach(system => {
            if (system.destroy) system.destroy();
        });
        state.canvases.clear();

        // Clear animations
        state.animations.clear();
    });

    // Export for debugging
    window.katanxLanding = {
        state,
        init,
        CanvasParticleSystem,
        AIVisualizationSystem
    };

})();