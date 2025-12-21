/**
 * Landing Page V3 - Interactions Module
 * Interactive cards, hover effects, and user interactions
 */

export default {
  config: null,
  features: null,

  init(config, features) {
    this.config = config;
    this.features = features;

    // Respect reduced motion
    if (config.performance.reducedMotion) {
      return;
    }

    this.initCardInteractions();
    this.initMagneticCursor();
    this.initHoverEffects();
  },

  initCardInteractions() {
    const cards = document.querySelectorAll('.card[data-v3="card"]');

    cards.forEach(card => {
      // Add expand functionality on click
      card.addEventListener('click', (e) => {
        if (!card.classList.contains('v3-expandable')) return;

        const isExpanded = card.classList.contains('v3-expanded');
        
        // Close other expanded cards
        cards.forEach(c => {
          if (c !== card && c.classList.contains('v3-expanded')) {
            c.classList.remove('v3-expanded');
          }
        });

        // Toggle current card
        card.classList.toggle('v3-expanded', !isExpanded);
      });

      // Add keyboard support
      card.addEventListener('keydown', (e) => {
        if ((e.key === 'Enter' || e.key === ' ') && card.classList.contains('v3-expandable')) {
          e.preventDefault();
          card.click();
        }
      });
    });
  },

  initMagneticCursor() {
    // Only enable on desktop and if not low-end device
    if (this.config.performance.lowEndDevice || window.innerWidth < 768) {
      return;
    }

    const magneticElements = document.querySelectorAll('[data-v3="magnetic"]');
    if (magneticElements.length === 0) return;

    magneticElements.forEach(element => {
      element.addEventListener('mousemove', (e) => {
        const rect = element.getBoundingClientRect();
        const x = e.clientX - rect.left - rect.width / 2;
        const y = e.clientY - rect.top - rect.height / 2;

        const moveX = x * 0.15;
        const moveY = y * 0.15;

        element.style.transform = `translate(${moveX}px, ${moveY}px)`;
      });

      element.addEventListener('mouseleave', () => {
        element.style.transform = 'translate(0, 0)';
      });
    });
  },

  initHoverEffects() {
    const hoverElements = document.querySelectorAll('[data-v3="hover"]');

    hoverElements.forEach(element => {
      element.addEventListener('mouseenter', () => {
        element.classList.add('v3-hover-active');
      });

      element.addEventListener('mouseleave', () => {
        element.classList.remove('v3-hover-active');
      });
    });
  }
};



