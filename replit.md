# LEAP Options Screener

## Overview

This is a comprehensive financial analysis tool built with Streamlit that screens for Long-term Equity Anticipation Securities (LEAP) options opportunities. The application identifies undervalued S&P 500 and NASDAQ-100 stocks by analyzing fundamental metrics, implied volatility, and sentiment data. It combines quantitative financial analysis with sentiment analysis from news sources to provide actionable investment insights for options traders.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit for web interface
- **User Interface**: Single-page application with sidebar configuration and main dashboard
- **Visualization**: Built-in Streamlit components for data tables, metrics, and filters
- **State Management**: Session state for data persistence across user interactions

### Backend Architecture
- **Core Processing**: Modular Python architecture with specialized classes:
  - `DataProcessor`: Handles market data retrieval and fundamental analysis
  - `SentimentAnalyzer`: Processes news sentiment using AI analysis
  - `utils`: Utility functions for data formatting and calculations
- **Data Flow**: Real-time data fetching → filtering → sentiment analysis → presentation
- **Error Handling**: Graceful degradation with fallback values and timeout management

### Data Processing Pipeline
- **Market Data Source**: Yahoo Finance API (yfinance) for historical prices, fundamental data
- **Sentiment Analysis**: News API for headlines + OpenAI GPT for sentiment classification
- **Stock Universe**: Predefined ticker lists for S&P 500 and NASDAQ-100 indices
- **Filtering Logic**: Multi-criteria screening based on price drops, market cap, and volatility metrics

### Key Features
- **Fundamental Screening**: Filters stocks based on drop from all-time high and market capitalization
- **Volatility Analysis**: Calculates historical volatility for options strategy identification
- **Sentiment Overlay**: AI-powered news sentiment analysis for additional confirmation
- **Multi-Market Support**: Coverage of S&P 500, NASDAQ-100, or combined universe
- **Real-time Processing**: On-demand data fetching and analysis

## External Dependencies

### Financial Data APIs
- **Yahoo Finance (yfinance)**: Primary source for stock prices, historical data, and company fundamentals
- **News API**: Retrieval of recent news headlines for sentiment analysis

### AI/ML Services
- **OpenAI API**: GPT model integration for natural language processing of news sentiment
- **Custom sentiment classification**: Converts news headlines into BULLISH/NEUTRAL/BEARISH signals

### Python Libraries
- **Streamlit**: Web application framework and UI components
- **pandas/numpy**: Data manipulation and numerical computations
- **requests**: HTTP client for API interactions
- **datetime**: Time-based calculations and date filtering

### Data Sources
- **Static ticker lists**: Hardcoded S&P 500 and NASDAQ-100 symbols for universe definition
- **Real-time market data**: Live price and volume information via Yahoo Finance
- **News aggregation**: Multi-source news headlines filtered by relevancy and recency

### Configuration Requirements
- **Environment variables**: API keys for News API and OpenAI services
- **Demo mode support**: Fallback functionality when API keys are not configured
- **Timeout handling**: Robust error management for external service dependencies