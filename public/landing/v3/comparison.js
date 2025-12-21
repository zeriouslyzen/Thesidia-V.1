/**
 * Landing Page V3 - Comparison Tool Module
 * Interactive side-by-side comparison with traditional social media
 */

export default {
  config: null,
  features: null,

  init(config, features) {
    this.config = config;
    this.features = features;

    this.initComparisonTool();
  },

  initComparisonTool() {
    const comparisonContainer = document.querySelector('[data-v3="comparison"]');
    if (!comparisonContainer) return;

    // Create comparison data
    const comparisonData = {
      metrics: [
        { label: 'Signal-to-Noise Ratio', katanx: 95, traditional: 15 },
        { label: 'Real Progress Tracking', katanx: true, traditional: false },
        { label: 'AI Content Filtering', katanx: true, traditional: false },
        { label: 'Practitioner Focus', katanx: true, traditional: false },
        { label: 'Influencer Culture', katanx: false, traditional: true }
      ]
    };

    // Render comparison
    this.renderComparison(comparisonContainer, comparisonData);
  },

  renderComparison(container, data) {
    let html = '<div class="v3-comparison-grid">';
    html += '<div class="v3-comparison-header">';
    html += '<div class="v3-comparison-cell">Metric</div>';
    html += '<div class="v3-comparison-cell">katanx</div>';
    html += '<div class="v3-comparison-cell">Traditional Social Media</div>';
    html += '</div>';

    data.metrics.forEach(metric => {
      html += '<div class="v3-comparison-row">';
      html += `<div class="v3-comparison-cell">${metric.label}</div>`;
      
      if (typeof metric.katanx === 'boolean') {
        html += `<div class="v3-comparison-cell ${metric.katanx ? 'v3-check' : 'v3-cross'}">${metric.katanx ? '✓' : '✗'}</div>`;
        html += `<div class="v3-comparison-cell ${metric.traditional ? 'v3-check' : 'v3-cross'}">${metric.traditional ? '✓' : '✗'}</div>`;
      } else {
        html += `<div class="v3-comparison-cell"><div class="v3-bar" style="width: ${metric.katanx}%"></div></div>`;
        html += `<div class="v3-comparison-cell"><div class="v3-bar" style="width: ${metric.traditional}%"></div></div>`;
      }
      
      html += '</div>';
    });

    html += '</div>';
    container.innerHTML = html;

    // Animate bars on scroll
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const bars = entry.target.querySelectorAll('.v3-bar');
          bars.forEach(bar => {
            const width = bar.style.width;
            bar.style.width = '0%';
            setTimeout(() => {
              bar.style.transition = 'width 1s ease-out';
              bar.style.width = width;
            }, 100);
          });
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.5 });

    observer.observe(container);
  }
};



