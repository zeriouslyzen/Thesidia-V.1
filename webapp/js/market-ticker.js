/**
 * Katanx Market Ticker Component
 * Real-time crypto and stock price ticker for Nexus dashboard
 * 
 * Features:
 * - Crypto: BTC, ETH, SOL, XRP (customizable)
 * - Stocks: NASDAQ, Gold, Silver
 * - Real-time updates every 30 seconds
 * - Add/remove assets
 */

class MarketTicker {
    constructor(options = {}) {
        this.container = options.container || document.getElementById('market-ticker');
        this.updateInterval = options.updateInterval || 30000; // 30 seconds
        this.cryptoAssets = options.cryptoAssets || ['bitcoin', 'ethereum', 'solana', 'ripple'];
        this.stockAssets = options.stockAssets || ['NASDAQ', 'GOLD', 'SILVER'];

        this.prices = {};
        this.updateTimer = null;

        this.init();
    }

    init() {
        this.render();
        this.fetchPrices();
        this.startAutoUpdate();
    }

    render() {
        if (!this.container) return;

        this.container.innerHTML = `
            <div class="ticker-row crypto-row">
                <div class="ticker-label">CRYPTO</div>
                <div class="ticker-items" id="crypto-items"></div>
                <button class="ticker-add-btn" onclick="marketTicker.addAsset('crypto')" title="Add crypto">
                    <i data-lucide="plus"></i>
                </button>
            </div>
            <div class="ticker-row stocks-row">
                <div class="ticker-label">MARKETS</div>
                <div class="ticker-items" id="stock-items"></div>
                <button class="ticker-add-btn" onclick="marketTicker.addAsset('stock')" title="Add stock">
                    <i data-lucide="plus"></i>
                </button>
            </div>
        `;

        // Initialize Lucide icons
        if (window.lucide) {
            lucide.createIcons();
        }
    }

    async fetchPrices() {
        await Promise.all([
            this.fetchCryptoPrices(),
            this.fetchStockPrices()
        ]);
        this.updateDisplay();
    }

    async fetchCryptoPrices() {
        try {
            const ids = this.cryptoAssets.join(',');
            const response = await fetch(`/api/market/crypto?symbols=${ids}`);
            const data = await response.json();

            // Merge with existing prices
            Object.assign(this.prices, data);
        } catch (error) {
            console.error('Failed to fetch crypto prices:', error);
        }
    }

    async fetchStockPrices() {
        try {
            const symbols = this.stockAssets.join(',');
            const response = await fetch(`/api/market/stocks?symbols=${symbols}`);
            const data = await response.json();

            // Merge with existing prices
            Object.assign(this.prices, data);
        } catch (error) {
            console.error('Failed to fetch stock prices:', error);
        }
    }

    updateDisplay() {
        this.updateCryptoDisplay();
        this.updateStockDisplay();
    }

    updateCryptoDisplay() {
        const container = document.getElementById('crypto-items');
        if (!container) return;

        container.innerHTML = this.cryptoAssets.map(asset => {
            const data = this.prices[asset];
            if (!data) return '';

            const changeClass = data.change_24h >= 0 ? 'positive' : 'negative';
            const changeIcon = data.change_24h >= 0 ? '▲' : '▼';

            return `
                <div class="ticker-item">
                    <span class="ticker-symbol">${data.symbol || asset.toUpperCase()}</span>
                    <span class="ticker-price">$${this.formatPrice(data.price)}</span>
                    <span class="ticker-change ${changeClass}">
                        ${changeIcon} ${Math.abs(data.change_24h).toFixed(2)}%
                    </span>
                    <button class="ticker-remove-btn" onclick="marketTicker.removeAsset('crypto', '${asset}')" title="Remove">
                        <i data-lucide="x"></i>
                    </button>
                </div>
            `;
        }).join('');

        // Re-initialize Lucide icons
        if (window.lucide) {
            lucide.createIcons();
        }
    }

    updateStockDisplay() {
        const container = document.getElementById('stock-items');
        if (!container) return;

        container.innerHTML = this.stockAssets.map(asset => {
            const data = this.prices[asset];
            if (!data) return '';

            const changeClass = data.change >= 0 ? 'positive' : 'negative';
            const changeIcon = data.change >= 0 ? '▲' : '▼';

            return `
                <div class="ticker-item">
                    <span class="ticker-symbol">${asset}</span>
                    <span class="ticker-price">$${this.formatPrice(data.price)}</span>
                    <span class="ticker-change ${changeClass}">
                        ${changeIcon} ${Math.abs(data.change).toFixed(2)}%
                    </span>
                    <button class="ticker-remove-btn" onclick="marketTicker.removeAsset('stock', '${asset}')" title="Remove">
                        <i data-lucide="x"></i>
                    </button>
                </div>
            `;
        }).join('');

        // Re-initialize Lucide icons
        if (window.lucide) {
            lucide.createIcons();
        }
    }

    formatPrice(price) {
        if (price >= 1000) {
            return price.toLocaleString('en-US', { maximumFractionDigits: 0 });
        } else if (price >= 1) {
            return price.toLocaleString('en-US', { maximumFractionDigits: 2 });
        } else {
            return price.toLocaleString('en-US', { maximumFractionDigits: 4 });
        }
    }

    startAutoUpdate() {
        this.updateTimer = setInterval(() => {
            this.fetchPrices();
        }, this.updateInterval);
    }

    stopAutoUpdate() {
        if (this.updateTimer) {
            clearInterval(this.updateTimer);
            this.updateTimer = null;
        }
    }

    addAsset(type) {
        const assetName = prompt(`Enter ${type} asset name (e.g., ${type === 'crypto' ? 'dogecoin' : 'AAPL'}):`);
        if (!assetName) return;

        if (type === 'crypto') {
            if (!this.cryptoAssets.includes(assetName.toLowerCase())) {
                this.cryptoAssets.push(assetName.toLowerCase());
                this.savePreferences();
                this.fetchPrices();
            }
        } else {
            if (!this.stockAssets.includes(assetName.toUpperCase())) {
                this.stockAssets.push(assetName.toUpperCase());
                this.savePreferences();
                this.fetchPrices();
            }
        }
    }

    removeAsset(type, asset) {
        if (type === 'crypto') {
            this.cryptoAssets = this.cryptoAssets.filter(a => a !== asset);
        } else {
            this.stockAssets = this.stockAssets.filter(a => a !== asset);
        }
        this.savePreferences();
        this.updateDisplay();
    }

    savePreferences() {
        localStorage.setItem('marketTicker_crypto', JSON.stringify(this.cryptoAssets));
        localStorage.setItem('marketTicker_stocks', JSON.stringify(this.stockAssets));
    }

    loadPreferences() {
        const savedCrypto = localStorage.getItem('marketTicker_crypto');
        const savedStocks = localStorage.getItem('marketTicker_stocks');

        if (savedCrypto) {
            this.cryptoAssets = JSON.parse(savedCrypto);
        }
        if (savedStocks) {
            this.stockAssets = JSON.parse(savedStocks);
        }
    }

    destroy() {
        this.stopAutoUpdate();
    }
}

// Initialize on page load
let marketTicker;
document.addEventListener('DOMContentLoaded', () => {
    marketTicker = new MarketTicker();
});
