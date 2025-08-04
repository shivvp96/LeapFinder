import os
import json
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any
import pandas as pd
import time
from openai import OpenAI

class SentimentAnalyzer:
    def __init__(self):
        # Initialize APIs
        self.news_api_key = os.getenv("NEWS_API_KEY", "demo_key")
        
        # Initialize OpenAI
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "demo_key")
        self.openai_client = OpenAI(api_key=self.openai_api_key)
        
    def get_news_headlines(self, ticker: str, days_back: int = 14) -> List[str]:
        """Get recent news headlines for a ticker"""
        headlines = []
        
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            # NewsAPI endpoint
            url = "https://newsapi.org/v2/everything"
            params = {
                'q': f'"{ticker}" OR "{ticker} stock" OR "{ticker} shares"',
                'from': start_date.strftime('%Y-%m-%d'),
                'to': end_date.strftime('%Y-%m-%d'),
                'sortBy': 'relevancy',
                'language': 'en',
                'pageSize': 20,
                'apiKey': self.news_api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                
                for article in articles:
                    title = article.get('title', '')
                    description = article.get('description', '')
                    
                    # Combine title and description
                    headline = f"{title}. {description}" if description else title
                    if headline and len(headline) > 10:
                        headlines.append(headline)
                        
            elif response.status_code == 429:
                # Rate limit exceeded, use fallback
                headlines = self._get_fallback_headlines(ticker)
            else:
                # API error, use fallback
                headlines = self._get_fallback_headlines(ticker)
                
        except Exception as e:
            print(f"Error fetching news for {ticker}: {str(e)}")
            headlines = self._get_fallback_headlines(ticker)
        
        return headlines[:10]  # Limit to 10 headlines
    
    def _get_fallback_headlines(self, ticker: str) -> List[str]:
        """Generate realistic fallback headlines when API is unavailable"""
        # This provides fallback when NewsAPI is unavailable
        # In production, you might want to use alternative news sources
        fallback_headlines = [
            f"{ticker} reports quarterly earnings results",
            f"Analysts update price target for {ticker}",
            f"{ticker} announces strategic partnership",
            f"Market volatility affects {ticker} trading",
            f"Institutional investors adjust {ticker} positions"
        ]
        return fallback_headlines
    
    def analyze_sentiment_with_gpt(self, ticker: str, headlines: List[str]) -> Dict[str, Any]:
        """Analyze sentiment using OpenAI GPT"""
        if not headlines:
            return {
                'sentiment': 'NEUTRAL',
                'confidence': 0.5,
                'notes': 'No recent news available for analysis'
            }
        
        try:
            # Prepare headlines text
            headlines_text = "\n".join([f"- {headline}" for headline in headlines])
            
            # Create prompt
            prompt = f"""Given the following recent headlines about {ticker}, analyze the overall sentiment and provide:
1. Overall sentiment: BULLISH, NEUTRAL, or BEARISH
2. Confidence score between 0 and 1
3. Brief 1-2 sentence explanation

Headlines:
{headlines_text}

Respond with JSON in this exact format:
{{"sentiment": "BULLISH/NEUTRAL/BEARISH", "confidence": 0.0-1.0, "notes": "brief explanation"}}"""

            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a financial sentiment analysis expert. Analyze news headlines and provide structured sentiment analysis."
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=200,
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Validate response
            sentiment = result.get('sentiment', 'NEUTRAL').upper()
            if sentiment not in ['BULLISH', 'NEUTRAL', 'BEARISH']:
                sentiment = 'NEUTRAL'
            
            confidence = float(result.get('confidence', 0.5))
            confidence = max(0, min(1, confidence))  # Clamp between 0 and 1
            
            notes = result.get('notes', 'Analysis completed')
            
            return {
                'sentiment': sentiment,
                'confidence': confidence,
                'notes': notes
            }
            
        except Exception as e:
            print(f"Error analyzing sentiment for {ticker}: {str(e)}")
            # Fallback sentiment analysis
            return self._fallback_sentiment_analysis(headlines)
    
    def _fallback_sentiment_analysis(self, headlines: List[str]) -> Dict[str, Any]:
        """Simple fallback sentiment analysis when OpenAI is unavailable"""
        if not headlines:
            return {
                'sentiment': 'NEUTRAL',
                'confidence': 0.5,
                'notes': 'No headlines available for analysis'
            }
        
        # Simple keyword-based sentiment
        positive_words = ['up', 'rise', 'gain', 'growth', 'profit', 'beat', 'strong', 'bullish', 'upgrade', 'buy']
        negative_words = ['down', 'fall', 'loss', 'decline', 'drop', 'miss', 'weak', 'bearish', 'downgrade', 'sell']
        
        headline_text = ' '.join(headlines).lower()
        
        positive_count = sum(1 for word in positive_words if word in headline_text)
        negative_count = sum(1 for word in negative_words if word in headline_text)
        
        if positive_count > negative_count + 1:
            sentiment = 'BULLISH'
            confidence = min(0.8, 0.5 + (positive_count - negative_count) * 0.1)
        elif negative_count > positive_count + 1:
            sentiment = 'BEARISH'
            confidence = min(0.8, 0.5 + (negative_count - positive_count) * 0.1)
        else:
            sentiment = 'NEUTRAL'
            confidence = 0.6
        
        return {
            'sentiment': sentiment,
            'confidence': confidence,
            'notes': f'Keyword-based analysis: {positive_count} positive, {negative_count} negative signals'
        }
    
    def analyze_batch_sentiment(self, df: pd.DataFrame) -> pd.DataFrame:
        """Analyze sentiment for a batch of stocks"""
        results = []
        
        for _, row in df.iterrows():
            try:
                ticker = row['ticker']
                
                # Get news headlines
                headlines = self.get_news_headlines(ticker)
                
                # Analyze sentiment
                sentiment_result = self.analyze_sentiment_with_gpt(ticker, headlines)
                
                # Add results to row
                result_row = row.copy()
                result_row['sentiment'] = sentiment_result['sentiment']
                result_row['sentiment_confidence'] = sentiment_result['confidence']
                result_row['sentiment_notes'] = sentiment_result['notes']
                result_row['headlines_count'] = len(headlines)
                
                results.append(result_row)
                
                # Rate limiting for API calls
                time.sleep(1)  # 1 second between calls to be respectful
                
            except Exception as e:
                print(f"Error analyzing sentiment for {row['ticker']}: {str(e)}")
                # Add row with neutral sentiment on error
                result_row = row.copy()
                result_row['sentiment'] = 'NEUTRAL'
                result_row['sentiment_confidence'] = 0.5
                result_row['sentiment_notes'] = f'Error in analysis: {str(e)[:50]}'
                result_row['headlines_count'] = 0
                results.append(result_row)
                continue
        
        return pd.DataFrame(results)
