/**
 * Nav brand scroll behavior: same as landing.
 * When scrollY > 40: brand shows "/x" (slash yellow, x blue).
 * When scrollY <= 40: brand shows "/katanx" (slash yellow, katanx white).
 * Run once on DOMContentLoaded.
 */
(function () {
    function initNavBrandScroll() {
        var brand = document.querySelector('.header-branding .nav-brand') || document.querySelector('.nav-brand');
        if (!brand) return;
        var originalText = 'katanx';
        var compressed = false;

        function setBrand(text, makeBlue) {
            brand.style.opacity = '0';
            requestAnimationFrame(function () {
                setTimeout(function () {
                    brand.textContent = text;
                    if (makeBlue && text === 'x') {
                        brand.classList.add('nav-brand-x');
                    } else {
                        brand.classList.remove('nav-brand-x');
                    }
                    brand.style.opacity = '1';
                }, 120);
            });
        }

        function handleScroll() {
            if (window.scrollY > 40 && !compressed) {
                compressed = true;
                setBrand('x', true);
            } else if (window.scrollY <= 40 && compressed) {
                compressed = false;
                setBrand(originalText, false);
            }
        }

        window.addEventListener('scroll', handleScroll, { passive: true });
        handleScroll();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initNavBrandScroll);
    } else {
        initNavBrandScroll();
    }
})();
