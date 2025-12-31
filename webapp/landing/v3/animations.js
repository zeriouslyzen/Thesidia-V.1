/**
 * Landing Page V3 - Animations Module
 * GSAP integration and enhanced scroll animations
 */

export default {
  config: null,
  features: null,
  gsapLoaded: false,

  async init(config, features) {
    this.config = config;
    this.features = features;

    // Load GSAP if enabled and not already loaded
    if (config.features.gsap && !this.gsapLoaded) {
      await this.loadGSAP();
    }

    // Initialize animations
    if (this.gsapLoaded && typeof gsap !== 'undefined' && typeof ScrollTrigger !== 'undefined') {
      this.initGSAPAnimations();
    } else {
      // Fallback to CSS/IntersectionObserver animations
      this.initFallbackAnimations();
    }
  },

  async loadGSAP() {
    try {
      // Load GSAP from CDN
      if (typeof gsap === 'undefined') {
        await window.LandingV3Utils.loadScript('https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/gsap.min.js');
      }

      // Load ScrollTrigger plugin
      if (typeof ScrollTrigger === 'undefined') {
        await window.LandingV3Utils.loadScript('https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/ScrollTrigger.min.js');
        gsap.registerPlugin(ScrollTrigger);
      }

      this.gsapLoaded = true;
      window.LandingV3Utils?.logInfo('GSAP loaded successfully');
    } catch (error) {
      window.LandingV3Utils?.logError('Failed to load GSAP', error);
      this.gsapLoaded = false;
    }
  },

  initGSAPAnimations() {
    if (!this.gsapLoaded || typeof gsap === 'undefined') return;

    // Respect reduced motion preference
    if (this.config.performance.reducedMotion) {
      gsap.config({ nullTargetWarn: false });
      return;
    }

    try {
      // Enhanced scroll animations for sections
      gsap.utils.toArray('.section[data-v3="section"]').forEach((section, index) => {
        gsap.fromTo(section,
          {
            opacity: 0,
            y: 50
          },
          {
            opacity: 1,
            y: 0,
            duration: 1,
            ease: 'power3.out',
            scrollTrigger: {
              trigger: section,
              start: 'top 80%',
              end: 'top 20%',
              toggleActions: 'play none none reverse'
            }
          }
        );
      });

      // Staggered card animations
      gsap.utils.toArray('.card[data-v3="card"]').forEach((card, index) => {
        gsap.fromTo(card,
          {
            opacity: 0,
            scale: 0.9,
            y: 30
          },
          {
            opacity: 1,
            scale: 1,
            y: 0,
            duration: 0.6,
            delay: index * 0.1,
            ease: 'back.out(1.7)',
            scrollTrigger: {
              trigger: card,
              start: 'top 85%',
              toggleActions: 'play none none reverse'
            }
          }
        );
      });

      // Parallax effect for hero section
      const hero = document.querySelector('.hero[data-v3="hero"]');
      if (hero) {
        gsap.to(hero, {
          yPercent: -50,
          ease: 'none',
          scrollTrigger: {
            trigger: hero,
            start: 'top top',
            end: 'bottom top',
            scrub: true
          }
        });
      }

      // Scroll progress indicator
      this.initScrollProgress();

      window.LandingV3Utils?.logInfo('GSAP animations initialized');
    } catch (error) {
      window.LandingV3Utils?.logError('Failed to initialize GSAP animations', error);
      this.initFallbackAnimations();
    }
  },

  initScrollProgress() {
    // Create scroll progress indicator
    const progressBar = document.createElement('div');
    progressBar.className = 'v3-scroll-progress';
    document.body.appendChild(progressBar);

    // Update progress on scroll
    const updateProgress = window.LandingV3Utils?.throttle(() => {
      const progress = window.LandingV3Utils?.getScrollProgress() || 0;
      progressBar.style.width = `${progress * 100}%`;
    }, 10);

    window.addEventListener('scroll', updateProgress, { passive: true });
  },

  initFallbackAnimations() {
    // Use IntersectionObserver as fallback
    if (!('IntersectionObserver' in window)) {
      // Show all elements immediately if IntersectionObserver not supported
      document.querySelectorAll('[data-v3]').forEach(el => {
        el.style.opacity = '1';
        el.style.transform = 'none';
      });
      return;
    }

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('v3-visible');
          observer.unobserve(entry.target);
        }
      });
    }, {
      threshold: 0.1,
      rootMargin: '0px 0px -50px 0px'
    });

    document.querySelectorAll('.section[data-v3="section"], .card[data-v3="card"]').forEach(el => {
      observer.observe(el);
    });

    window.LandingV3Utils?.logInfo('Fallback animations initialized');
  }
};



