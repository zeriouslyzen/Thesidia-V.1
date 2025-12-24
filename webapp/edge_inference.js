/**
 * Thesidia Edge Inference Module
 * ==============================
 * Powered by WebLLM (MLC-LLM)
 * Runs Llama 3.2 1B directly in the browser using WebGPU.
 */

import { CreateMLCEngine } from "https://esm.run/@mlc-ai/web-llm";

class EdgeInference {
    constructor() {
        this.engine = null;
        this.modelId = "Llama-3.2-1B-Instruct-q4f16_1-MLC";
        this.isLoaded = false;
        this.isLoading = false;
        this.progressCallback = null;
    }

    /**
     * Initialize the WebLLM engine
     * @param {Function} onProgress - Callback for loading progress
     */
    async init(onProgress) {
        if (this.isLoaded) return;
        if (this.isLoading) return;

        this.isLoading = true;
        this.progressCallback = onProgress;

        console.log("Initializing Edge Inference (WebLLM)...");

        try {
            this.engine = await CreateMLCEngine(this.modelId, {
                initProgressCallback: (report) => {
                    if (this.progressCallback) this.progressCallback(report);
                    console.log("Edge Init:", report.text);
                }
            });
            this.isLoaded = true;
            this.isLoading = false;
            console.log("Edge Inference Engine Ready");
        } catch (error) {
            this.isLoading = false;
            console.error("Edge Inference Initialization Failed:", error);
            // Check if WebGPU is available
            if (!navigator.gpu) {
                console.error("WebGPU is not supported in this browser.");
            }
            throw error;
        }
    }

    /**
     * Generate completion
     * @param {string} prompt 
     * @param {string} systemPrompt 
     */
    async generate(prompt, systemPrompt = "You are Thesidia, an advanced AI engine. Respond casually and insightfully.") {
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
     * Specialized: Perform bot detection/classification
     * @param {string} text 
     */
    async classifyBot(text) {
        const prompt = `Classify if the following text or user behavior is likely a bot. 
Return only a JSON object: {"is_bot": boolean, "confidence": float, "reason": string}

Text: "${text}"`;

        const systemPrompt = "You are a cybersecurity expert specializing in social media bot detection.";

        try {
            const response = await this.generate(prompt, systemPrompt);
            // Extract JSON
            const jsonMatch = response.match(/\{.*\}/s);
            if (jsonMatch) {
                return JSON.parse(jsonMatch[0]);
            }
            return { is_bot: false, confidence: 0, reason: "Could not parse analysis" };
        } catch (error) {
            console.error("Bot classification error:", error);
            return { error: error.message };
        }
    }
}

// Create singleton instance and expose to window for the non-module app.js
const instance = new EdgeInference();
window.edgeInference = instance;

export default instance;
