# S&P 500 tickers (representative sample - in production, you'd load this dynamically)
SP500_TICKERS = [
    'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'NVDA', 'TSLA', 'META', 'TSM', 'UNH',
    'XOM', 'JNJ', 'JPM', 'V', 'PG', 'MA', 'HD', 'CVX', 'ABBV', 'PFE',
    'AVGO', 'LLY', 'KO', 'COST', 'PEP', 'TMO', 'WMT', 'MRK', 'DIS', 'ABT',
    'BAC', 'CRM', 'NFLX', 'ADBE', 'AMD', 'NKE', 'LIN', 'ORCL', 'WFC', 'ACN',
    'TXN', 'PM', 'RTX', 'QCOM', 'DHR', 'NEE', 'IBM', 'SPGI', 'T', 'UNP',
    'LOW', 'GS', 'HON', 'CAT', 'MDT', 'INTC', 'UPS', 'BLK', 'INTU', 'DE',
    'AXP', 'AMAT', 'CI', 'SYK', 'GILD', 'TJX', 'AMT', 'BKNG', 'MU', 'ADP',
    'TMUS', 'VRTX', 'CVS', 'LRCX', 'REGN', 'ZTS', 'SLB', 'PLD', 'MO', 'MMC',
    'FI', 'TGT', 'SO', 'CL', 'PYPL', 'BSX', 'BMY', 'BDX', 'ITW', 'EL',
    'CSX', 'CB', 'DUK', 'AON', 'SHW', 'APD', 'NOC', 'COP', 'CME', 'EQIX'
]

# NASDAQ-100 tickers (representative sample)
NASDAQ100_TICKERS = [
    'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'NVDA', 'TSLA', 'META', 'AVGO', 'COST',
    'NFLX', 'PEP', 'ADBE', 'CSCO', 'TMUS', 'CRM', 'TXN', 'QCOM', 'CMCSA', 'AMD',
    'INTC', 'INTU', 'AMGN', 'HON', 'AMAT', 'BKNG', 'ADP', 'GILD', 'MU', 'ADI',
    'LRCX', 'MELI', 'MDLZ', 'REGN', 'ISRG', 'PYPL', 'KLAC', 'SNPS', 'CDNS', 'MAR',
    'MRVL', 'ORLY', 'CSX', 'FTNT', 'ADSK', 'NXPI', 'WDAY', 'ABNB', 'CHTR', 'MNST',
    'TEAM', 'DXCM', 'AEP', 'EXC', 'KDP', 'FANG', 'ROST', 'VRSK', 'KHC', 'CCEP',
    'IDXX', 'CTAS', 'EA', 'FAST', 'ODFL', 'BKR', 'XEL', 'AZN', 'CTSH', 'GEHC',
    'PCAR', 'MRNA', 'ON', 'BIIB', 'PAYX', 'LULU', 'DDOG', 'WBD', 'ANSS', 'ZM',
    'SGEN', 'CRWD', 'DLTR', 'CSGP', 'WBA', 'LCID', 'SIRI', 'ZS', 'EBAY', 'GFS'
]

def get_sp500_tickers():
    """
    Get S&P 500 tickers. In production, this could fetch from:
    - Wikipedia S&P 500 list
    - Yahoo Finance API
    - Financial data providers
    """
    return SP500_TICKERS

def get_nasdaq100_tickers():
    """
    Get NASDAQ-100 tickers. In production, this could fetch from:
    - NASDAQ official API
    - Financial data providers
    """
    return NASDAQ100_TICKERS

def get_all_tickers():
    """Get combined list of all available tickers"""
    return list(set(SP500_TICKERS + NASDAQ100_TICKERS))

# Additional ticker lists for future expansion
DOW30_TICKERS = [
    'AAPL', 'MSFT', 'UNH', 'GS', 'HD', 'AMGN', 'MCD', 'CAT', 'CRM', 'V',
    'BA', 'AXP', 'TRV', 'JPM', 'JNJ', 'PG', 'CVX', 'NKE', 'MRK', 'WMT',
    'DIS', 'IBM', 'MMM', 'KO', 'HON', 'CSCO', 'INTC', 'VZ', 'WBA', 'DOW'
]

def get_dow30_tickers():
    """Get Dow Jones Industrial Average tickers"""
    return DOW30_TICKERS
