/**
 * Landing Page V3 - Core Module
 * Initialization, feature detection, and module loading
 * Zero dependencies on platform code
 */

(function() {
  'use strict';

  const LandingV3 = {
    config: window.LANDING_V3_CONFIG || {
      features: {
        gsap: true,
        webgl: true,
        viewTransitions: true,
        serviceWorker: false,
        webComponents: false
      },
      performance: {
        reducedMotion: false,
        lowEndDevice: false
      }
    },

    features: {
      gsap: false,
      webgl: false,
      viewTransitions: false,
      serviceWorker: false,
      webComponents: false
    },

    modules: {},

    /**
     * Initialize V3
     */
    init() {
      try {
        this.logInfo('Initializing Landing V3...');
        
        // Update performance config
        this.config.performance.reducedMotion = window.LandingV3Utils?.prefersReducedMotion() || false;
        this.config.performance.lowEndDevice = window.LandingV3Utils?.isLowEndDevice() || false;

        // Detect features
        this.detectFeatures();

        // Initialize modules conditionally
        this.initModules();

        // Set up error handling
        this.setupErrorHandling();

        this.logInfo('Landing V3 initialized successfully');
      } catch (error) {
        this.logError('Failed to initialize Landing V3', error);
        this.gracefulDegrade();
      }
    },

    /**
     * Detect browser capabilities
     */
    detectFeatures() {
      // GSAP detection (will be set when GSAP loads)
      this.features.gsap = this.config.features.gsap && typeof gsap !== 'undefined';

      // WebGL detection
      if (this.config.features.webgl && !this.config.performance.lowEndDevice) {
        this.features.webgl = window.LandingV3Utils?.supportsWebGL() || false;
      }

      // View Transitions API
      if (this.config.features.viewTransitions) {
        this.features.viewTransitions = window.LandingV3Utils?.supportsViewTransitions() || false;
      }

      // Service Worker
      if (this.config.features.serviceWorker && 'serviceWorker' in navigator) {
        this.features.serviceWorker = true;
      }

      // Web Components
      if (this.config.features.webComponents) {
        this.features.webComponents = typeof customElements !== 'undefined';
      }

      this.logInfo('Feature detection complete', this.features);
    },

    /**
     * Initialize modules conditionally
     */
    async initModules() {
      const modulePath = '/landing/v3/';

      // Always load core modules (non-blocking)
      const coreModules = [];
      
      // Animations module (will check for GSAP internally)
      if (this.config.features.gsap) {
        coreModules.push(this.loadModule('animations', modulePath + 'animations.js'));
      }

      // Interactions module
      coreModules.push(this.loadModule('interactions', modulePath + 'interactions.js'));

      // Performance module
      coreModules.push(this.loadModule('performance', modulePath + 'performance.js'));

      // Manifesto module
      coreModules.push(this.loadModule('manifesto', modulePath + 'manifesto.js'));

      // Load core modules in parallel
      await Promise.allSettled(coreModules);

      // Conditionally load optional modules
      const optionalModules = [];

      if (this.features.webgl && this.config.features.webgl && !this.config.performance.lowEndDevice) {
        optionalModules.push(this.loadModule('webgl', modulePath + 'webgl.js'));
      }

      if (this.features.viewTransitions && this.config.features.viewTransitions) {
        optionalModules.push(this.loadModule('transitions', modulePath + 'transitions.js'));
      }

      if (this.config.features.webComponents && this.features.webComponents) {
        optionalModules.push(this.loadModule('components', modulePath + 'components.js'));
      }

      // Load optional modules in parallel (non-blocking)
      await Promise.allSettled(optionalModules);
    },

    /**
     * Load a module dynamically
     */
    async loadModule(name, path) {
      if (this.modules[name]) {
        this.logInfo(`Module ${name} already loaded`);
        return;
      }

      try {
        // Use dynamic import for ES modules
        const module = await import(path);
        this.modules[name] = module;
        
        // Initialize module if it has an init method
        // Modules export default object with init method
        if (module.default && typeof module.default.init === 'function') {
          await module.default.init(this.config, this.features);
        } else if (typeof module.init === 'function') {
          await module.init(this.config, this.features);
        }

        this.logInfo(`Module ${name} loaded successfully`);
      } catch (error) {
        this.logError(`Failed to load module ${name}`, error);
        // Don't throw - allow other modules to load
      }
    },

    /**
     * Set up error handling
     */
    setupErrorHandling() {
      // Global error handler
      window.addEventListener('error', (event) => {
        // Only handle errors from V3 code
        if (event.filename && event.filename.includes('/landing/v3/')) {
          this.logError('V3 error caught', {
            message: event.message,
            filename: event.filename,
            lineno: event.lineno,
            colno: event.colno,
            error: event.error
          });
          
          // Don't break the page - just log
          event.preventDefault();
        }
      });

      // Unhandled promise rejection handler
      window.addEventListener('unhandledrejection', (event) => {
        if (event.reason && event.reason.toString().includes('landing/v3')) {
          this.logError('V3 unhandled promise rejection', event.reason);
          event.preventDefault();
        }
      });
    },

    /**
     * Graceful degradation to V2 behavior
     */
    gracefulDegrade() {
      this.logInfo('Gracefully degrading to V2 behavior');
      // Remove V3-specific classes/attributes
      document.documentElement.classList.remove('v3-enabled');
      document.body.classList.remove('v3-enabled');
      
      // V2 behavior will work as normal since we haven't modified core functionality
    },

    /**
     * Log error safely
     */
    logError(message, error) {
      if (window.LandingV3Utils) {
        window.LandingV3Utils.logError(message, error);
      } else if (console && console.error) {
        console.error(`[LandingV3] ${message}`, error || '');
      }
    },

    /**
     * Log info safely
     */
    logInfo(message, data) {
      if (window.LandingV3Utils) {
        window.LandingV3Utils.logInfo(message, data);
      } else if (console && console.log) {
        console.log(`[LandingV3] ${message}`, data || '');
      }
    }
  };

  // Expose globally
  window.LandingV3 = LandingV3;

  // Auto-initialize on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => LandingV3.init());
  } else {
    LandingV3.init();
  }
})();

