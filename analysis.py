import pandas as pd
import numpy as np
from scipy import stats
from datetime import datetime, timedelta
import streamlit as st

class TradingAnalyzer:
    """Class to perform trading and sentiment analysis"""
    
    def __init__(self, fear_greed_data, trading_data):
        self.fear_greed_data = fear_greed_data
        self.trading_data = trading_data
        self.merged_data = None
        self.daily_data = None
        self._prepare_data()
    
    def _prepare_data(self):
        """Prepare merged and aggregated data for analysis"""
        # Merge datasets by date
        self.merged_data = self._merge_by_date()
        
        # Create daily aggregates
        self.daily_data = self._create_daily_aggregates()
    
    def _merge_by_date(self):
        """Merge fear/greed and trading data by date"""
        # Prepare fear/greed data
        fg_df = self.fear_greed_data.copy()
        fg_df['date'] = pd.to_datetime(fg_df['date']).dt.date
        
        # Prepare trading data
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
        
        # Merge
        merged = pd.merge(
            trading_df,
            fg_df[['date', 'value', 'classification']],
            on='date',
            how='left'
        )
        
        merged = merged.rename(columns={
            'value': 'sentiment_score',
            'classification': 'sentiment_category'
        })
        
        return merged
    
    def _create_daily_aggregates(self):
        """Create daily aggregated data"""
        if self.merged_data is None:
            return None
        
        daily_agg = self.merged_data.groupby('date').agg({
            'Closed PnL': ['sum', 'mean', 'count', 'std'],
            'Size USD': ['sum', 'mean'],
            'sentiment_score': 'first',
            'sentiment_category': 'first',
            'Side': lambda x: (x == 'BUY').sum(),
            'Fee': 'sum'
        }).reset_index()
        
        # Flatten column names
        daily_agg.columns = [
            'date', 'total_pnl', 'avg_pnl', 'trade_count', 'pnl_std',
            'total_volume', 'avg_volume', 'sentiment_score',
            'sentiment_category', 'buy_count', 'total_fees'
        ]
        
        # Calculate additional metrics
        daily_agg['sell_count'] = daily_agg['trade_count'] - daily_agg['buy_count']
        daily_agg['buy_ratio'] = daily_agg['buy_count'] / daily_agg['trade_count']
        daily_agg['cumulative_pnl'] = daily_agg['total_pnl'].cumsum()
        
        # Win rate calculation
        win_trades = self.merged_data.groupby('date')['Closed PnL'].apply(lambda x: (x > 0).sum())
        daily_agg['win_trades'] = win_trades.values
        daily_agg['win_rate'] = daily_agg['win_trades'] / daily_agg['trade_count'] * 100
        
        # Fill missing sentiment data with forward fill
        daily_agg['sentiment_score'] = daily_agg['sentiment_score'].ffill()
        daily_agg['sentiment_category'] = daily_agg['sentiment_category'].ffill()
        
        return daily_agg
    
    def calculate_sentiment_statistics(self):
        """Calculate sentiment distribution statistics"""
        sentiment_counts = self.fear_greed_data['classification'].value_counts()
        
        return {
            'extreme_fear_days': sentiment_counts.get('Extreme Fear', 0),
            'fear_days': sentiment_counts.get('Fear', 0),
            'neutral_days': sentiment_counts.get('Neutral', 0),
            'greed_days': sentiment_counts.get('Greed', 0),
            'extreme_greed_days': sentiment_counts.get('Extreme Greed', 0),
            'avg_score': self.fear_greed_data['value'].mean(),
            'median_score': self.fear_greed_data['value'].median(),
            'std_score': self.fear_greed_data['value'].std()
        }
    
    def calculate_trading_metrics(self):
        """Calculate comprehensive trading metrics"""
        if self.trading_data is None or len(self.trading_data) == 0:
            return {}
        
        # Basic metrics
        total_trades = len(self.trading_data)
        profitable_trades = len(self.trading_data[self.trading_data['Closed PnL'] > 0])
        win_rate = (profitable_trades / total_trades) * 100 if total_trades > 0 else 0
        
        total_pnl = self.trading_data['Closed PnL'].sum()
        avg_profit = self.trading_data['Closed PnL'].mean()
        total_volume = self.trading_data['Size USD'].sum()
        
        # Risk metrics
        daily_returns = self.daily_data['total_pnl'] if self.daily_data is not None else self.trading_data['Closed PnL']
        sharpe_ratio = self._calculate_sharpe_ratio(daily_returns)
        max_drawdown = self._calculate_max_drawdown(daily_returns.cumsum())
        
        return {
            'total_trades': total_trades,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'avg_profit': avg_profit,
            'total_volume': total_volume,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'profitable_trades': profitable_trades,
            'losing_trades': total_trades - profitable_trades
        }
    
    def calculate_sentiment_trading_correlations(self):
        """Calculate correlations between sentiment and trading metrics"""
        if self.daily_data is None:
            return {}
        
        # Remove rows with missing sentiment data
        clean_data = self.daily_data.dropna(subset=['sentiment_score'])
        
        if len(clean_data) == 0:
            return {
                'sentiment_pnl': 0,
                'sentiment_volume': 0,
                'sentiment_trades': 0,
                'sentiment_winrate': 0
            }
        
        return {
            'sentiment_pnl': clean_data['sentiment_score'].corr(clean_data['total_pnl']),
            'sentiment_volume': clean_data['sentiment_score'].corr(clean_data['total_volume']),
            'sentiment_trades': clean_data['sentiment_score'].corr(clean_data['trade_count']),
            'sentiment_winrate': clean_data['sentiment_score'].corr(clean_data['win_rate'])
        }
    
    def perform_statistical_tests(self):
        """Perform statistical tests on sentiment vs performance"""
        if self.daily_data is None:
            return {}
        
        clean_data = self.daily_data.dropna(subset=['sentiment_category', 'total_pnl'])
        
        results = {}
        sentiment_categories = clean_data['sentiment_category'].unique()
        
        for category in sentiment_categories:
            if category is not None:
                category_data = clean_data[clean_data['sentiment_category'] == category]['total_pnl']
                other_data = clean_data[clean_data['sentiment_category'] != category]['total_pnl']
                
                if len(category_data) > 1 and len(other_data) > 1:
                    t_stat, p_value = stats.ttest_ind(category_data, other_data)
                    results[category] = {
                        'mean_pnl': category_data.mean(),
                        't_statistic': t_stat,
                        'p_value': p_value,
                        'sample_size': len(category_data)
                    }
        
        return results
    
    def generate_insights(self):
        """Generate key insights from the analysis"""
        insights = []
        
        # Correlation insights
        correlations = self.calculate_sentiment_trading_correlations()
        
        if abs(correlations.get('sentiment_pnl', 0)) > 0.3:
            direction = "positive" if correlations['sentiment_pnl'] > 0 else "negative"
            insights.append(f"Strong {direction} correlation between sentiment and PnL ({correlations['sentiment_pnl']:.3f})")
        
        if abs(correlations.get('sentiment_volume', 0)) > 0.3:
            direction = "positive" if correlations['sentiment_volume'] > 0 else "negative"
            insights.append(f"Strong {direction} correlation between sentiment and trading volume ({correlations['sentiment_volume']:.3f})")
        
        # Performance by sentiment insights
        if self.daily_data is not None:
            sentiment_performance = self.daily_data.groupby('sentiment_category')['total_pnl'].mean()
            best_sentiment = sentiment_performance.idxmax() if len(sentiment_performance) > 0 else None
            worst_sentiment = sentiment_performance.idxmin() if len(sentiment_performance) > 0 else None
            
            if best_sentiment:
                insights.append(f"Best performance during {best_sentiment} periods (avg PnL: ${sentiment_performance[best_sentiment]:.2f})")
            
            if worst_sentiment and worst_sentiment != best_sentiment:
                insights.append(f"Worst performance during {worst_sentiment} periods (avg PnL: ${sentiment_performance[worst_sentiment]:.2f})")
        
        # Trading pattern insights
        trading_metrics = self.calculate_trading_metrics()
        if trading_metrics.get('win_rate', 0) > 60:
            insights.append(f"High win rate of {trading_metrics['win_rate']:.1f}% indicates strong trading strategy")
        elif trading_metrics.get('win_rate', 0) < 40:
            insights.append(f"Low win rate of {trading_metrics['win_rate']:.1f}% suggests room for strategy improvement")
        
        return insights
    
    def get_data_quality_metrics(self):
        """Get data quality metrics for both datasets"""
        fear_greed_metrics = {
            'total_records': len(self.fear_greed_data),
            'date_range': f"{self.fear_greed_data['date'].min()} to {self.fear_greed_data['date'].max()}",
            'missing_values': self.fear_greed_data.isnull().sum().sum()
        }
        
        # Use Timestamp IST column if datetime doesn't exist
        if 'datetime' in self.trading_data.columns:
            date_col = 'datetime'
        elif 'Timestamp IST' in self.trading_data.columns:
            date_col = 'Timestamp IST'
        else:
            date_col = None
            
        if date_col:
            date_range = f"{self.trading_data[date_col].min()} to {self.trading_data[date_col].max()}"
        else:
            date_range = "Date range unavailable"
            
        trading_metrics = {
            'total_records': len(self.trading_data),
            'date_range': date_range,
            'missing_values': self.trading_data.isnull().sum().sum()
        }
        
        return {
            'fear_greed': fear_greed_metrics,
            'trading': trading_metrics
        }
    
    def generate_summary_report(self):
        """Generate a comprehensive summary report"""
        trading_metrics = self.calculate_trading_metrics()
        sentiment_stats = self.calculate_sentiment_statistics()
        correlations = self.calculate_sentiment_trading_correlations()
        
        report_data = {
            'Metric': [
                'Total Trades',
                'Win Rate (%)',
                'Total PnL ($)',
                'Average Sentiment Score',
                'Sentiment-PnL Correlation',
                'Sentiment-Volume Correlation',
                'Sharpe Ratio',
                'Max Drawdown ($)'
            ],
            'Value': [
                trading_metrics.get('total_trades', 0),
                f"{trading_metrics.get('win_rate', 0):.2f}%",
                f"${trading_metrics.get('total_pnl', 0):.2f}",
                f"{sentiment_stats.get('avg_score', 0):.2f}",
                f"{correlations.get('sentiment_pnl', 0):.3f}",
                f"{correlations.get('sentiment_volume', 0):.3f}",
                f"{trading_metrics.get('sharpe_ratio', 0):.3f}",
                f"${trading_metrics.get('max_drawdown', 0):.2f}"
            ]
        }
        
        return pd.DataFrame(report_data)
    
    def get_correlation_data(self):
        """Get detailed correlation data for export"""
        if self.daily_data is None:
            return pd.DataFrame()
        
        clean_data = self.daily_data.dropna(subset=['sentiment_score'])
        
        correlation_data = clean_data[['date', 'sentiment_score', 'sentiment_category', 
                                     'total_pnl', 'total_volume', 'trade_count', 'win_rate']].copy()
        
        return correlation_data
    
    def get_detailed_metrics(self):
        """Get detailed metrics for export"""
        if self.daily_data is None:
            return pd.DataFrame()
        
        return self.daily_data.copy()
    
    def _calculate_sharpe_ratio(self, returns, risk_free_rate=0.02):
        """Calculate Sharpe ratio"""
        if len(returns) == 0 or returns.std() == 0:
            return 0
        
        excess_returns = returns - (risk_free_rate / 252)  # Daily risk-free rate
        return excess_returns.mean() / returns.std() * np.sqrt(252)  # Annualized
    
    def _calculate_max_drawdown(self, cumulative_returns):
        """Calculate maximum drawdown"""
        if len(cumulative_returns) == 0:
            return 0
        
        running_max = cumulative_returns.expanding().max()
        drawdown = cumulative_returns - running_max
        return drawdown.min()
