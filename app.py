import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
from data_processor import DataProcessor
from sentiment_analyzer import SentimentAnalyzer
from utils import format_currency, format_percentage, get_color_for_sentiment
import io

# Page configuration
st.set_page_config(
    page_title="LEAP Options Screener",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'screener_data' not in st.session_state:
    st.session_state.screener_data = None

# Title and description
st.title("📈 LEAP Options Screener")
st.markdown("""
**High-IV LEAP Screener with Sentiment Overlay**

This tool identifies undervalued S&P 500 and NASDAQ stocks with high Implied Volatility (IV), 
positive sentiment, and strong upside potential for LEAP options.
""")

# Sidebar configuration
st.sidebar.header("⚙️ Configuration")

# Market selection
market_selection = st.sidebar.selectbox(
    "Select Market Index",
    ["S&P 500", "NASDAQ-100", "Both"],
    index=0
)

# Fundamental filters
st.sidebar.subheader("📊 Fundamental Filters")
min_drop_from_ath = st.sidebar.slider(
    "Minimum Drop from ATH (%)",
    min_value=10,
    max_value=80,
    value=40,
    step=5
)

min_market_cap = st.sidebar.number_input(
    "Minimum Market Cap ($B)",
    min_value=1,
    max_value=500,
    value=50,
    step=5
)

# Volatility filters
st.sidebar.subheader("📈 Volatility Filters")
min_iv_hv_ratio = st.sidebar.slider(
    "Minimum IV/HV Ratio",
    min_value=1.0,
    max_value=3.0,
    value=1.25,
    step=0.05
)

# Sentiment filter
st.sidebar.subheader("🎯 Sentiment Filter")
sentiment_filter = st.sidebar.multiselect(
    "Include Sentiment Types",
    ["BULLISH", "NEUTRAL", "BEARISH"],
    default=["BULLISH", "NEUTRAL"]
)

# Earnings filter
include_earnings = st.sidebar.checkbox(
    "Include stocks with upcoming earnings (30 days)",
    value=True
)

# Main content area
col1, col2 = st.columns([3, 1])

with col2:
    if st.button("🔄 Run Screener", type="primary", use_container_width=True):
        with st.spinner("Running screener analysis..."):
            try:
                # Initialize processors
                data_processor = DataProcessor()
                sentiment_analyzer = SentimentAnalyzer()
                
                # Progress tracking
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Step 1: Load tickers
                status_text.text("Loading ticker universe...")
                tickers = data_processor.get_ticker_universe(market_selection)
                progress_bar.progress(10)
                
                # Step 2: Filter by fundamentals
                status_text.text("Filtering by fundamentals...")
                fundamental_data = data_processor.filter_by_fundamentals(
                    tickers, min_drop_from_ath, min_market_cap * 1e9
                )
                progress_bar.progress(30)
                
                # Step 3: Calculate volatility
                status_text.text("Calculating volatility metrics...")
                volatility_data = data_processor.calculate_volatility_metrics(
                    fundamental_data, min_iv_hv_ratio
                )
                progress_bar.progress(50)
                
                # Step 4: Check earnings
                status_text.text("Checking earnings calendar...")
                earnings_data = data_processor.check_earnings_calendar(volatility_data)
                progress_bar.progress(70)
                
                # Step 5: Sentiment analysis
                status_text.text("Analyzing sentiment...")
                final_data = sentiment_analyzer.analyze_batch_sentiment(earnings_data)
                progress_bar.progress(90)
                
                # Step 6: Apply final filters
                status_text.text("Applying filters...")
                filtered_data = final_data[
                    (final_data['sentiment'].isin(sentiment_filter)) &
                    (final_data['has_earnings'] == include_earnings if not include_earnings else True)
                ]
                
                progress_bar.progress(100)
                status_text.text("Analysis complete!")
                
                st.session_state.screener_data = filtered_data
                st.session_state.data_loaded = True
                
                time.sleep(1)  # Brief pause to show completion
                progress_bar.empty()
                status_text.empty()
                
            except Exception as e:
                st.error(f"Error running screener: {str(e)}")
                st.session_state.data_loaded = False

with col1:
    if st.session_state.data_loaded and st.session_state.screener_data is not None:
        data = st.session_state.screener_data
        
        if len(data) > 0:
            st.subheader(f"📋 Screener Results ({len(data)} stocks found)")
            
            # Summary metrics
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            
            with col_m1:
                avg_drop = data['drop_from_ath_pct'].mean()
                st.metric("Avg Drop from ATH", format_percentage(avg_drop))
                
            with col_m2:
                avg_iv_hv = data['iv_hv_ratio'].mean()
                st.metric("Avg IV/HV Ratio", f"{avg_iv_hv:.2f}")
                
            with col_m3:
                bullish_count = len(data[data['sentiment'] == 'BULLISH'])
                st.metric("Bullish Stocks", f"{bullish_count}")
                
            with col_m4:
                earnings_count = len(data[data['has_earnings'] == True])
                st.metric("With Earnings", f"{earnings_count}")
            
            # Results table
            st.subheader("📊 Filtered Results")
            
            # Format data for display
            display_data = data.copy()
            display_data['Market Cap'] = display_data['market_cap'].apply(format_currency)
            display_data['Drop from ATH'] = display_data['drop_from_ath_pct'].apply(format_percentage)
            display_data['IV'] = display_data['implied_volatility'].apply(lambda x: f"{x:.1f}%")
            display_data['HV'] = display_data['historical_volatility'].apply(lambda x: f"{x:.1f}%")
            display_data['IV/HV Ratio'] = display_data['iv_hv_ratio'].apply(lambda x: f"{x:.2f}")
            display_data['Sentiment'] = display_data['sentiment']
            display_data['Earnings Date'] = display_data['earnings_date']
            display_data['Notes'] = display_data['sentiment_notes']
            
            # Select columns for display
            columns_to_show = [
                'ticker', 'Market Cap', 'Drop from ATH', 'IV', 'HV', 
                'IV/HV Ratio', 'Earnings Date', 'Sentiment', 'Notes'
            ]
            
            # Create styled dataframe
            styled_data = display_data[columns_to_show].copy()
            styled_data.columns = [
                'Ticker', 'Market Cap', 'Drop from ATH', 'IV', 'HV',
                'IV/HV Ratio', 'Earnings Date', 'Sentiment', 'Notes'
            ]
            
            # Display interactive table
            st.dataframe(
                styled_data,
                use_container_width=True,
                height=400,
                column_config={
                    "Sentiment": st.column_config.TextColumn(
                        "Sentiment",
                        help="AI-powered sentiment analysis"
                    ),
                    "Notes": st.column_config.TextColumn(
                        "Notes",
                        help="Sentiment analysis justification",
                        width="large"
                    )
                }
            )
            
            # Export functionality
            st.subheader("📤 Export Results")
            
            col_e1, col_e2 = st.columns(2)
            
            with col_e1:
                # CSV export
                csv_data = data.to_csv(index=False)
                st.download_button(
                    label="📄 Download CSV",
                    data=csv_data,
                    file_name=f"leap_screener_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col_e2:
                # Summary export
                summary_data = {
                    'Total Stocks': len(data),
                    'Average Drop from ATH': f"{data['drop_from_ath_pct'].mean():.1f}%",
                    'Average IV/HV Ratio': f"{data['iv_hv_ratio'].mean():.2f}",
                    'Bullish Sentiment': len(data[data['sentiment'] == 'BULLISH']),
                    'Neutral Sentiment': len(data[data['sentiment'] == 'NEUTRAL']),
                    'Bearish Sentiment': len(data[data['sentiment'] == 'BEARISH']),
                    'With Upcoming Earnings': len(data[data['has_earnings'] == True])
                }
                
                summary_text = "\n".join([f"{k}: {v}" for k, v in summary_data.items()])
                st.download_button(
                    label="📊 Download Summary",
                    data=summary_text,
                    file_name=f"leap_screener_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
        else:
            st.warning("🔍 No stocks found matching the current criteria. Try adjusting your filters.")
    else:
        st.info("👆 Click 'Run Screener' to begin the analysis")

# Footer
st.markdown("---")
st.markdown("""
**⚠️ Disclaimer:** This tool is for educational and research purposes only. 
Past performance does not guarantee future results. Please conduct your own research 
and consult with a qualified financial advisor before making investment decisions.
""")
