import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import io
import base64

from data_processor import DataProcessor
from analysis import TradingAnalyzer
from visualizations import DashboardVisualizer
from utils import export_results, calculate_metrics

# Page configuration
st.set_page_config(
    page_title="Bitcoin Sentiment & Trading Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'fear_greed_data' not in st.session_state:
    st.session_state.fear_greed_data = None
if 'trading_data' not in st.session_state:
    st.session_state.trading_data = None

def main():
    st.title("📊 Bitcoin Market Sentiment & Trader Performance Analytics")
    st.markdown("---")
    
    # Sidebar for data upload and controls
    with st.sidebar:
        st.header("📁 Data Upload")
        
        # File uploaders
        fear_greed_file = st.file_uploader(
            "Upload Fear & Greed Index CSV",
            type=['csv'],
            help="Upload the Bitcoin Fear & Greed Index dataset"
        )
        
        trading_file = st.file_uploader(
            "Upload Historical Trading Data CSV",
            type=['csv'],
            help="Upload the Hyperliquid historical trading dataset"
        )
        
        # Load default data if files not uploaded
        if st.button("Load Sample Data") or (fear_greed_file is None and trading_file is None and not st.session_state.data_loaded):
            try:
                processor = DataProcessor()
                st.session_state.fear_greed_data = processor.load_fear_greed_data('data/fear_greed_index.csv')
                st.session_state.trading_data = processor.load_trading_data('data/historical_data.csv')
                st.session_state.data_loaded = True
                st.success("Sample data loaded successfully!")
            except Exception as e:
                st.error(f"Error loading sample data: {str(e)}")
        
        # Process uploaded files
        if fear_greed_file is not None and trading_file is not None:
            try:
                processor = DataProcessor()
                
                # Load and process data
                fear_greed_df = processor.load_fear_greed_data(fear_greed_file)
                trading_df = processor.load_trading_data(trading_file)
                
                st.session_state.fear_greed_data = fear_greed_df
                st.session_state.trading_data = trading_df
                st.session_state.data_loaded = True
                
                st.success("✅ Data uploaded and processed successfully!")
                
                # Display data info
                st.markdown("### Data Overview")
                st.write(f"**Fear & Greed Index:** {len(fear_greed_df)} records")
                st.write(f"**Trading Data:** {len(trading_df)} records")
                
            except Exception as e:
                st.error(f"Error processing data: {str(e)}")
    
    # Main dashboard
    if st.session_state.data_loaded:
        display_dashboard()
    else:
        st.info("👆 Please upload your datasets or load sample data using the sidebar to begin analysis.")
        
        # Display information about expected data format
        st.markdown("### Expected Data Format")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Fear & Greed Index CSV:**")
            st.code("""
timestamp,value,classification,date
1517463000,30,Fear,2018-02-01
1517549400,15,Extreme Fear,2018-02-02
            """)
        
        with col2:
            st.markdown("**Trading Data CSV:**")
            st.code("""
Account,Coin,Execution Price,Size Tokens,Size USD,Side,Timestamp IST,Start Position,Direction,Closed PnL,Transaction Hash,Order ID,Crossed,Fee,Trade ID,Timestamp
            """)

def display_dashboard():
    """Display the main analytics dashboard"""
    
    # Initialize analyzer and visualizer
    analyzer = TradingAnalyzer(st.session_state.fear_greed_data, st.session_state.trading_data)
    visualizer = DashboardVisualizer(st.session_state.fear_greed_data, st.session_state.trading_data)
    
    # Main tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Overview", 
        "😰 Market Sentiment", 
        "💰 Trading Performance", 
        "🔗 Correlation Analysis", 
        "📊 Advanced Analytics"
    ])
    
    with tab1:
        display_overview_tab(analyzer, visualizer)
    
    with tab2:
        display_sentiment_tab(analyzer, visualizer)
    
    with tab3:
        display_trading_tab(analyzer, visualizer)
    
    with tab4:
        display_correlation_tab(analyzer, visualizer)
    
    with tab5:
        display_advanced_tab(analyzer, visualizer)

def display_overview_tab(analyzer, visualizer):
    """Display overview dashboard"""
    st.header("📈 Data Overview & Key Metrics")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_trades = len(st.session_state.trading_data)
        st.metric("Total Trades", f"{total_trades:,}")
    
    with col2:
        total_pnl = st.session_state.trading_data['Closed PnL'].sum()
        st.metric("Total PnL", f"${total_pnl:,.2f}")
    
    with col3:
        avg_sentiment = st.session_state.fear_greed_data['value'].mean()
        st.metric("Avg Sentiment Score", f"{avg_sentiment:.1f}")
    
    with col4:
        unique_traders = st.session_state.trading_data['Account'].nunique()
        st.metric("Unique Traders", f"{unique_traders:,}")
    
    st.markdown("---")
    
    # Timeline overview
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📅 Data Timeline")
        timeline_fig = visualizer.create_timeline_overview()
        st.plotly_chart(timeline_fig, use_container_width=True)
    
    with col2:
        st.subheader("💹 Trading Volume Distribution")
        volume_fig = visualizer.create_volume_distribution()
        st.plotly_chart(volume_fig, use_container_width=True)
    
    # Data quality summary
    st.subheader("🔍 Data Quality Summary")
    quality_metrics = analyzer.get_data_quality_metrics()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Fear & Greed Index Data:**")
        st.write(f"• Records: {quality_metrics['fear_greed']['total_records']:,}")
        st.write(f"• Date Range: {quality_metrics['fear_greed']['date_range']}")
        st.write(f"• Missing Values: {quality_metrics['fear_greed']['missing_values']}")
    
    with col2:
        st.markdown("**Trading Data:**")
        st.write(f"• Records: {quality_metrics['trading']['total_records']:,}")
        st.write(f"• Date Range: {quality_metrics['trading']['date_range']}")
        st.write(f"• Missing Values: {quality_metrics['trading']['missing_values']}")

def display_sentiment_tab(analyzer, visualizer):
    """Display sentiment analysis tab"""
    st.header("😰 Market Sentiment Analysis")
    
    # Sentiment distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Sentiment Distribution")
        sentiment_dist_fig = visualizer.create_sentiment_distribution()
        st.plotly_chart(sentiment_dist_fig, use_container_width=True)
    
    with col2:
        st.subheader("Sentiment Over Time")
        sentiment_time_fig = visualizer.create_sentiment_timeline()
        st.plotly_chart(sentiment_time_fig, use_container_width=True)
    
    # Sentiment statistics
    st.subheader("📊 Sentiment Statistics")
    sentiment_stats = analyzer.calculate_sentiment_statistics()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Fear Days", sentiment_stats['fear_days'])
        st.metric("Extreme Fear Days", sentiment_stats['extreme_fear_days'])
    
    with col2:
        st.metric("Neutral Days", sentiment_stats['neutral_days'])
        st.metric("Average Score", f"{sentiment_stats['avg_score']:.1f}")
    
    with col3:
        st.metric("Greed Days", sentiment_stats['greed_days'])
        st.metric("Extreme Greed Days", sentiment_stats['extreme_greed_days'])
    
    # Monthly sentiment trends
    st.subheader("📈 Monthly Sentiment Trends")
    monthly_sentiment_fig = visualizer.create_monthly_sentiment_trends()
    st.plotly_chart(monthly_sentiment_fig, use_container_width=True)

def display_trading_tab(analyzer, visualizer):
    """Display trading performance tab"""
    st.header("💰 Trading Performance Analysis")
    
    # Trading metrics
    trading_metrics = analyzer.calculate_trading_metrics()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Win Rate", f"{trading_metrics['win_rate']:.1f}%")
    
    with col2:
        st.metric("Avg Profit per Trade", f"${trading_metrics['avg_profit']:.2f}")
    
    with col3:
        st.metric("Total Volume", f"${trading_metrics['total_volume']:,.0f}")
    
    with col4:
        st.metric("Sharpe Ratio", f"{trading_metrics['sharpe_ratio']:.2f}")
    
    st.markdown("---")
    
    # PnL distribution and trends
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("PnL Distribution")
        pnl_dist_fig = visualizer.create_pnl_distribution()
        st.plotly_chart(pnl_dist_fig, use_container_width=True)
    
    with col2:
        st.subheader("Cumulative PnL Over Time")
        cumulative_pnl_fig = visualizer.create_cumulative_pnl()
        st.plotly_chart(cumulative_pnl_fig, use_container_width=True)
    
    # Trading patterns
    st.subheader("📊 Trading Patterns")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Trading Volume by Hour")
        hourly_volume_fig = visualizer.create_hourly_trading_volume()
        st.plotly_chart(hourly_volume_fig, use_container_width=True)
    
    with col2:
        st.subheader("Buy vs Sell Distribution")
        buy_sell_fig = visualizer.create_buy_sell_distribution()
        st.plotly_chart(buy_sell_fig, use_container_width=True)

def display_correlation_tab(analyzer, visualizer):
    """Display correlation analysis tab"""
    st.header("🔗 Correlation Analysis")
    
    # Calculate correlations
    correlations = analyzer.calculate_sentiment_trading_correlations()
    
    # Main correlation metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Sentiment vs PnL Correlation", 
            f"{correlations['sentiment_pnl']:.3f}",
            help="Correlation between market sentiment and trading PnL"
        )
    
    with col2:
        st.metric(
            "Sentiment vs Volume Correlation", 
            f"{correlations['sentiment_volume']:.3f}",
            help="Correlation between market sentiment and trading volume"
        )
    
    with col3:
        st.metric(
            "Sentiment vs Trade Count Correlation", 
            f"{correlations['sentiment_trades']:.3f}",
            help="Correlation between market sentiment and number of trades"
        )
    
    st.markdown("---")
    
    # Correlation heatmap
    st.subheader("📊 Correlation Matrix")
    correlation_matrix_fig = visualizer.create_correlation_heatmap()
    st.plotly_chart(correlation_matrix_fig, use_container_width=True)
    
    # Sentiment vs Performance scatter
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Sentiment vs Daily PnL")
        sentiment_pnl_fig = visualizer.create_sentiment_vs_pnl_scatter()
        st.plotly_chart(sentiment_pnl_fig, use_container_width=True)
    
    with col2:
        st.subheader("Sentiment vs Trading Volume")
        sentiment_volume_fig = visualizer.create_sentiment_vs_volume_scatter()
        st.plotly_chart(sentiment_volume_fig, use_container_width=True)
    
    # Performance by sentiment category
    st.subheader("📈 Performance by Sentiment Category")
    performance_by_sentiment_fig = visualizer.create_performance_by_sentiment()
    st.plotly_chart(performance_by_sentiment_fig, use_container_width=True)

def display_advanced_tab(analyzer, visualizer):
    """Display advanced analytics tab"""
    st.header("📊 Advanced Analytics & Insights")
    
    # Statistical analysis
    st.subheader("📈 Statistical Analysis")
    
    # T-test results
    ttest_results = analyzer.perform_statistical_tests()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Performance Comparison by Sentiment:**")
        for sentiment, result in ttest_results.items():
            if result['p_value'] < 0.05:
                significance = "Significant ✅"
            else:
                significance = "Not Significant ❌"
            
            st.write(f"• {sentiment}: p-value = {result['p_value']:.4f} ({significance})")
    
    with col2:
        st.markdown("**Key Statistical Insights:**")
        insights = analyzer.generate_insights()
        for insight in insights:
            st.write(f"• {insight}")
    
    # Time series analysis
    st.subheader("⏰ Time Series Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Rolling Correlation (30-day)")
        rolling_corr_fig = visualizer.create_rolling_correlation()
        st.plotly_chart(rolling_corr_fig, use_container_width=True)
    
    with col2:
        st.subheader("Volatility Analysis")
        volatility_fig = visualizer.create_volatility_analysis()
        st.plotly_chart(volatility_fig, use_container_width=True)
    
    # Regime analysis
    st.subheader("🔄 Market Regime Analysis")
    regime_analysis_fig = visualizer.create_regime_analysis()
    st.plotly_chart(regime_analysis_fig, use_container_width=True)
    
    # Export functionality
    st.subheader("📥 Export Analysis Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Export Summary Report"):
            report = analyzer.generate_summary_report()
            st.download_button(
                label="Download Report (CSV)",
                data=report.to_csv(index=False),
                file_name=f"trading_sentiment_analysis_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("Export Correlation Data"):
            corr_data = analyzer.get_correlation_data()
            st.download_button(
                label="Download Correlations (CSV)",
                data=corr_data.to_csv(index=False),
                file_name=f"sentiment_correlations_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    with col3:
        if st.button("Export Trading Metrics"):
            metrics_data = analyzer.get_detailed_metrics()
            st.download_button(
                label="Download Metrics (CSV)",
                data=metrics_data.to_csv(index=False),
                file_name=f"trading_metrics_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    main()
