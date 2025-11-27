/**
 * Debounce and Throttle Utilities
 * Prevents excessive function calls for performance optimization
 */

/**
 * Debounce function - delays execution until after wait time
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @param {boolean} immediate - Execute immediately on first call
 * @returns {Function} Debounced function
 */
export function debounce(func, wait = 300, immediate = false) {
    let timeout;
    return function executedFunction(...args) {
        const context = this;
        const later = () => {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    };
}

/**
 * Throttle function - limits execution to once per wait time
 * @param {Function} func - Function to throttle
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} Throttled function
 */
export function throttle(func, wait = 300) {
    let inThrottle;
    return function executedFunction(...args) {
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => {
                inThrottle = false;
            }, wait);
        }
    };
}

/**
 * Request throttle - prevents excessive API calls
 * @param {Function} requestFunc - Function that makes API request
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} Throttled request function
 */
export function throttleRequest(requestFunc, wait = 500) {
    let lastCall = 0;
    let pendingRequest = null;
    
    return function executedFunction(...args) {
        const context = this;
        const now = Date.now();
        
        // If enough time has passed, execute immediately
        if (now - lastCall >= wait) {
            lastCall = now;
            return requestFunc.apply(context, args);
        }
        
        // Otherwise, cancel pending request and schedule new one
        if (pendingRequest) {
            clearTimeout(pendingRequest);
        }
        
        return new Promise((resolve, reject) => {
            pendingRequest = setTimeout(() => {
                lastCall = Date.now();
                pendingRequest = null;
                try {
                    const result = requestFunc.apply(context, args);
                    resolve(result);
                } catch (error) {
                    reject(error);
                }
            }, wait - (now - lastCall));
        });
    };
}

/**
 * Debounced scroll handler
 * @param {Function} handler - Scroll handler function
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} Debounced scroll handler
 */
export function debounceScroll(handler, wait = 100) {
    return debounce(handler, wait);
}

/**
 * Throttled scroll handler
 * @param {Function} handler - Scroll handler function
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} Throttled scroll handler
 */
export function throttleScroll(handler, wait = 100) {
    return throttle(handler, wait);
}

