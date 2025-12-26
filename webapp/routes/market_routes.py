"""
Market Data Routes Blueprint - Crypto & Stock Prices

Handles real-time market data API endpoints:
- /api/market/crypto - Cryptocurrency prices from CoinGecko
- /api/market/stocks - Stock/commodity prices from Yahoo Finance
"""

import requests
from flask import jsonify, request
from webapp.routes import market_bp
from logger_setup import server_logger as logger


# Symbol name mappings
CRYPTO_SYMBOLS = {
    'bitcoin': 'BTC',
    'ethereum': 'ETH',
    'solana': 'SOL',
    'ripple': 'XRP',
    'cardano': 'ADA',
    'dogecoin': 'DOGE',
    'polkadot': 'DOT',
    'avalanche-2': 'AVAX'
}

STOCK_SYMBOLS = {
    '^IXIC': 'NASDAQ',
    'GC=F': 'GOLD',
    'SI=F': 'SILVER',
    '^GSPC': 'S&P 500',
    '^DJI': 'DOW'
}


@market_bp.route('/crypto', methods=['GET'])
def get_crypto_prices():
    """
    Get real-time cryptocurrency prices from CoinGecko API.
    Query params: symbols (comma-separated, e.g., bitcoin,ethereum,solana,ripple)
    """
    try:
        symbols = request.args.get('symbols', 'bitcoin,ethereum,solana,ripple')
        symbol_list = [s.strip() for s in symbols.split(',')]
        
        # CoinGecko API - free tier, no API key needed
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            'ids': ','.join(symbol_list),
            'vs_currencies': 'usd',
            'include_24hr_change': 'true'
        }
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return jsonify({'error': 'Failed to fetch crypto prices'}), 500
        
        data = response.json()
        
        # Format response
        result = {}
        for coin_id, coin_data in data.items():
            result[coin_id] = {
                'symbol': CRYPTO_SYMBOLS.get(coin_id, coin_id.upper()),
                'price': coin_data.get('usd', 0),
                'change_24h': coin_data.get('usd_24h_change', 0)
            }
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error fetching crypto prices: {e}")
        return jsonify({'error': str(e)}), 500


@market_bp.route('/stocks', methods=['GET'])
def get_stock_prices():
    """
    Get real-time stock/commodity prices using Yahoo Finance.
    Query params: symbols (comma-separated, e.g., ^IXIC,GC=F,SI=F)
    """
    try:
        symbols = request.args.get('symbols', '^IXIC,GC=F,SI=F')
        symbol_list = [s.strip() for s in symbols.split(',')]
        
        result = {}
        
        for symbol in symbol_list:
            try:
                # Yahoo Finance API (free, no key needed)
                url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
                params = {'interval': '1d', 'range': '5d'}
                
                response = requests.get(url, params=params, timeout=10)
                if response.status_code != 200:
                    continue
                
                data = response.json()
                quote = data.get('chart', {}).get('result', [{}])[0]
                meta = quote.get('meta', {})
                
                current_price = meta.get('regularMarketPrice', 0)
                previous_close = meta.get('previousClose', current_price)
                change_percent = ((current_price - previous_close) / previous_close * 100) if previous_close else 0
                
                result[STOCK_SYMBOLS.get(symbol, symbol)] = {
                    'price': current_price,
                    'change': change_percent
                }
            except Exception as e:
                logger.error(f"Error fetching {symbol}: {e}")
                continue
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error fetching stock prices: {e}")
        return jsonify({'error': str(e)}), 500
