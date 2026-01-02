/**
 * Category Cards Design Test v2
 * 
 * Uses topic-related images instead of faces.
 * Run this in the browser console on the forums page to test the new design.
 */

(function enableEnhancedCategoryDesign() {
    // Add CSS file if not already loaded
    if (!document.getElementById('category-cards-test-css')) {
        const link = document.createElement('link');
        link.id = 'category-cards-test-css';
        link.rel = 'stylesheet';
        link.href = '/css/category-cards-test.css';
        document.head.appendChild(link);
        console.log('✅ Enhanced category design CSS loaded');
    }

    // Topic-to-keyword mapping for Unsplash images
    const topicKeywords = {
        'all': 'abstract,pattern',
        'visual': 'art,painting,canvas',
        'movement': 'dance,yoga,fitness',
        'craft': 'handmade,pottery,craft',
        'writing': 'writing,typewriter,book',
        'music': 'music,instrument,piano',
        'performance': 'stage,theater,performance',
        'teaching': 'classroom,education,learning',
        'meta-guidelines': 'compass,direction,guide',
        'posting-rules': 'rules,organization,structure',
        'human-development': 'growth,mindfulness,nature',
        'martial': 'dojo,boxing-gloves,punching-bag',
        'martial-arts': 'dojo,boxing-gloves,punching-bag',
        'literature': 'books,library,reading',
        'digital': 'technology,digital,code',
        'sculpture': 'sculpture,statue,art',
        'photography': 'camera,photography,lens',
        'film': 'cinema,film,movie',
        'cooking': 'cooking,food,kitchen',
        'gaming': 'gaming,controller,esports',
        'meditation': 'meditation,zen,peaceful',
        'sports': 'sports,athlete,fitness',
        'nature': 'nature,landscape,outdoor'
    };

    // Function to get topic keywords from category name/slug
    function getTopicKeywords(categorySlug, categoryName) {
        const slug = (categorySlug || '').toLowerCase();
        const name = (categoryName || '').toLowerCase();

        // Check direct matches first
        for (const [key, keywords] of Object.entries(topicKeywords)) {
            if (slug.includes(key) || name.includes(key)) {
                return keywords;
            }
        }

        // Default to abstract pattern
        return 'abstract,minimal,dark';
    }

    // Override category names for cleaner /slash format
    function formatCategoryName(slug, name) {
        // Convert to clean /slug format
        const cleanSlug = (slug || name || 'category')
            .toLowerCase()
            .replace(/[\s&]+/g, '')  // Remove spaces and &
            .replace(/[^a-z0-9]/g, ''); // Keep only letters/numbers
        return `/${cleanSlug}`;
    }

    // Override avatar URLs and category names for all items
    function updateCategoryItems() {
        const categories = document.querySelectorAll('.circle-category-item');

        categories.forEach((item, index) => {
            const slug = item.dataset.slug || item.dataset.category || '';
            const nameEl = item.querySelector('.circle-category-name');
            const name = nameEl ? nameEl.textContent : '';
            const img = item.querySelector('.circle-category-avatar');

            // Update name to /slash format
            if (nameEl && slug !== 'all') {
                nameEl.textContent = formatCategoryName(slug, name);
            } else if (nameEl && slug === 'all') {
                nameEl.textContent = '/all';
            }

            if (img && slug !== 'all') {
                const keywords = getTopicKeywords(slug, name);
                const seed = index + Math.abs(slug.split('').reduce((a, c) => a + c.charCodeAt(0), 0));

                // Use Unsplash Source with topic keywords
                img.src = `https://source.unsplash.com/300x400/?${keywords}&sig=${seed}`;
                img.onerror = function () {
                    // Fallback to picsum with grayscale
                    this.src = `https://picsum.photos/seed/${slug || index}/300/400?grayscale`;
                };
            }
        });

        console.log(`✅ Updated ${categories.length} category names to /slash format`);
    }

    // Add the enhanced-design class to the categories scroll container
    const categoriesScroll = document.getElementById('circlesCategoriesScroll');
    if (categoriesScroll) {
        categoriesScroll.classList.add('enhanced-design');
        console.log('✅ Enhanced design class added to categories');

        // Update images after a short delay to ensure DOM is ready
        setTimeout(updateCategoryItems, 500);

        // Also set up a MutationObserver to handle dynamically loaded categories
        const observer = new MutationObserver(() => {
            setTimeout(updateCategoryItems, 100);
        });
        observer.observe(categoriesScroll, { childList: true, subtree: true });

    } else {
        console.log('⏳ Categories container not found yet. Navigate to forums first, then run again.');
    }
})();

// To disable, run:
// document.getElementById('circlesCategoriesScroll')?.classList.remove('enhanced-design');
// document.getElementById('category-cards-test-css')?.remove();
