/**
 * Landing Page V3 - Shared Utilities
 * Zero dependencies on platform code
 */

(function() {
  'use strict';

  window.LandingV3Utils = {
    /**
     * Debounce function
     */
    debounce(func, wait, immediate) {
      let timeout;
      return function executedFunction(...args) {
        const later = () => {
          timeout = null;
          if (!immediate) func(...args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func(...args);
      };
    },

    /**
     * Throttle function
     */
    throttle(func, limit) {
      let inThrottle;
      return function(...args) {
        if (!inThrottle) {
          func.apply(this, args);
          inThrottle = true;
          setTimeout(() => inThrottle = false, limit);
        }
      };
    },

    /**
     * Check if element is in viewport
     */
    isInViewport(element, threshold = 0) {
      const rect = element.getBoundingClientRect();
      return (
        rect.top >= -threshold &&
        rect.left >= -threshold &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) + threshold &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth) + threshold
      );
    },

    /**
     * Get scroll progress (0 to 1)
     */
    getScrollProgress() {
      const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
      const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
      return height > 0 ? winScroll / height : 0;
    },

    /**
     * Smooth scroll to element
     */
    scrollToElement(element, offset = 0) {
      if (!element) return;
      const elementPosition = element.getBoundingClientRect().top + window.pageYOffset;
      const offsetPosition = elementPosition - offset;

      window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth'
      });
    },

    /**
     * Check if user prefers reduced motion
     */
    prefersReducedMotion() {
      return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    },

    /**
     * Check if device is low-end
     */
    isLowEndDevice() {
      return navigator.hardwareConcurrency < 4 || 
             (navigator.deviceMemory && navigator.deviceMemory < 4);
    },

    /**
     * Check if browser supports WebGL
     */
    supportsWebGL() {
      try {
        const canvas = document.createElement('canvas');
        return !!(canvas.getContext('webgl') || canvas.getContext('experimental-webgl'));
      } catch (e) {
        return false;
      }
    },

    /**
     * Check if browser supports View Transitions API
     */
    supportsViewTransitions() {
      return 'startViewTransition' in document;
    },

    /**
     * Load script dynamically
     */
    loadScript(src, onLoad, onError) {
      return new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.src = src;
        script.async = true;
        script.onload = () => {
          if (onLoad) onLoad();
          resolve();
        };
        script.onerror = () => {
          if (onError) onError();
          reject(new Error(`Failed to load script: ${src}`));
        };
        document.head.appendChild(script);
      });
    },

    /**
     * Load stylesheet dynamically
     */
    loadStylesheet(href) {
      return new Promise((resolve, reject) => {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = href;
        link.onload = () => resolve();
        link.onerror = () => reject(new Error(`Failed to load stylesheet: ${href}`));
        document.head.appendChild(link);
      });
    },

    /**
     * Create element with attributes
     */
    createElement(tag, attributes = {}, textContent = '') {
      const element = document.createElement(tag);
      Object.entries(attributes).forEach(([key, value]) => {
        if (key === 'className') {
          element.className = value;
        } else if (key === 'dataset') {
          Object.entries(value).forEach(([dataKey, dataValue]) => {
            element.dataset[dataKey] = dataValue;
          });
        } else {
          element.setAttribute(key, value);
        }
      });
      if (textContent) {
        element.textContent = textContent;
      }
      return element;
    },

    /**
     * Log error safely (doesn't break page)
     */
    logError(message, error) {
      if (console && console.error) {
        console.error(`[LandingV3] ${message}`, error || '');
      }
    },

    /**
     * Log info safely
     */
    logInfo(message, data) {
      if (console && console.log) {
        console.log(`[LandingV3] ${message}`, data || '');
      }
    }
  };
})();



