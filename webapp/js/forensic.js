/**
 * Forensic Output Formatter & Interaction Handler
 * Handles the aesthetic rendering of Thesidia's forensic outputs.
 */

const ForensicUI = {
    /**
     * Main function to format raw text into aesthetic HTML
     * @param {string} text - Raw output text from Thesidia
     * @returns {string} - HTML string with forensic styling
     */
    format: function (text, messageId) {
        if (!text) return '';

        // Check if this is actually a forensic output (contains //section markers)
        if (!text.includes('//exposure') && !text.includes('//thread options')) {
            // Not forensic output, return standard markdown/text processing
            // You might want to wrap this in a standard container or return as is
            return this.processStandardText(text);
        }

        // Initialize container
        let html = `<div class="forensic-output" data-message-id="${messageId || ''}">`;

        // Extract and format sections
        const sections = this.extractSections(text);

        // Check for Confidence Meter in the last section or text end
        let confidenceHtml = '';
        if (sections.length > 0) {
            const lastSection = sections[sections.length - 1];
            const confidenceMatch = lastSection.content.match(/\*\*Epistemological Grounding:\*\*\s*([█░]+)\s*(\d+\/\d+)\s*layers aligned\s*\((HIGH|MEDIUM|LOW)\)/i);

            if (confidenceMatch) {
                // Extract and remove from section content
                lastSection.content = lastSection.content.replace(confidenceMatch[0], '').trim();
                confidenceHtml = this.renderConfidenceMeter(confidenceMatch[1], confidenceMatch[2], confidenceMatch[3]);
            }
        }

        sections.forEach((section, index) => {
            if (section.type === 'thread options') {
                html += this.renderThreadOptions(section.content, messageId);
            } else {
                html += this.renderSection(section.type, section.content, index);
            }
        });

        html += confidenceHtml;
        html += '</div>';

        // Add SVG definitions if not already present on page
        html += this.getSVGDefs();

        return html;
    },

    /**
     * Extract sections based on //marker
     */
    extractSections: function (text) {
        const sections = [];
        const lines = text.split('\n');
        let currentSection = null;
        let currentContent = [];

        // Regex for //section markers
        const markerRegex = /^\/\/\s*(.+)$/;

        lines.forEach(line => {
            const match = line.trim().match(markerRegex);
            if (match) {
                // Save previous section
                if (currentSection) {
                    sections.push({
                        type: currentSection,
                        content: currentContent.join('\n').trim()
                    });
                }
                // Start new section
                currentSection = match[1].toLowerCase().trim();
                currentContent = [];
            } else {
                // Add content to current section
                if (currentSection) {
                    currentContent.push(line);
                } else if (line.trim()) {
                    // Content before first section (preamble)
                    // We can either ignore it or add as 'intro'
                    // For forensic mode, we usually ignore preamble
                }
            }
        });

        // Save last section
        if (currentSection) {
            sections.push({
                type: currentSection,
                content: currentContent.join('\n').trim()
            });
        }

        return sections;
    },

    /**
     * Render a standard forensic section
     */
    renderSection: function (type, content, index) {
        // Special styling for exposure
        const isExposure = type === 'exposure';
        const className = isExposure ? 'forensic-section section-exposure' : 'forensic-section';

        // Process content for highlights (patterns, entities, etc.)
        const formattedContent = this.highlightEntities(this.highlightPatterns(this.formatMarkdown(content)));

        return `
            <div class="${className}" style="animation-delay: ${0.1 * (index + 1)}s">
                <div class="section-header">//${type}</div>
                <div class="section-content">${formattedContent}</div>
            </div>
        `;
    },

    /**
     * Render Thread Options as interactive cards
     */
    renderThreadOptions: function (content, messageId) {
        const lines = content.split('\n');
        let html = `
            <div class="thread-options-container forensic-section">
                <div class="section-header">//thread options</div>
        `;

        lines.forEach(line => {
            line = line.trim().replace(/^-\s*/, '').replace(/^→\s*/, ''); // Remove bullet/arrow
            if (!line) return;

            // Detect type
            let type = 'trace';
            let icon = this.icons.trace;

            if (line.toLowerCase().includes('re-enter')) {
                type = 're-enter';
                icon = this.icons.reEnter;
            } else if (line.toLowerCase().includes('cold-read')) {
                type = 'cold-read';
                icon = this.icons.coldRead;
            }

            html += `
                <div class="thread-card" onclick="ForensicUI.handleThreadClick(this, '${type}', '${this.escapeHtml(line)}', '${messageId || ''}')" role="button" tabindex="0">
                    <div class="thread-icon-wrapper">${icon}</div>
                    <div class="thread-label">${line}</div>
                    <div class="thread-arrow">→</div>
                </div>
            `;
        });

        html += '</div>';
        return html;
    },

    /**
     * Render Confidence Meter
     */
    renderConfidenceMeter: function (barVisual, score, status) {
        const percentage = (parseInt(score.split('/')[0]) / parseInt(score.split('/')[1])) * 100;
        const statusLower = status.toLowerCase();

        return `
            <div class="confidence-meter forensic-section" style="animation-delay: 0.5s">
                <div class="meter-header">
                    <span class="meter-label">Epistemological Grounding</span>
                    <span class="meter-score">${score} layers aligned</span>
                </div>
                <div class="meter-bar">
                    <div class="meter-fill" style="width: ${percentage}%"></div>
                </div>
                <div class="meter-status ${statusLower}">
                    Confidence: ${status}
                </div>
            </div>
        `;
    },

    /**
     * Handle thread click (To be connected to backend)
     */
    handleThreadClick: function (element, type, query) {
        console.log(`Thread clicked: ${type} - ${query}`);

        // Visual feedback
        element.style.borderColor = '#EC4899';
        element.style.background = 'rgba(236, 72, 153, 0.1)';

        // Dispatch custom event for the main app to handle
        const event = new CustomEvent('forensic-thread-click', {
            detail: { type, query }
        });
        document.dispatchEvent(event);

        // If integrated with input box directly:
        const input = document.getElementById('kim-message-input'); // or whatever ID
        if (input) {
            input.value = query;
            input.focus();
            // Optional: Auto-submit
            // document.getElementById('kim-send-btn').click();
        }
    },

    /**
     * Highlight patterns in text
     */
    highlightPatterns: function (text) {
        // This would ideally come from the backend or a comprehensive list
        // Simple regex for demonstration
        const patterns = [
            'centralization', 'suppression', 'power consolidation',
            'information control', 'authority', 'manipulation',
            'mechanism', 'protocol', 'lattice', 'vector'
        ];

        let processed = text;
        patterns.forEach(pat => {
            const regex = new RegExp(`\\b${pat}\\b`, 'gi');
            processed = processed.replace(regex, `<span class="pattern">$&</span>`);
        });
        return processed;
    },

    /**
     * Highlight entities/proper nouns (Simplified)
     */
    highlightEntities: function (text) {
        // Very basic heuristic: Look for capitalized words that aren't start of sentence
        // In production, backend should wrap entities in markers like [[Entity]]
        return text.replace(/\[\[(.*?)\]\]/g, '<span class="entity">$1</span>');
    },

    /**
     * Basic Markdown to HTML (Paragraphs, Bold, Italic, Lists)
     */
    processStandardText: function (text) {
        // Escape HTML first for safety
        const safeText = this.escapeHtml(text);
        return this.formatMarkdown(safeText);
    },

    formatMarkdown: function (text) {
        if (!text) return '';

        // Bold
        text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

        // Italic
        text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');

        // Links (careful with XSS here too, but simple regex assumes well-formed markdown)
        text = text.replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank">$1</a>');

        // Lists
        text = text.replace(/^\s*-\s+(.*)$/gm, '<li>$1</li>');
        text = text.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');

        // Paragraphs (double newline)
        const paragraphs = text.split(/\n\s*\n/);
        return paragraphs.map(p => {
            if (p.trim().startsWith('<ul') || p.trim().startsWith('<li')) return p;
            return `<p>${p}</p>`;
        }).join('');
    },

    escapeHtml: function (text) {
        return text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    },

    // SVG Icons
    icons: {
        reEnter: `<svg width="20" height="20" viewBox="0 0 20 20" fill="none"><path d="M4 10C4 6.68629 6.68629 4 10 4C13.3137 4 16 6.68629 16 10" stroke="url(#grad1)" stroke-width="2" stroke-linecap="round"/><path d="M13 7L16 10L13 13" stroke="url(#grad1)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
        trace: `<svg width="20" height="20" viewBox="0 0 20 20" fill="none"><circle cx="10" cy="10" r="7" stroke="url(#grad2)" stroke-width="2"/><path d="M10 3V10L14 14" stroke="url(#grad2)" stroke-width="2" stroke-linecap="round"/><circle cx="10" cy="10" r="2" fill="url(#grad2)"/></svg>`,
        coldRead: `<svg width="20" height="20" viewBox="0 0 20 20" fill="none"><path d="M2 10C2 10 5 4 10 4C15 4 18 10 18 10C18 10 15 16 10 16C5 16 2 10 2 10Z" stroke="url(#grad3)" stroke-width="2"/><circle cx="10" cy="10" r="3" stroke="url(#grad3)" stroke-width="2"/></svg>`
    },

    getSVGDefs: function () {
        return `
        <svg class="svg-defs">
            <defs>
                <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#8B5CF6"/>
                    <stop offset="100%" stop-color="#EC4899"/>
                </linearGradient>
                <linearGradient id="grad2" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#06B6D4"/>
                    <stop offset="100%" stop-color="#3B82F6"/>
                </linearGradient>
                <linearGradient id="grad3" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#F59E0B"/>
                    <stop offset="100%" stop-color="#EF4444"/>
                </linearGradient>
            </defs>
        </svg>
        `;
    }
};

// Export to global scope
window.ForensicUI = ForensicUI;
