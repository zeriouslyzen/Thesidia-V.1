/**
 * Landing Page V3 - Enhanced Manifesto Module
 * Typewriter effects, scroll-triggered highlights, interactive quotes
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

    this.initScrollHighlights();
    this.initInteractiveQuotes();
  },

  initScrollHighlights() {
    const manifestoSection = document.querySelector('.manifesto-section[data-v3="manifesto"]');
    if (!manifestoSection) return;

    const keyPhrases = manifestoSection.querySelectorAll('[data-v3="highlight"]');
    
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('v3-highlighted');
        } else {
          entry.target.classList.remove('v3-highlighted');
        }
      });
    }, {
      threshold: 0.5,
      rootMargin: '0px 0px -100px 0px'
    });

    keyPhrases.forEach(phrase => {
      observer.observe(phrase);
    });
  },

  initInteractiveQuotes() {
    const quotes = document.querySelectorAll('[data-v3="quote"]');
    
    quotes.forEach(quote => {
      quote.addEventListener('click', () => {
        // Toggle expanded state
        quote.classList.toggle('v3-quote-expanded');
        
        // Show additional context if available
        const context = quote.dataset.context;
        if (context && !quote.querySelector('.v3-quote-context')) {
          const contextEl = document.createElement('div');
          contextEl.className = 'v3-quote-context';
          contextEl.textContent = context;
          quote.appendChild(contextEl);
        }
      });

      // Keyboard support
      quote.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          quote.click();
        }
      });
    });
  }
};



