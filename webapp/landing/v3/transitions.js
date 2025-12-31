/**
 * Landing Page V3 - View Transitions Module
 * Smooth section transitions using View Transitions API
 */

export default {
  config: null,
  features: null,

  init(config, features) {
    this.config = config;
    this.features = features;

    if (!features.viewTransitions || !('startViewTransition' in document)) {
      return;
    }

    this.initSectionTransitions();
  },

  initSectionTransitions() {
    // Add transition names to sections
    const sections = document.querySelectorAll('.section[data-v3="section"]');
    sections.forEach((section, index) => {
      section.style.viewTransitionName = `section-${index}`;
    });

    // Smooth scroll with transitions
    document.querySelectorAll('a[href^="#"]').forEach(link => {
      link.addEventListener('click', (e) => {
        const href = link.getAttribute('href');
        if (href === '#' || !href.startsWith('#')) return;

        const target = document.querySelector(href);
        if (!target) return;

        e.preventDefault();

        // Use view transition if available
        if (document.startViewTransition) {
          document.startViewTransition(() => {
            window.LandingV3Utils?.scrollToElement(target, 80);
          });
        } else {
          window.LandingV3Utils?.scrollToElement(target, 80);
        }
      });
    });

    window.LandingV3Utils?.logInfo('View transitions initialized');
  }
};



