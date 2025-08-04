import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import time
from typing import List, Dict, Any
from tickers import SP500_TICKERS, NASDAQ100_TICKERS

class DataProcessor:
    def __init__(self):
        self.session = requests.Session()
        
    def get_ticker_universe(self, market_selection: str) -> List[str]:
        """Get ticker universe based on market selection"""
        if market_selection == "S&P 500":
            return SP500_TICKERS
        elif market_selection == "NASDAQ-100":
            return NASDAQ100_TICKERS
        else:  # Both
            return list(set(SP500_TICKERS + NASDAQ100_TICKERS))
    
    def filter_by_fundamentals(self, tickers: List[str], min_drop_pct: float, min_market_cap: float) -> pd.DataFrame:
        """Filter stocks by fundamental criteria"""
        results = []
        
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                
                # Get historical data (5 years)
                end_date = datetime.now()
                start_date = end_date - timedelta(days=1825)  # ~5 years
                
                hist_data = stock.history(start=start_date, end=end_date)
                if hist_data.empty:
                    continue
                
                # Calculate all-time high and current price
                ath = hist_data['Close'].max()
                current_price = hist_data['Close'].iloc[-1]
                drop_from_ath_pct = ((ath - current_price) / ath) * 100
                
                # Get market cap
                info = stock.info
                market_cap = info.get('marketCap', 0)
                
                # Apply filters
                if drop_from_ath_pct >= min_drop_pct and market_cap >= min_market_cap:
                    results.append({
                        'ticker': ticker,
                        'current_price': current_price,
                        'ath': ath,
                        'drop_from_ath_pct': drop_from_ath_pct,
                        'market_cap': market_cap,
                        'company_name': info.get('longName', ticker),
                        'sector': info.get('sector', 'Unknown'),
                        'hist_data': hist_data
                    })
                
                # Rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Error processing {ticker}: {str(e)}")
                continue
        
        return pd.DataFrame(results)
    
    def calculate_volatility_metrics(self, df: pd.DataFrame, min_iv_hv_ratio: float) -> pd.DataFrame:
        """Calculate historical volatility and mock implied volatility"""
        results = []
        
        for _, row in df.iterrows():
            try:
                hist_data = row['hist_data']
                
                # Calculate 30-day historical volatility
                returns = hist_data['Close'].pct_change().dropna()
                recent_returns = returns.tail(30)  # Last 30 days
                
                if len(recent_returns) < 20:  # Need sufficient data
                    continue
                
                # Annualized historical volatility
                hv = recent_returns.std() * np.sqrt(252) * 100  # Convert to percentage
                
                # Mock implied volatility (in production, use real options API)
                # Generate realistic IV that's typically higher than HV
                base_iv = hv * np.random.uniform(1.1, 2.5)  # IV usually higher than HV
                # Add some randomness but keep it realistic
                iv = base_iv + np.random.normal(0, hv * 0.1)
                iv = max(iv, hv * 1.05)  # Ensure IV is at least slightly higher than HV
                
                iv_hv_ratio = iv / hv if hv > 0 else 0
                
                # Apply IV/HV filter
                if iv_hv_ratio >= min_iv_hv_ratio:
                    result_row = row.copy()
                    result_row['historical_volatility'] = hv
                    result_row['implied_volatility'] = iv
                    result_row['iv_hv_ratio'] = iv_hv_ratio
                    
                    # Remove hist_data to save memory
                    del result_row['hist_data']
                    results.append(result_row)
                
            except Exception as e:
                print(f"Error calculating volatility for {row['ticker']}: {str(e)}")
                continue
        
        return pd.DataFrame(results)
    
    def check_earnings_calendar(self, df: pd.DataFrame) -> pd.DataFrame:
        """Check for upcoming earnings dates"""
        results = []
        
        for _, row in df.iterrows():
            try:
                ticker = row['ticker']
                stock = yf.Ticker(ticker)
                
                # Get calendar data
                calendar = stock.calendar
                earnings_date = None
                has_earnings = False
                
                if calendar is not None and not calendar.empty:
                    # Get next earnings date
                    next_earnings = calendar.index[0] if len(calendar.index) > 0 else None
                    
                    if next_earnings:
                        days_until_earnings = (next_earnings - datetime.now().date()).days
                        if 0 <= days_until_earnings <= 30:
                            has_earnings = True
                            earnings_date = next_earnings.strftime('%Y-%m-%d')
                
                # If no calendar data, try to get from info
                if not has_earnings:
                    info = stock.info
                    earnings_date = info.get('earningsDate', None)
                    if earnings_date:
                        # earningsDate is usually a timestamp
                        if isinstance(earnings_date, (int, float)):
                            earnings_dt = datetime.fromtimestamp(earnings_date)
                            days_until = (earnings_dt.date() - datetime.now().date()).days
                            if 0 <= days_until <= 30:
                                has_earnings = True
                                earnings_date = earnings_dt.strftime('%Y-%m-%d')
                            else:
                                earnings_date = None
                
                result_row = row.copy()
                result_row['earnings_date'] = earnings_date if earnings_date else 'N/A'
                result_row['has_earnings'] = has_earnings
                results.append(result_row)
                
                # Rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Error checking earnings for {row['ticker']}: {str(e)}")
                # Add row with no earnings data
                result_row = row.copy()
                result_row['earnings_date'] = 'N/A'
                result_row['has_earnings'] = False
                results.append(result_row)
                continue
        
        return pd.DataFrame(results)
    
    def get_stock_info(self, ticker: str) -> Dict[str, Any]:
        """Get additional stock information"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            return {
                'pe_ratio': info.get('trailingPE', None),
                'forward_pe': info.get('forwardPE', None),
                'peg_ratio': info.get('pegRatio', None),
                'price_to_book': info.get('priceToBook', None),
                'debt_to_equity': info.get('debtToEquity', None),
                'return_on_equity': info.get('returnOnEquity', None),
                'profit_margin': info.get('profitMargin', None),
                'beta': info.get('beta', None)
            }
        except Exception as e:
            print(f"Error getting stock info for {ticker}: {str(e)}")
            return {}
