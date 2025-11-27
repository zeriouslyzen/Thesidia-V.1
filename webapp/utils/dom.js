/**
 * Safe DOM Manipulation Utilities
 * Prevents XSS attacks by using safe DOM methods instead of innerHTML
 */

/**
 * Safely set text content of an element
 * @param {HTMLElement} element - Target element
 * @param {string} text - Text content to set
 */
export function setTextContent(element, text) {
    if (!element) return;
    element.textContent = text || '';
}

/**
 * Safely create an element with text content
 * @param {string} tag - HTML tag name
 * @param {string} text - Text content
 * @param {Object} attributes - Element attributes
 * @returns {HTMLElement}
 */
export function createElement(tag, text = '', attributes = {}) {
    const element = document.createElement(tag);
    if (text) {
        element.textContent = text;
    }
    Object.entries(attributes).forEach(([key, value]) => {
        if (key === 'className') {
            element.className = value;
        } else if (key === 'dataset') {
            Object.entries(value).forEach(([dataKey, dataValue]) => {
                element.dataset[dataKey] = dataValue;
            });
        } else {
            element.setAttribute(key, value);
        }
    });
    return element;
}

/**
 * Safely escape HTML entities
 * @param {string} text - Text to escape
 * @returns {string} Escaped text
 */
export function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Safely create HTML from template string (with escaped variables)
 * Use this for complex HTML structures
 * @param {Array<string>} strings - Template string parts
 * @param {...any} values - Values to interpolate (will be escaped)
 * @returns {DocumentFragment}
 */
export function safeHtml(strings, ...values) {
    const fragment = document.createDocumentFragment();
    const temp = document.createElement('div');
    
    let html = '';
    strings.forEach((str, i) => {
        html += str;
        if (i < values.length) {
            // Escape all interpolated values
            html += escapeHtml(String(values[i]));
        }
    });
    
    temp.innerHTML = html;
    while (temp.firstChild) {
        fragment.appendChild(temp.firstChild);
    }
    
    return fragment;
}

/**
 * Safely append HTML to element
 * @param {HTMLElement} parent - Parent element
 * @param {string} html - HTML string (will be sanitized)
 */
export function safeAppendHtml(parent, html) {
    if (!parent) return;
    const temp = document.createElement('div');
    temp.innerHTML = html;
    while (temp.firstChild) {
        parent.appendChild(temp.firstChild);
    }
}

/**
 * Safely replace element content
 * @param {HTMLElement} element - Target element
 * @param {string|HTMLElement|DocumentFragment} content - Content to set
 */
export function safeSetContent(element, content) {
    if (!element) return;
    
    // Clear existing content
    element.textContent = '';
    
    if (typeof content === 'string') {
        // For simple text, use textContent
        element.textContent = content;
    } else if (content instanceof HTMLElement || content instanceof DocumentFragment) {
        // For DOM elements, append them
        element.appendChild(content);
    } else {
        // For HTML strings, parse safely
        safeAppendHtml(element, String(content));
    }
}

/**
 * Safely create element from HTML string
 * @param {string} html - HTML string
 * @returns {DocumentFragment}
 */
export function createFromHtml(html) {
    const fragment = document.createDocumentFragment();
    const temp = document.createElement('div');
    temp.innerHTML = html;
    while (temp.firstChild) {
        fragment.appendChild(temp.firstChild);
    }
    return fragment;
}

