/**
 * Thesidia Edge Inference Module
 * ==============================
 * Powered by WebLLM (MLC-LLM)
 * Tiered model system with auto-detection of device capabilities.
 *
 * Model tiers:
 *   high   -- Qwen 2.5 3B  (best reasoning, ~3 GB VRAM)
 *   medium -- Llama 3.2 3B  (balanced speed/quality, ~2 GB VRAM)
 *   light  -- Llama 3.2 1B  (fastest, works on phones, ~1.6 GB VRAM)
 */

import { CreateMLCEngine } from "https://esm.run/@mlc-ai/web-llm";

const MODEL_TIERS = [
    {
        id: 'high',
        name: 'Qwen 2.5 3B (Best Quality)',
        model: 'Qwen2.5-3B-Instruct-q4f16_1-MLC',
        vramRequired: 3000, // MB
        description: 'Best reasoning, recommended for desktops'
    },
    {
        id: 'medium',
        name: 'Llama 3.2 3B (Balanced)',
        model: 'Llama-3.2-3B-Instruct-q4f16_1-MLC',
        vramRequired: 2000,
        description: 'Good balance of speed and quality'
    },
    {
        id: 'light',
        name: 'Llama 3.2 1B (Fast)',
        model: 'Llama-3.2-1B-Instruct-q4f16_1-MLC',
        vramRequired: 1600,
        description: 'Fastest, works on phones and low-end devices'
    }
];

class EdgeInference {
    constructor() {
        this.engine = null;
        this.modelId = null;
        this.currentTier = null;
        this.isLoaded = false;
        this.isLoading = false;
        this.progressCallback = null;
        this.detectedVRAM = null;
    }

    /**
     * Detect available VRAM via WebGPU adapter info.
     * Returns estimated VRAM in MB, or null if unavailable.
     */
    async detectVRAM() {
        if (this.detectedVRAM !== null) return this.detectedVRAM;
        try {
            if (!navigator.gpu) return null;
            const adapter = await navigator.gpu.requestAdapter();
            if (!adapter) return null;
            // maxBufferSize is the best proxy for VRAM budget in WebGPU
            const info = adapter.limits;
            const maxBuffer = info.maxBufferSize || 0;
            // Convert bytes to MB (rough estimate -- actual VRAM may differ)
            this.detectedVRAM = Math.round(maxBuffer / (1024 * 1024));
            console.log(`[EdgeInference] Detected VRAM budget: ~${this.detectedVRAM} MB`);
            return this.detectedVRAM;
        } catch (e) {
            console.warn("[EdgeInference] VRAM detection failed:", e);
            return null;
        }
    }

    /**
     * Select the best model tier for this device.
     * @param {string} preferredTier - "auto", "high", "medium", or "light"
     */
    async selectTier(preferredTier = 'auto') {
        if (preferredTier !== 'auto') {
            const tier = MODEL_TIERS.find(t => t.id === preferredTier);
            if (tier) {
                this.currentTier = tier;
                this.modelId = tier.model;
                console.log(`[EdgeInference] Manual tier: ${tier.name}`);
                return tier;
            }
        }

        // Auto-select based on VRAM
        const vram = await this.detectVRAM();
        if (vram === null) {
            // Cannot detect -- default to light for safety
            const fallback = MODEL_TIERS.find(t => t.id === 'light');
            this.currentTier = fallback;
            this.modelId = fallback.model;
            console.log(`[EdgeInference] VRAM unknown, defaulting to: ${fallback.name}`);
            return fallback;
        }

        // Pick highest tier the device can handle
        for (const tier of MODEL_TIERS) {
            if (vram >= tier.vramRequired) {
                this.currentTier = tier;
                this.modelId = tier.model;
                console.log(`[EdgeInference] Auto-selected: ${tier.name} (VRAM: ${vram} MB >= ${tier.vramRequired} MB)`);
                return tier;
            }
        }

        // Fallback to lightest
        const lightest = MODEL_TIERS[MODEL_TIERS.length - 1];
        this.currentTier = lightest;
        this.modelId = lightest.model;
        console.log(`[EdgeInference] Low VRAM (${vram} MB), falling back to: ${lightest.name}`);
        return lightest;
    }

    /**
     * Set a specific tier (called from UI settings).
     * If a model is already loaded, it will be unloaded on next init.
     */
    setTier(tierId) {
        const oldModel = this.modelId;
        this.selectTier(tierId);
        if (this.isLoaded && this.modelId !== oldModel) {
            // Model changed -- mark as needing reload
            this.isLoaded = false;
            this.engine = null;
            console.log(`[EdgeInference] Model changed. Will reload on next use.`);
        }
    }

    /**
     * Initialize the WebLLM engine with the selected model.
     * @param {Function} onProgress - Callback for loading progress updates
     */
    async init(onProgress) {
        if (this.isLoaded) return;
        if (this.isLoading) return;

        this.isLoading = true;
        this.progressCallback = onProgress;

        // Ensure a model is selected
        if (!this.modelId) {
            const savedTier = (typeof localStorage !== 'undefined') ? localStorage.getItem('edgeModelTier') : null;
            await this.selectTier(savedTier || 'auto');
        }

        console.log(`[EdgeInference] Initializing with model: ${this.modelId}`);

        try {
            this.engine = await CreateMLCEngine(this.modelId, {
                initProgressCallback: (report) => {
                    if (this.progressCallback) this.progressCallback(report);
                    console.log("[EdgeInference]", report.text);
                }
            });
            this.isLoaded = true;
            this.isLoading = false;
            console.log("[EdgeInference] Engine Ready --", this.currentTier?.name || this.modelId);
        } catch (error) {
            this.isLoading = false;
            console.error("[EdgeInference] Initialization Failed:", error);
            if (!navigator.gpu) {
                console.error("[EdgeInference] WebGPU is not supported in this browser.");
            }
            throw error;
        }
    }

    /**
     * Generate a chat completion.
     * @param {string} prompt - User message
     * @param {string} systemPrompt - System instructions
     * @returns {Promise<string>} Model response text
     */
    async generate(prompt, systemPrompt = "You are Thesidia, an advanced AI research engine. Be conversational, insightful, and precise.") {
        if (!this.isLoaded) {
            await this.init();
        }

        const messages = [
            { role: "system", content: systemPrompt },
            { role: "user", content: prompt }
        ];

        const reply = await this.engine.chat.completions.create({
            messages,
            stream: false
        });

        return reply.choices[0].message.content;
    }

    /**
     * Specialized: Perform bot detection/classification.
     * @param {string} text
     */
    async classifyBot(text) {
        const prompt = `Classify if the following text or user behavior is likely a bot.
Return only a JSON object: {"is_bot": boolean, "confidence": float, "reason": string}

Text: "${text}"`;

        const systemPrompt = "You are a cybersecurity expert specializing in social media bot detection.";

        try {
            const response = await this.generate(prompt, systemPrompt);
            const jsonMatch = response.match(/\{.*\}/s);
            if (jsonMatch) {
                return JSON.parse(jsonMatch[0]);
            }
            return { is_bot: false, confidence: 0, reason: "Could not parse analysis" };
        } catch (error) {
            console.error("[EdgeInference] Bot classification error:", error);
            return { error: error.message };
        }
    }

    /**
     * Get information about available tiers.
     */
    getTiers() {
        return MODEL_TIERS.map(t => ({
            ...t,
            active: t.id === this.currentTier?.id,
            loaded: t.model === this.modelId && this.isLoaded
        }));
    }
}

// Create singleton and expose to window for the non-module app.js
const instance = new EdgeInference();
window.edgeInference = instance;

export default instance;
