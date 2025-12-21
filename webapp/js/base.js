import { ComponentLoader } from './modules/loader.js';
import { Navigation } from './modules/navigation.js';
import { Effects } from './modules/effects.js';

async function initBase() {
    // Load components
    await ComponentLoader.loadSharedComponents();

    // Init Navigation
    const nav = new Navigation();
    nav.init();

    // Init Common Effects
    Effects.initNanoDust();
    Effects.initAstrologicalTime();
    Effects.initStarNotepad();

    console.log('Base components initialized');
}

document.addEventListener('DOMContentLoaded', initBase);
