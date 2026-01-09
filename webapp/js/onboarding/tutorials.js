/**
 * Tutorial Registry
 * Defines all available tutorials and their content
 */

export class TutorialRegistry {
    constructor() {
        this.tutorials = new Map();
        this.registerDefaultTutorials();
    }
    
    /**
     * Register default tutorials
     */
    registerDefaultTutorials() {
        // Welcome / Project Introduction
        this.register({
            id: 'welcome',
            title: 'Welcome to Katanx',
            content: [
                'Katanx is a platform for practitioners, researchers, and creators.',
                'Here you can share your work, discover others, and build meaningful connections.',
                'Let\'s get you started with a quick tour.'
            ],
            skippable: true,
            nextText: 'Let\'s go',
            skipText: 'Skip tour'
        });
        
        // Profile Setup
        this.register({
            id: 'profile-setup',
            title: 'Complete Your Profile',
            content: [
                'Your profile is how others discover you on Katanx.',
                'Add a photo, write a bio, and share your interests.',
                'You can customize how your profile appears to others.'
            ],
            target: '.profile-info, .profile-name-large',
            skippable: true,
            nextText: 'Got it'
        });
        
        // Stream Navigation
        this.register({
            id: 'stream-navigation',
            title: 'Explore Your Stream',
            content: [
                'This is your main feed where you\'ll see posts from people you follow.',
                'Use the navigation bar to switch between Stream, Explore, and other sections.',
                'Click on posts to read more and interact with the community.'
            ],
            target: '.nav-links, .nav-item',
            skippable: true,
            nextText: 'Got it'
        });
        
        // Explore Page
        this.register({
            id: 'explore',
            title: 'Discover New Content',
            content: [
                'The Explore page helps you discover new practitioners and content.',
                'Search for topics, browse categories, and find people with similar interests.',
                'Follow people whose work resonates with you.'
            ],
            target: '.search-bar, .search-input',
            skippable: true,
            nextText: 'Got it'
        });
        
        // KIM Chat
        this.register({
            id: 'kim-chat',
            title: 'Connect with Messages',
            content: [
                'KIM (Killer Instant Messaging) lets you chat with other practitioners.',
                'Join public rooms or start private conversations.',
                'Messages are end-to-end encrypted for privacy.'
            ],
            target: '.kim-sidebar-panel, .kim-toggle-btn',
            skippable: true,
            nextText: 'Got it'
        });
        
        // Posting Content
        this.register({
            id: 'posting',
            title: 'Share Your Work',
            content: [
                'Create posts to share your research, insights, or creative work.',
                'Use tags to help others discover your content.',
                'Engage with the community through likes, comments, and reposts.'
            ],
            target: '.post-create-btn, [data-action="create-post"]',
            skippable: true,
            nextText: 'Got it'
        });
        
        // Profile Customization
        this.register({
            id: 'profile-customization',
            title: 'Customize Your Profile',
            content: [
                'You can customize how your profile appears to others.',
                'Choose which sections to show, rearrange layout, and control visibility.',
                'Use the preview toggle to see how others see your profile.'
            ],
            target: '.profile-customize-btn, .profile-edit-btn',
            skippable: true,
            nextText: 'Got it'
        });
    }
    
    /**
     * Register a tutorial
     */
    register(tutorial) {
        if (!tutorial.id) {
            console.error('[TutorialRegistry] Tutorial must have an id');
            return;
        }
        
        this.tutorials.set(tutorial.id, {
            id: tutorial.id,
            title: tutorial.title || 'Tutorial',
            content: tutorial.content || [],
            target: tutorial.target || null,
            skippable: tutorial.skippable !== false,
            nextText: tutorial.nextText || 'Next',
            skipText: tutorial.skipText || 'Skip',
            ...tutorial
        });
    }
    
    /**
     * Get a tutorial by ID
     */
    get(tutorialId) {
        return this.tutorials.get(tutorialId) || null;
    }
    
    /**
     * Get all tutorials
     */
    getAll() {
        return Array.from(this.tutorials.values());
    }
    
    /**
     * Check if tutorial exists
     */
    has(tutorialId) {
        return this.tutorials.has(tutorialId);
    }
}

