import pandas as pd
import numpy as np
from datetime import datetime
import streamlit as st

class DataProcessor:
    """Class to handle data loading and preprocessing"""
    
    def __init__(self):
        self.fear_greed_data = None
        self.trading_data = None
    
    def load_fear_greed_data(self, file_source):
        """Load and preprocess Fear & Greed Index data"""
        try:
            if isinstance(file_source, str):
                # File path
                df = pd.read_csv(file_source)
            else:
                # Uploaded file
                df = pd.read_csv(file_source)
            
            # Clean and preprocess
            df = self._clean_fear_greed_data(df)
            self.fear_greed_data = df
            
            return df
            
        except Exception as e:
            raise Exception(f"Error loading Fear & Greed data: {str(e)}")
    
    def load_trading_data(self, file_source):
        """Load and preprocess trading data"""
        try:
            if isinstance(file_source, str):
                # File path
                df = pd.read_csv(file_source)
            else:
                # Uploaded file
                df = pd.read_csv(file_source)
            
            # Clean and preprocess
            df = self._clean_trading_data(df)
            self.trading_data = df
            
            return df
            
        except Exception as e:
            raise Exception(f"Error loading trading data: {str(e)}")
    
    def _clean_fear_greed_data(self, df):
        """Clean Fear & Greed Index data"""
        # Convert timestamp to datetime
        if 'timestamp' in df.columns:
            df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
        
        # Ensure date column is datetime
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        
        # Ensure value is numeric
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        
        # Remove any rows with missing values
        df = df.dropna()
        
        # Sort by date
        df = df.sort_values('date').reset_index(drop=True)
        
        return df
    
    def _clean_trading_data(self, df):
        """Clean trading data"""
        # Convert timestamp columns
        if 'Timestamp IST' in df.columns:
            df['datetime'] = pd.to_datetime(df['Timestamp IST'], format='%d-%m-%Y %H:%M', errors='coerce')
        elif 'Timestamp' in df.columns:
            df['datetime'] = pd.to_datetime(df['Timestamp'], unit='s', errors='coerce')
        else:
            # If no datetime column exists, create a placeholder
            df['datetime'] = pd.to_datetime('2024-12-02')
        
        # Convert numeric columns
        numeric_columns = ['Execution Price', 'Size Tokens', 'Size USD', 'Closed PnL', 'Fee']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Remove rows with missing critical data (but allow missing datetime for now)
        df = df.dropna(subset=['Side'])
        
        # Sort by datetime
        df = df.sort_values('datetime').reset_index(drop=True)
        
        # Extract date for merging
        df['date'] = df['datetime'].dt.date
        
        return df
    
    def merge_datasets(self):
        """Merge fear/greed data with trading data by date"""
        if self.fear_greed_data is None or self.trading_data is None:
            raise Exception("Both datasets must be loaded before merging")
        
        # Prepare fear/greed data for merging
        fg_daily = self.fear_greed_data.copy()
        fg_daily['date'] = pd.to_datetime(fg_daily['date']).dt.date
        
        # Prepare trading data for merging
        trading_daily = self.trading_data.copy()
        trading_daily['date'] = pd.to_datetime(trading_daily['date'])
        
        # Merge datasets
        merged_df = pd.merge(
            trading_daily,
            fg_daily[['date', 'value', 'classification']],
            on='date',
            how='left'
        )
        
        # Rename columns for clarity
        merged_df = merged_df.rename(columns={
            'value': 'sentiment_score',
            'classification': 'sentiment_category'
        })
        
        return merged_df
    
    def get_daily_aggregates(self, merged_df):
        """Create daily aggregates for analysis"""
        daily_agg = merged_df.groupby('date').agg({
            'Closed PnL': ['sum', 'mean', 'count'],
            'Size USD': ['sum', 'mean'],
            'sentiment_score': 'first',
            'sentiment_category': 'first',
            'Side': lambda x: (x == 'BUY').sum(),
            'Fee': 'sum'
        }).reset_index()
        
        # Flatten column names
        daily_agg.columns = [
            'date', 'total_pnl', 'avg_pnl', 'trade_count',
            'total_volume', 'avg_volume', 'sentiment_score',
            'sentiment_category', 'buy_count', 'total_fees'
        ]
        
        # Calculate additional metrics
        daily_agg['sell_count'] = daily_agg['trade_count'] - daily_agg['buy_count']
        daily_agg['buy_ratio'] = daily_agg['buy_count'] / daily_agg['trade_count']
        daily_agg['win_trades'] = merged_df.groupby('date')['Closed PnL'].apply(lambda x: (x > 0).sum()).values
        daily_agg['win_rate'] = daily_agg['win_trades'] / daily_agg['trade_count'] * 100
        
        return daily_agg
    
    def validate_data(self):
        """Validate loaded data"""
        issues = []
        
        if self.fear_greed_data is not None:
            # Check for required columns
            required_fg_cols = ['date', 'value', 'classification']
            missing_cols = [col for col in required_fg_cols if col not in self.fear_greed_data.columns]
            if missing_cols:
                issues.append(f"Fear/Greed data missing columns: {missing_cols}")
            
            # Check value range
            if 'value' in self.fear_greed_data.columns:
                if not (0 <= self.fear_greed_data['value'].min() <= self.fear_greed_data['value'].max() <= 100):
                    issues.append("Fear/Greed values should be between 0 and 100")
        
        if self.trading_data is not None:
            # Check for required columns
            required_trading_cols = ['Account', 'Side', 'Execution Price', 'Size USD']
            missing_cols = [col for col in required_trading_cols if col not in self.trading_data.columns]
            if missing_cols:
                issues.append(f"Trading data missing columns: {missing_cols}")
        
        return issues
