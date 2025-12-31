// The Problem Page JavaScript
// Interactive elements and data visualizations

document.addEventListener('DOMContentLoaded', () => {
    // Add smooth scroll animations for sections
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observe all problem sections
    document.querySelectorAll('.problem-section').forEach(section => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(20px)';
        section.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(section);
    });

    // Add hover effects to comparison table rows
    const tableRows = document.querySelectorAll('.comparison-table tbody tr');
    tableRows.forEach(row => {
        row.addEventListener('mouseenter', () => {
            row.style.backgroundColor = 'rgba(255, 215, 0, 0.05)';
        });
        row.addEventListener('mouseleave', () => {
            row.style.backgroundColor = 'transparent';
        });
    });

    // Animate comparison table on scroll
    const comparisonTable = document.querySelector('.comparison-table');
    if (comparisonTable) {
        const tableObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'scale(1)';
                }
            });
        }, { threshold: 0.2 });

        comparisonTable.style.opacity = '0';
        comparisonTable.style.transform = 'scale(0.95)';
        comparisonTable.style.transition = 'opacity 0.8s ease, transform 0.8s ease';
        tableObserver.observe(comparisonTable);
    }
});

