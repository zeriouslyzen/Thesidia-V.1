/**
 * Component Loader
 * Responsible for loading and injecting shared HTML components.
 */

export const ComponentLoader = {
    async load(componentName, targetId) {
        const target = document.getElementById(targetId);
        if (!target) {
            console.error(`Target element #${targetId} not found.`);
            return false;
        }

        try {
            const response = await fetch(`/components/${componentName}.html`);
            if (!response.ok) throw new Error(`Failed to load component: ${componentName}`);

            const html = await response.text();
            target.innerHTML = html;
            return true;
        } catch (error) {
            console.error(`Error loading component ${componentName}:`, error);
            return false;
        }
    },

    async loadSharedComponents() {
        const results = await Promise.all([
            this.load('header', 'appHeader'), // Ensure target exists in HTML
            this.load('sidebar', 'leftSidebar')
        ]);
        return results.every(res => res === true);
    }
};
