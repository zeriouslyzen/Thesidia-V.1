/**
 * Input Validation Utilities
 * Comprehensive validation for all API inputs
 */

/**
 * Validate user ID format
 * @param {string} user_id - User ID to validate
 * @returns {Object} {valid: boolean, error?: string}
 */
export function validateUserId(user_id) {
    if (!user_id) {
        return { valid: false, error: 'User ID is required' };
    }
    if (typeof user_id !== 'string') {
        return { valid: false, error: 'User ID must be a string' };
    }
    if (user_id.length < 3 || user_id.length > 100) {
        return { valid: false, error: 'User ID must be between 3 and 100 characters' };
    }
    if (!/^[a-zA-Z0-9_-]+$/.test(user_id)) {
        return { valid: false, error: 'User ID contains invalid characters' };
    }
    return { valid: true };
}

/**
 * Validate session ID format
 * @param {string} session_id - Session ID to validate
 * @returns {Object} {valid: boolean, error?: string}
 */
export function validateSessionId(session_id) {
    if (!session_id) {
        return { valid: false, error: 'Session ID is required' };
    }
    if (typeof session_id !== 'string') {
        return { valid: false, error: 'Session ID must be a string' };
    }
    if (session_id.length < 10 || session_id.length > 200) {
        return { valid: false, error: 'Session ID must be between 10 and 200 characters' };
    }
    return { valid: true };
}

/**
 * Validate post content
 * @param {string} content - Post content to validate
 * @param {number} maxLength - Maximum length (default 10000)
 * @returns {Object} {valid: boolean, error?: string}
 */
export function validatePostContent(content, maxLength = 10000) {
    if (!content) {
        return { valid: false, error: 'Content is required' };
    }
    if (typeof content !== 'string') {
        return { valid: false, error: 'Content must be a string' };
    }
    if (content.length > maxLength) {
        return { valid: false, error: `Content must be no more than ${maxLength} characters` };
    }
    if (content.trim().length === 0) {
        return { valid: false, error: 'Content cannot be empty' };
    }
    return { valid: true };
}

/**
 * Validate post ID format
 * @param {string} post_id - Post ID to validate
 * @returns {Object} {valid: boolean, error?: string}
 */
export function validatePostId(post_id) {
    if (!post_id) {
        return { valid: false, error: 'Post ID is required' };
    }
    if (typeof post_id !== 'string') {
        return { valid: false, error: 'Post ID must be a string' };
    }
    if (post_id.length < 5 || post_id.length > 100) {
        return { valid: false, error: 'Post ID must be between 5 and 100 characters' };
    }
    if (!/^[a-zA-Z0-9_-]+$/.test(post_id)) {
        return { valid: false, error: 'Post ID contains invalid characters' };
    }
    return { valid: true };
}

/**
 * Validate pagination parameters
 * @param {number} limit - Items per page
 * @param {number} offset - Offset
 * @param {number} maxLimit - Maximum limit (default 100)
 * @returns {Object} {valid: boolean, error?: string, limit?: number, offset?: number}
 */
export function validatePagination(limit, offset, maxLimit = 100) {
    const limitNum = parseInt(limit, 10);
    const offsetNum = parseInt(offset, 10);
    
    if (isNaN(limitNum) || limitNum < 1) {
        return { valid: false, error: 'Limit must be a positive integer' };
    }
    if (limitNum > maxLimit) {
        return { valid: false, error: `Limit cannot exceed ${maxLimit}` };
    }
    if (isNaN(offsetNum) || offsetNum < 0) {
        return { valid: false, error: 'Offset must be a non-negative integer' };
    }
    
    return { valid: true, limit: limitNum, offset: offsetNum };
}

/**
 * Validate feed type
 * @param {string} feed_type - Feed type to validate
 * @returns {Object} {valid: boolean, error?: string}
 */
export function validateFeedType(feed_type) {
    const validTypes = ['chronological', 'quality', 'personalized'];
    if (!feed_type) {
        return { valid: false, error: 'Feed type is required' };
    }
    if (!validTypes.includes(feed_type)) {
        return { valid: false, error: `Feed type must be one of: ${validTypes.join(', ')}` };
    }
    return { valid: true };
}

/**
 * Validate comment content
 * @param {string} content - Comment content
 * @param {number} maxLength - Maximum length (default 5000)
 * @returns {Object} {valid: boolean, error?: string}
 */
export function validateCommentContent(content, maxLength = 5000) {
    if (!content) {
        return { valid: false, error: 'Comment content is required' };
    }
    if (typeof content !== 'string') {
        return { valid: false, error: 'Comment content must be a string' };
    }
    if (content.length > maxLength) {
        return { valid: false, error: `Comment must be no more than ${maxLength} characters` };
    }
    if (content.trim().length === 0) {
        return { valid: false, error: 'Comment cannot be empty' };
    }
    return { valid: true };
}

/**
 * Validate media array
 * @param {Array} media - Media array
 * @param {number} maxItems - Maximum items (default 10)
 * @returns {Object} {valid: boolean, error?: string}
 */
export function validateMedia(media, maxItems = 10) {
    if (!Array.isArray(media)) {
        return { valid: false, error: 'Media must be an array' };
    }
    if (media.length > maxItems) {
        return { valid: false, error: `Cannot attach more than ${maxItems} media items` };
    }
    
    for (const item of media) {
        if (typeof item !== 'object' || !item.type || !item.url) {
            return { valid: false, error: 'Each media item must have type and url' };
        }
        if (!['image', 'video'].includes(item.type)) {
            return { valid: false, error: 'Media type must be "image" or "video"' };
        }
        if (typeof item.url !== 'string' || item.url.length === 0) {
            return { valid: false, error: 'Media URL must be a non-empty string' };
        }
    }
    
    return { valid: true };
}

/**
 * Validate tags array
 * @param {Array} tags - Tags array
 * @param {number} maxItems - Maximum items (default 20)
 * @returns {Object} {valid: boolean, error?: string}
 */
export function validateTags(tags, maxItems = 20) {
    if (!Array.isArray(tags)) {
        return { valid: false, error: 'Tags must be an array' };
    }
    if (tags.length > maxItems) {
        return { valid: false, error: `Cannot use more than ${maxItems} tags` };
    }
    
    for (const tag of tags) {
        if (typeof tag !== 'string') {
            return { valid: false, error: 'Each tag must be a string' };
        }
        if (tag.length === 0 || tag.length > 50) {
            return { valid: false, error: 'Each tag must be between 1 and 50 characters' };
        }
        if (!/^[a-zA-Z0-9_#-]+$/.test(tag)) {
            return { valid: false, error: 'Tags can only contain letters, numbers, underscores, hyphens, and #' };
        }
    }
    
    return { valid: true };
}

/**
 * Validate visibility setting
 * @param {string} visibility - Visibility setting
 * @returns {Object} {valid: boolean, error?: string}
 */
export function validateVisibility(visibility) {
    const validValues = ['public', 'followers', 'private'];
    if (!visibility) {
        return { valid: false, error: 'Visibility is required' };
    }
    if (!validValues.includes(visibility)) {
        return { valid: false, error: `Visibility must be one of: ${validValues.join(', ')}` };
    }
    return { valid: true };
}

/**
 * Validate message content (for Thesidia API)
 * @param {string} message - Message content
 * @param {number} maxLength - Maximum length (default 10000)
 * @returns {Object} {valid: boolean, error?: string}
 */
export function validateMessage(message, maxLength = 10000) {
    if (!message) {
        return { valid: false, error: 'Message is required' };
    }
    if (typeof message !== 'string') {
        return { valid: false, error: 'Message must be a string' };
    }
    if (message.length > maxLength) {
        return { valid: false, error: `Message must be no more than ${maxLength} characters` };
    }
    if (message.trim().length === 0) {
        return { valid: false, error: 'Message cannot be empty' };
    }
    return { valid: true };
}

