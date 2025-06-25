import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime

class DashboardVisualizer:
    """Class to create all dashboard visualizations"""
    
    def __init__(self, fear_greed_data, trading_data):
        self.fear_greed_data = fear_greed_data
        self.trading_data = trading_data
        self.color_scheme = {
            'Extreme Fear': '#FF4444',
            'Fear': '#FF8888',
            'Neutral': '#FFAA00',
            'Greed': '#88DD88',
            'Extreme Greed': '#44AA44'
        }
    
    def create_timeline_overview(self):
        """Create timeline overview chart"""
        fig = go.Figure()
        
        # Add fear/greed timeline
        fig.add_trace(go.Scatter(
            x=self.fear_greed_data['date'],
            y=self.fear_greed_data['value'],
            mode='lines',
            name='Fear & Greed Index',
            line=dict(color='blue', width=2),
            hovertemplate='Date: %{x}<br>Score: %{y}<extra></extra>'
        ))
        
        fig.update_layout(
            title='Fear & Greed Index Timeline',
            xaxis_title='Date',
            yaxis_title='Score (0-100)',
            height=400,
            showlegend=True
        )
        
        return fig
    
    def create_volume_distribution(self):
        """Create trading volume distribution"""
        fig = px.histogram(
            self.trading_data,
            x='Size USD',
            nbins=50,
            title='Trading Volume Distribution',
            labels={'Size USD': 'Trade Size (USD)', 'count': 'Frequency'}
        )
        
        fig.update_layout(height=400)
        return fig
    
    def create_sentiment_distribution(self):
        """Create sentiment distribution pie chart"""
        sentiment_counts = self.fear_greed_data['classification'].value_counts()
        
        fig = px.pie(
            values=sentiment_counts.values,
            names=sentiment_counts.index,
            title='Market Sentiment Distribution',
            color=sentiment_counts.index,
            color_discrete_map=self.color_scheme
        )
        
        fig.update_layout(height=400)
        return fig
    
    def create_sentiment_timeline(self):
        """Create sentiment timeline with color coding"""
        fig = go.Figure()
        
        for sentiment in self.fear_greed_data['classification'].unique():
            if pd.notna(sentiment):
                sentiment_data = self.fear_greed_data[self.fear_greed_data['classification'] == sentiment]
                
                fig.add_trace(go.Scatter(
                    x=sentiment_data['date'],
                    y=sentiment_data['value'],
                    mode='markers',
                    name=sentiment,
                    marker=dict(
                        color=self.color_scheme.get(sentiment, 'gray'),
                        size=6
                    ),
                    hovertemplate=f'{sentiment}<br>Date: %{{x}}<br>Score: %{{y}}<extra></extra>'
                ))
        
        fig.update_layout(
            title='Sentiment Timeline by Category',
            xaxis_title='Date',
            yaxis_title='Fear & Greed Score',
            height=400
        )
        
        return fig
    
    def create_monthly_sentiment_trends(self):
        """Create monthly sentiment trends"""
        monthly_data = self.fear_greed_data.copy()
        monthly_data['month'] = pd.to_datetime(monthly_data['date']).dt.to_period('M')
        monthly_avg = monthly_data.groupby('month')['value'].mean().reset_index()
        monthly_avg['month'] = monthly_avg['month'].astype(str)
        
        fig = px.line(
            monthly_avg,
            x='month',
            y='value',
            title='Monthly Average Sentiment Trends',
            labels={'month': 'Month', 'value': 'Average Score'}
        )
        
        fig.update_layout(height=400, xaxis_tickangle=45)
        
        return fig
    
    def create_pnl_distribution(self):
        """Create PnL distribution histogram"""
        fig = px.histogram(
            self.trading_data,
            x='Closed PnL',
            nbins=50,
            title='PnL Distribution',
            labels={'Closed PnL': 'Profit/Loss (USD)', 'count': 'Frequency'}
        )
        
        # Add vertical line at zero
        fig.add_vline(x=0, line_dash="dash", line_color="red")
        
        fig.update_layout(height=400)
        return fig
    
    def create_cumulative_pnl(self):
        """Create cumulative PnL chart"""
        # Use appropriate datetime column
        if 'datetime' in self.trading_data.columns:
            sort_col = 'datetime'
        elif 'Timestamp IST' in self.trading_data.columns:
            sort_col = 'Timestamp IST'
        else:
            # Use index if no datetime column
            trading_sorted = self.trading_data.copy()
            trading_sorted['cumulative_pnl'] = trading_sorted['Closed PnL'].cumsum()
            fig = px.line(
                trading_sorted,
                y='cumulative_pnl',
                title='Cumulative PnL Over Time',
                labels={'index': 'Trade Number', 'cumulative_pnl': 'Cumulative PnL (USD)'}
            )
            fig.update_layout(height=400)
            return fig
            
        trading_sorted = self.trading_data.sort_values(sort_col)
        trading_sorted['cumulative_pnl'] = trading_sorted['Closed PnL'].cumsum()
        
        fig = px.line(
            trading_sorted,
            x=sort_col,
            y='cumulative_pnl',
            title='Cumulative PnL Over Time',
            labels={sort_col: 'Date/Time', 'cumulative_pnl': 'Cumulative PnL (USD)'}
        )
        
        fig.update_layout(height=400)
        return fig
    
    def create_hourly_trading_volume(self):
        """Create hourly trading volume chart"""
        hourly_data = self.trading_data.copy()
        
        # Handle different datetime column formats
        if 'datetime' in hourly_data.columns:
            hourly_data['hour'] = hourly_data['datetime'].dt.hour
        elif 'Timestamp IST' in hourly_data.columns:
            hourly_data['datetime'] = pd.to_datetime(hourly_data['Timestamp IST'], format='%d-%m-%Y %H:%M', errors='coerce')
            hourly_data['hour'] = hourly_data['datetime'].dt.hour
        else:
            # Create a simple distribution by order if no time data
            hourly_data['hour'] = (hourly_data.index % 24)
            
        hourly_volume = hourly_data.groupby('hour')['Size USD'].sum().reset_index()
        
        fig = px.bar(
            hourly_volume,
            x='hour',
            y='Size USD',
            title='Trading Volume by Hour',
            labels={'hour': 'Hour of Day', 'Size USD': 'Total Volume (USD)'}
        )
        
        fig.update_layout(height=400)
        return fig
    
    def create_buy_sell_distribution(self):
        """Create buy vs sell distribution"""
        side_counts = self.trading_data['Side'].value_counts()
        
        fig = px.pie(
            values=side_counts.values,
            names=side_counts.index,
            title='Buy vs Sell Distribution',
            color=side_counts.index,
            color_discrete_map={'BUY': '#44AA44', 'SELL': '#FF4444'}
        )
        
        fig.update_layout(height=400)
        return fig
    
    def create_correlation_heatmap(self):
        """Create correlation heatmap"""
        # Prepare daily aggregated data
        daily_data = self._prepare_daily_correlation_data()
        
        if daily_data is None or len(daily_data) == 0:
            # Return empty figure
            fig = go.Figure()
            fig.add_annotation(
                text="Insufficient data for correlation analysis",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font_size=16
            )
            fig.update_layout(height=400, title="Correlation Matrix")
            return fig
        
        # Calculate correlation matrix
        correlation_cols = ['sentiment_score', 'total_pnl', 'total_volume', 'trade_count', 'win_rate']
        available_cols = [col for col in correlation_cols if col in daily_data.columns]
        
        if len(available_cols) < 2:
            fig = go.Figure()
            fig.add_annotation(
                text="Insufficient columns for correlation analysis",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font_size=16
            )
            fig.update_layout(height=400, title="Correlation Matrix")
            return fig
        
        corr_matrix = daily_data[available_cols].corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=corr_matrix.round(3).values,
            texttemplate="%{text}",
            textfont={"size": 10},
            hoverongaps=False
        ))
        
        fig.update_layout(
            title='Correlation Matrix',
            height=500,
            xaxis_title='Variables',
            yaxis_title='Variables'
        )
        
        return fig
    
    def create_sentiment_vs_pnl_scatter(self):
        """Create sentiment vs PnL scatter plot"""
        daily_data = self._prepare_daily_correlation_data()
        
        if daily_data is None or len(daily_data) == 0:
            fig = go.Figure()
            fig.add_annotation(
                text="Insufficient data for scatter plot",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font_size=16
            )
            fig.update_layout(height=400, title="Sentiment vs PnL")
            return fig
        
        fig = px.scatter(
            daily_data,
            x='sentiment_score',
            y='total_pnl',
            color='sentiment_category',
            title='Daily PnL vs Sentiment Score',
            labels={'sentiment_score': 'Sentiment Score', 'total_pnl': 'Daily PnL (USD)'},
            color_discrete_map=self.color_scheme
        )
        
        # Add trend line
        if len(daily_data) > 1:
            fig.add_trace(go.Scatter(
                x=daily_data['sentiment_score'],
                y=np.poly1d(np.polyfit(daily_data['sentiment_score'], daily_data['total_pnl'], 1))(daily_data['sentiment_score']),
                mode='lines',
                name='Trend Line',
                line=dict(color='black', dash='dash')
            ))
        
        fig.update_layout(height=400)
        return fig
    
    def create_sentiment_vs_volume_scatter(self):
        """Create sentiment vs volume scatter plot"""
        daily_data = self._prepare_daily_correlation_data()
        
        if daily_data is None or len(daily_data) == 0:
            fig = go.Figure()
            fig.add_annotation(
                text="Insufficient data for scatter plot",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font_size=16
            )
            fig.update_layout(height=400, title="Sentiment vs Volume")
            return fig
        
        fig = px.scatter(
            daily_data,
            x='sentiment_score',
            y='total_volume',
            color='sentiment_category',
            title='Daily Volume vs Sentiment Score',
            labels={'sentiment_score': 'Sentiment Score', 'total_volume': 'Daily Volume (USD)'},
            color_discrete_map=self.color_scheme
        )
        
        fig.update_layout(height=400)
        return fig
    
    def create_performance_by_sentiment(self):
        """Create performance comparison by sentiment category"""
        daily_data = self._prepare_daily_correlation_data()
        
        if daily_data is None or len(daily_data) == 0:
            fig = go.Figure()
            fig.add_annotation(
                text="Insufficient data for performance analysis",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font_size=16
            )
            fig.update_layout(height=400, title="Performance by Sentiment")
            return fig
        
        sentiment_performance = daily_data.groupby('sentiment_category').agg({
            'total_pnl': ['mean', 'std', 'count'],
            'win_rate': 'mean',
            'total_volume': 'mean'
        }).reset_index()
        
        # Flatten column names
        sentiment_performance.columns = [
            'sentiment_category', 'avg_pnl', 'pnl_std', 'days_count', 'avg_win_rate', 'avg_volume'
        ]
        
        fig = px.bar(
            sentiment_performance,
            x='sentiment_category',
            y='avg_pnl',
            color='sentiment_category',
            title='Average Daily PnL by Sentiment Category',
            labels={'sentiment_category': 'Sentiment Category', 'avg_pnl': 'Average Daily PnL (USD)'},
            color_discrete_map=self.color_scheme,
            error_y='pnl_std'
        )
        
        fig.update_layout(height=400)
        return fig
    
    def create_rolling_correlation(self):
        """Create rolling correlation chart"""
        daily_data = self._prepare_daily_correlation_data()
        
        if daily_data is None or len(daily_data) < 30:
            fig = go.Figure()
            fig.add_annotation(
                text="Insufficient data for rolling correlation (need 30+ days)",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font_size=16
            )
            fig.update_layout(height=400, title="30-Day Rolling Correlation")
            return fig
        
        daily_data = daily_data.sort_values('date')
        rolling_corr = daily_data['sentiment_score'].rolling(window=30).corr(daily_data['total_pnl'])
        
        fig = px.line(
            x=daily_data['date'],
            y=rolling_corr,
            title='30-Day Rolling Correlation: Sentiment vs PnL',
            labels={'x': 'Date', 'y': 'Correlation Coefficient'}
        )
        
        # Add horizontal line at zero
        fig.add_hline(y=0, line_dash="dash", line_color="gray")
        
        fig.update_layout(height=400)
        return fig
    
    def create_volatility_analysis(self):
        """Create volatility analysis chart"""
        daily_data = self._prepare_daily_correlation_data()
        
        if daily_data is None or len(daily_data) < 10:
            fig = go.Figure()
            fig.add_annotation(
                text="Insufficient data for volatility analysis",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font_size=16
            )
            fig.update_layout(height=400, title="PnL Volatility Analysis")
            return fig
        
        daily_data = daily_data.sort_values('date')
        rolling_std = daily_data['total_pnl'].rolling(window=7).std()
        
        fig = px.line(
            x=daily_data['date'],
            y=rolling_std,
            title='7-Day Rolling PnL Volatility',
            labels={'x': 'Date', 'y': 'PnL Standard Deviation'}
        )
        
        fig.update_layout(height=400)
        return fig
    
    def create_regime_analysis(self):
        """Create market regime analysis"""
        daily_data = self._prepare_daily_correlation_data()
        
        if daily_data is None or len(daily_data) == 0:
            fig = go.Figure()
            fig.add_annotation(
                text="Insufficient data for regime analysis",
                xref="paper", yref="paper",
                x=0.5, y=0.5, xanchor='center', yanchor='middle',
                showarrow=False, font_size=16
            )
            fig.update_layout(height=400, title="Market Regime Analysis")
            return fig
        
        # Create subplot with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Add sentiment score
        fig.add_trace(
            go.Scatter(
                x=daily_data['date'],
                y=daily_data['sentiment_score'],
                name='Sentiment Score',
                line=dict(color='blue')
            ),
            secondary_y=False,
        )
        
        # Add cumulative PnL
        daily_data = daily_data.sort_values('date')
        cumulative_pnl = daily_data['total_pnl'].cumsum()
        
        fig.add_trace(
            go.Scatter(
                x=daily_data['date'],
                y=cumulative_pnl,
                name='Cumulative PnL',
                line=dict(color='green')
            ),
            secondary_y=True,
        )
        
        # Set y-axes titles
        fig.update_yaxes(title_text="Sentiment Score", secondary_y=False)
        fig.update_yaxes(title_text="Cumulative PnL (USD)", secondary_y=True)
        
        fig.update_layout(
            title='Market Sentiment vs Trading Performance Over Time',
            height=400,
            xaxis_title='Date'
        )
        
        return fig
    
    def _prepare_daily_correlation_data(self):
        """Prepare daily aggregated data for correlation analysis"""
        # Merge fear/greed and trading data by date
        fg_df = self.fear_greed_data.copy()
        fg_df['date'] = pd.to_datetime(fg_df['date']).dt.date
        
        trading_df = self.trading_data.copy()
        if 'date' not in trading_df.columns:
            # Create datetime column if it doesn't exist
            if 'Timestamp IST' in trading_df.columns:
                trading_df['datetime'] = pd.to_datetime(trading_df['Timestamp IST'], format='%d-%m-%Y %H:%M', errors='coerce')
            elif 'Timestamp' in trading_df.columns:
                trading_df['datetime'] = pd.to_datetime(trading_df['Timestamp'], unit='s', errors='coerce')
            else:
                # Use a default date if no timestamp available
                trading_df['datetime'] = pd.to_datetime('2024-12-02')
            
            trading_df['date'] = trading_df['datetime'].dt.date
        
        # Create daily aggregates from trading data
        daily_trading = trading_df.groupby('date').agg({
            'Closed PnL': ['sum', 'mean', 'count'],
            'Size USD': 'sum',
            'Side': lambda x: (x == 'BUY').sum(),
        }).reset_index()
        
        # Flatten column names
        daily_trading.columns = ['date', 'total_pnl', 'avg_pnl', 'trade_count', 'total_volume', 'buy_count']
        
        # Calculate additional metrics
        daily_trading['win_count'] = trading_df.groupby('date')['Closed PnL'].apply(lambda x: (x > 0).sum()).values
        daily_trading['win_rate'] = daily_trading['win_count'] / daily_trading['trade_count'] * 100
        
        # Merge with sentiment data
        merged_data = pd.merge(
            daily_trading,
            fg_df[['date', 'value', 'classification']],
            on='date',
            how='inner'
        )
        
        merged_data = merged_data.rename(columns={
            'value': 'sentiment_score',
            'classification': 'sentiment_category'
        })
        
        return merged_data.dropna()
