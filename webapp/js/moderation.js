/**
 * Katanx Moderation Engine
 * 
 * Discord-style moderation with zero tolerance for hate/racism
 * but allowing casual profanity. Common sense, no nonsense.
 * 
 * @author Katanx Team
 */

const KatanxModeration = (function () {
    'use strict';

    // ═══════════════════════════════════════════════════════════════
    // CONFIGURATION
    // ═══════════════════════════════════════════════════════════════

    const Config = {
        // Timing
        SPAM_COOLDOWN_MS: 2000,        // 2 seconds between posts
        DUPLICATE_WINDOW_MS: 30000,    // 30 seconds to detect duplicates

        // Limits
        MAX_CAPS_RATIO: 0.7,           // Flag if >70% uppercase
        MAX_REPEAT_CHARS: 5,           // Flag repeated characters
        MAX_MENTIONS_PER_POST: 5,      // Mention spam threshold
        MAX_LINKS_PER_POST: 2,         // Link spam threshold
        MIN_WORD_LENGTH: 2,            // Min characters for a "word"

        // Escalation thresholds
        WARNINGS_BEFORE_MUTE: 3,
        MUTES_BEFORE_BAN: 2,
        MUTE_DURATION_MS: 10 * 60 * 1000  // 10 minutes
    };

    // ═══════════════════════════════════════════════════════════════
    // MODERATION ACTIONS
    // ═══════════════════════════════════════════════════════════════

    const Action = Object.freeze({
        ALLOW: 'allow',
        SHADOW_BLOCK: 'shadow_block',    // User sees it, others don't
        FLAG_FOR_REVIEW: 'flag_review',  // Goes to mod queue
        WARN: 'warn',                    // Inline warning
        TEMP_MUTE: 'temp_mute',          // Temporary mute
        BAN: 'ban'                       // Permanent
    });

    // ═══════════════════════════════════════════════════════════════
    // FILTER PATTERNS
    // ═══════════════════════════════════════════════════════════════

    // HARD BLOCK: Immediate action, no tolerance
    // These patterns use word boundaries to avoid false positives
    const HARD_BLOCK_PATTERNS = [
        // Racial slurs (using patterns to avoid storing full words)
        /\bn[i1][g9]{2,}[e3]r/i,
        /\bk[i1]k[e3]/i,
        /\bch[i1]nk/i,
        /\bsp[i1]c/i,
        /\bw[e3]tb[a4]ck/i,
        /\bc[o0]{2}n/i,
        /\bgr[o0](?:i|y)d/i,

        // Hate speech markers
        /\b(?:kill|murder|lynch|hang)\s+(?:all\s+)?(?:the\s+)?(?:jews?|blacks?|whites?|muslims?|gays?)/i,
        /\bhitler\s+(?:was|did)\s+(?:right|nothing\s+wrong)/i,
        /\b(?:gas|oven)\s+(?:the\s+)?jews?/i,
        /\bwhite\s*(?:power|supremacy)/i,
        /\brace\s*war/i,
        /\b14\s*88\b/,

        // Doxxing patterns
        /\b(?:dox+(?:ed|ing)?|leak(?:ed|ing)?)\s+(?:your|their|his|her)\s+(?:address|info|identity)/i,
        /\bi\s+know\s+where\s+you\s+live/i,

        // Threats
        /\bi['']?(?:ll|m\s+going\s+to|will)\s+(?:kill|murder|shoot|stab)\s+you/i,
        /\byou['']?(?:re|r)\s+(?:dead|gonna\s+die)/i,
        /\bkill\s+yourself/i,
        /\bkys\b/i
    ];

    // SOFT FLAG: Review queue, context-dependent
    const SOFT_FLAG_PATTERNS = [
        // Personal attacks
        /\byou['']?(?:re|r)\s+(?:an?\s+)?(?:idiot|moron|stupid|dumb|retard)/i,
        /\bshut\s+(?:the\s+fuck\s+)?up/i,
        /\bnobody\s+(?:cares|asked)/i,
        /\bgo\s+away/i,

        // Dismissive/uneducated opinion markers
        /\bi\s+don['']?t\s+(?:need|have)\s+(?:to\s+)?(?:prove|show|explain)/i,
        /\bdo\s+your\s+(?:own\s+)?research/i,
        /\bwake\s+up\s+sheeple?/i,
        /\bit['']s\s+(?:just\s+)?common\s+sense/i,

        // Excessive negativity
        /\bthis\s+(?:is\s+)?trash/i,
        /\bgarbage\s+(?:take|opinion|platform)/i,
        /\bunfollow(?:ed|ing)?/i,
        /\breport(?:ed|ing)?\s+(?:this|you)/i
    ];

    // ALLOWED: Explicitly permitted casual profanity
    const ALLOWED_WORDS = new Set([
        'shit', 'damn', 'hell', 'ass', 'crap', 'bastard',
        'piss', 'bollocks', 'bugger', 'bloody', 'sod',
        'dammit', 'goddamn', 'frickin', 'freaking'
    ]);

    // ═══════════════════════════════════════════════════════════════
    // USER STATE TRACKING
    // ═══════════════════════════════════════════════════════════════

    const userState = new Map();  // userId -> { warnings, mutes, lastPost, recentPosts }

    function getUserState(userId) {
        if (!userState.has(userId)) {
            userState.set(userId, {
                warnings: 0,
                mutes: 0,
                lastPostTime: 0,
                recentPosts: [],
                mutedUntil: 0
            });
        }
        return userState.get(userId);
    }

    // ═══════════════════════════════════════════════════════════════
    // CORE MODERATION FUNCTIONS
    // ═══════════════════════════════════════════════════════════════

    /**
     * Main moderation function - analyzes content and returns action
     * @param {string} content - The message content
     * @param {string} userId - The user's ID
     * @returns {Object} { action, reason, confidence }
     */
    function moderate(content, userId) {
        const state = getUserState(userId);
        const now = Date.now();

        // Check if user is muted
        if (state.mutedUntil > now) {
            return {
                action: Action.SHADOW_BLOCK,
                reason: 'User is temporarily muted',
                confidence: 1.0,
                muteRemaining: Math.ceil((state.mutedUntil - now) / 1000)
            };
        }

        // Spam detection
        const spamCheck = checkSpam(content, userId, state, now);
        if (spamCheck.action !== Action.ALLOW) {
            return spamCheck;
        }

        // Content analysis
        const contentCheck = analyzeContent(content);
        if (contentCheck.action !== Action.ALLOW) {
            return applyEscalation(contentCheck, state);
        }

        // Update state
        state.lastPostTime = now;
        state.recentPosts.push({ content, time: now });
        state.recentPosts = state.recentPosts.filter(p => now - p.time < Config.DUPLICATE_WINDOW_MS);

        return { action: Action.ALLOW, reason: null, confidence: 1.0 };
    }

    /**
     * Check for spam behavior
     */
    function checkSpam(content, userId, state, now) {
        // Rate limiting
        if (now - state.lastPostTime < Config.SPAM_COOLDOWN_MS) {
            return {
                action: Action.SHADOW_BLOCK,
                reason: 'Rate limited - posting too fast',
                confidence: 1.0
            };
        }

        // Duplicate detection
        const isDuplicate = state.recentPosts.some(p =>
            similarity(p.content, content) > 0.85
        );
        if (isDuplicate) {
            return {
                action: Action.WARN,
                reason: 'Duplicate message detected',
                confidence: 0.9
            };
        }

        // Mention spam
        const mentions = (content.match(/@\w+/g) || []).length;
        if (mentions > Config.MAX_MENTIONS_PER_POST) {
            return {
                action: Action.FLAG_FOR_REVIEW,
                reason: 'Excessive mentions',
                confidence: 0.8
            };
        }

        // Link spam
        const links = (content.match(/https?:\/\/\S+/g) || []).length;
        if (links > Config.MAX_LINKS_PER_POST) {
            return {
                action: Action.FLAG_FOR_REVIEW,
                reason: 'Excessive links',
                confidence: 0.8
            };
        }

        return { action: Action.ALLOW };
    }

    /**
     * Analyze content for violations
     */
    function analyzeContent(content) {
        const normalized = content.toLowerCase().trim();

        // HARD BLOCK check
        for (const pattern of HARD_BLOCK_PATTERNS) {
            if (pattern.test(content)) {
                return {
                    action: Action.BAN,
                    reason: 'Severe violation detected',
                    confidence: 0.95,
                    category: 'HARD_BLOCK'
                };
            }
        }

        // SOFT FLAG check
        for (const pattern of SOFT_FLAG_PATTERNS) {
            if (pattern.test(content)) {
                return {
                    action: Action.FLAG_FOR_REVIEW,
                    reason: 'Potential violation - needs review',
                    confidence: 0.7,
                    category: 'SOFT_FLAG'
                };
            }
        }

        // CAPS check (shouting)
        const letters = content.replace(/[^a-zA-Z]/g, '');
        const uppercaseRatio = letters.length > 10
            ? (letters.match(/[A-Z]/g) || []).length / letters.length
            : 0;
        if (uppercaseRatio > Config.MAX_CAPS_RATIO) {
            return {
                action: Action.WARN,
                reason: 'Excessive caps - feels like shouting',
                confidence: 0.6,
                category: 'CAPS'
            };
        }

        // Repeated character check
        if (/(.)\1{4,}/i.test(content)) {
            return {
                action: Action.WARN,
                reason: 'Repeated characters detected',
                confidence: 0.5,
                category: 'SPAM_PATTERN'
            };
        }

        return { action: Action.ALLOW };
    }

    /**
     * Apply escalation based on user history
     */
    function applyEscalation(result, state) {
        if (result.action === Action.BAN) {
            // Immediate ban for hard blocks
            return result;
        }

        if (result.action === Action.WARN) {
            state.warnings++;
            if (state.warnings >= Config.WARNINGS_BEFORE_MUTE) {
                state.warnings = 0;
                state.mutes++;
                state.mutedUntil = Date.now() + Config.MUTE_DURATION_MS;

                if (state.mutes >= Config.MUTES_BEFORE_BAN) {
                    return {
                        ...result,
                        action: Action.BAN,
                        reason: 'Repeated violations - escalated to ban'
                    };
                }

                return {
                    ...result,
                    action: Action.TEMP_MUTE,
                    reason: `Too many warnings - muted for ${Config.MUTE_DURATION_MS / 60000} minutes`
                };
            }
        }

        return result;
    }

    // ═══════════════════════════════════════════════════════════════
    // UTILITY FUNCTIONS
    // ═══════════════════════════════════════════════════════════════

    /**
     * Simple string similarity (Jaccard-ish)
     */
    function similarity(a, b) {
        const setA = new Set(a.toLowerCase().split(/\s+/));
        const setB = new Set(b.toLowerCase().split(/\s+/));
        const intersection = new Set([...setA].filter(x => setB.has(x)));
        const union = new Set([...setA, ...setB]);
        return intersection.size / union.size;
    }

    /**
     * Check if a word is in the allowed list
     */
    function isAllowedProfanity(word) {
        return ALLOWED_WORDS.has(word.toLowerCase());
    }

    /**
     * Clean content for display (redact violations)
     */
    function redactContent(content) {
        let cleaned = content;
        for (const pattern of HARD_BLOCK_PATTERNS) {
            cleaned = cleaned.replace(pattern, '[redacted]');
        }
        return cleaned;
    }

    /**
     * Reset user state (for admin use)
     */
    function resetUserState(userId) {
        userState.delete(userId);
    }

    /**
     * Get moderation stats
     */
    function getStats() {
        let totalWarnings = 0;
        let totalMutes = 0;
        userState.forEach(state => {
            totalWarnings += state.warnings;
            totalMutes += state.mutes;
        });
        return {
            trackedUsers: userState.size,
            totalWarnings,
            totalMutes
        };
    }

    // ═══════════════════════════════════════════════════════════════
    // PUBLIC API
    // ═══════════════════════════════════════════════════════════════

    return {
        moderate,
        Action,
        Config,
        isAllowedProfanity,
        redactContent,
        resetUserState,
        getStats,
        getUserState
    };

})();

// Export for Node.js / testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = KatanxModeration;
}
