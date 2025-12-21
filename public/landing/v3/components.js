/**
 * Landing Page V3 - Web Components Module
 * Custom web components for reusable UI elements (optional)
 */

export default {
  config: null,
  features: null,

  init(config, features) {
    this.config = config;
    this.features = features;

    if (!features.webComponents || typeof customElements === 'undefined') {
      return;
    }

    this.registerComponents();
  },

  registerComponents() {
    // ArtCard Component
    if (!customElements.get('v3-art-card')) {
      class ArtCard extends HTMLElement {
        constructor() {
          super();
          this.attachShadow({ mode: 'open' });
        }

        connectedCallback() {
          this.render();
        }

        render() {
          const title = this.getAttribute('title') || '';
          const tagline = this.getAttribute('tagline') || '';
          const description = this.getAttribute('description') || '';

          this.shadowRoot.innerHTML = `
            <style>
              :host {
                display: block;
                background: rgba(10, 10, 10, 0.8);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 1.5rem;
                transition: all 0.3s ease;
              }
              :host(:hover) {
                border-color: rgba(255, 215, 0, 0.3);
                transform: translateY(-2px);
              }
              h3 {
                color: #fff;
                margin: 0 0 0.5rem 0;
                font-family: 'Inconsolata', monospace;
              }
              .tagline {
                color: #d2b48c;
                font-weight: 600;
                margin: 0.5rem 0;
              }
              .description {
                color: #ccc;
                margin: 0.5rem 0 0 0;
              }
            </style>
            <h3>${title}</h3>
            <div class="tagline">${tagline}</div>
            <div class="description">${description}</div>
          `;
        }
      }

      customElements.define('v3-art-card', ArtCard);
    }

    window.LandingV3Utils?.logInfo('Web components registered');
  }
};



