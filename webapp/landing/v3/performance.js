/**
 * Landing Page V3 - Performance Module
 * Optimization, lazy loading, and performance monitoring
 */

export default {
  config: null,
  features: null,

  init(config, features) {
    this.config = config;
    this.features = features;

    this.initLazyLoading();
    this.initImageOptimization();
    this.initPerformanceMonitoring();
  },

  initLazyLoading() {
    // Enhanced lazy loading for images
    if ('loading' in HTMLImageElement.prototype) {
      const images = document.querySelectorAll('img[data-v3="lazy"]');
      images.forEach(img => {
        img.loading = 'lazy';
        img.addEventListener('load', () => {
          img.classList.add('v3-loaded');
        });
      });
    } else {
      // Fallback: IntersectionObserver for lazy loading
      const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            const img = entry.target;
            if (img.dataset.src) {
              img.src = img.dataset.src;
              img.removeAttribute('data-src');
            }
            imageObserver.unobserve(img);
          }
        });
      });

      document.querySelectorAll('img[data-v3="lazy"]').forEach(img => {
        imageObserver.observe(img);
      });
    }
  },

  initImageOptimization() {
    // Convert images to WebP if supported
    const images = document.querySelectorAll('img[data-v3="optimize"]');
    
    images.forEach(img => {
      // Check if browser supports WebP
      const supportsWebP = this.checkWebPSupport();
      
      if (supportsWebP && img.dataset.webp) {
        img.src = img.dataset.webp;
      }
    });
  },

  checkWebPSupport() {
    const canvas = document.createElement('canvas');
    canvas.width = 1;
    canvas.height = 1;
    return canvas.toDataURL('image/webp').indexOf('data:image/webp') === 0;
  },

  initPerformanceMonitoring() {
    // Monitor Core Web Vitals
    if ('PerformanceObserver' in window) {
      try {
        // Largest Contentful Paint
        const lcpObserver = new PerformanceObserver((list) => {
          const entries = list.getEntries();
          const lastEntry = entries[entries.length - 1];
          window.LandingV3Utils?.logInfo('LCP', lastEntry.renderTime || lastEntry.loadTime);
        });
        lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });

        // First Input Delay
        const fidObserver = new PerformanceObserver((list) => {
          const entries = list.getEntries();
          entries.forEach(entry => {
            window.LandingV3Utils?.logInfo('FID', entry.processingStart - entry.startTime);
          });
        });
        fidObserver.observe({ entryTypes: ['first-input'] });

        // Cumulative Layout Shift
        const clsObserver = new PerformanceObserver((list) => {
          const entries = list.getEntries();
          entries.forEach(entry => {
            if (!entry.hadRecentInput) {
              window.LandingV3Utils?.logInfo('CLS', entry.value);
            }
          });
        });
        clsObserver.observe({ entryTypes: ['layout-shift'] });
      } catch (error) {
        window.LandingV3Utils?.logError('Performance monitoring error', error);
      }
    }
  }
};



