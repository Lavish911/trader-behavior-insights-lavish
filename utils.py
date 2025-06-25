import pandas as pd
import numpy as np
from datetime import datetime
import io
import base64

def export_results(data, filename, file_format='csv'):
    """Export analysis results to various formats"""
    if file_format == 'csv':
        return data.to_csv(index=False)
    elif file_format == 'json':
        return data.to_json(orient='records', indent=2)
    else:
        raise ValueError("Unsupported file format. Use 'csv' or 'json'.")

def calculate_metrics(data, column):
    """Calculate comprehensive metrics for a given column"""
    if column not in data.columns:
        return {}
    
    series = data[column]
    
    return {
        'count': len(series),
        'mean': series.mean(),
        'median': series.median(),
        'std': series.std(),
        'min': series.min(),
        'max': series.max(),
        'q25': series.quantile(0.25),
        'q75': series.quantile(0.75),
        'skewness': series.skew(),
        'kurtosis': series.kurtosis()
    }

def format_currency(value):
    """Format currency values for display"""
    if pd.isna(value):
        return "N/A"
    
    if abs(value) >= 1000000:
        return f"${value/1000000:.2f}M"
    elif abs(value) >= 1000:
        return f"${value/1000:.2f}K"
    else:
        return f"${value:.2f}"

def format_percentage(value):
    """Format percentage values for display"""
    if pd.isna(value):
        return "N/A"
    return f"{value:.2f}%"

def calculate_drawdown(cumulative_returns):
    """Calculate drawdown series"""
    running_max = cumulative_returns.expanding().max()
    drawdown = (cumulative_returns - running_max) / running_max * 100
    return drawdown

def get_time_period_filter(data, date_column, period='1M'):
    """Filter data by time period"""
    if period == '1M':
        cutoff_date = datetime.now() - pd.DateOffset(months=1)
    elif period == '3M':
        cutoff_date = datetime.now() - pd.DateOffset(months=3)
    elif period == '6M':
        cutoff_date = datetime.now() - pd.DateOffset(months=6)
    elif period == '1Y':
        cutoff_date = datetime.now() - pd.DateOffset(years=1)
    else:
        return data
    
    return data[data[date_column] >= cutoff_date]

def validate_csv_structure(df, required_columns, dataset_name):
    """Validate CSV structure and return validation results"""
    issues = []
    
    # Check for required columns
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        issues.append(f"Missing required columns in {dataset_name}: {missing_columns}")
    
    # Check for empty dataframe
    if len(df) == 0:
        issues.append(f"{dataset_name} is empty")
    
    # Check for all NaN columns
    all_nan_columns = [col for col in df.columns if df[col].isna().all()]
    if all_nan_columns:
        issues.append(f"Columns with all NaN values in {dataset_name}: {all_nan_columns}")
    
    return issues

def create_download_link(df, filename, link_text):
    """Create a download link for dataframe"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{link_text}</a>'
    return href

def safe_divide(numerator, denominator, default=0):
    """Safely divide two numbers, handling division by zero"""
    if denominator == 0 or pd.isna(denominator):
        return default
    return numerator / denominator

def rolling_correlation(series1, series2, window=30):
    """Calculate rolling correlation between two series"""
    if len(series1) != len(series2):
        raise ValueError("Series must have the same length")
    
    if len(series1) < window:
        return pd.Series([np.nan] * len(series1), index=series1.index)
    
    return series1.rolling(window=window).corr(series2)

def detect_outliers(series, method='iqr', threshold=1.5):
    """Detect outliers in a series using IQR or Z-score method"""
    if method == 'iqr':
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR
        outliers = (series < lower_bound) | (series > upper_bound)
    elif method == 'zscore':
        z_scores = np.abs((series - series.mean()) / series.std())
        outliers = z_scores > threshold
    else:
        raise ValueError("Method must be 'iqr' or 'zscore'")
    
    return outliers

def calculate_risk_metrics(returns):
    """Calculate comprehensive risk metrics"""
    if len(returns) == 0:
        return {}
    
    return {
        'volatility': returns.std(),
        'var_95': returns.quantile(0.05),
        'cvar_95': returns[returns <= returns.quantile(0.05)].mean(),
        'max_loss': returns.min(),
        'positive_returns_ratio': (returns > 0).mean(),
        'avg_positive_return': returns[returns > 0].mean() if any(returns > 0) else 0,
        'avg_negative_return': returns[returns < 0].mean() if any(returns < 0) else 0
    }

def sentiment_to_numeric(sentiment_category):
    """Convert sentiment categories to numeric scores"""
    mapping = {
        'Extreme Fear': 1,
        'Fear': 2,
        'Neutral': 3,
        'Greed': 4,
        'Extreme Greed': 5
    }
    return mapping.get(sentiment_category, 3)

def create_summary_statistics(df, numeric_columns):
    """Create summary statistics for numeric columns"""
    summary = {}
    
    for col in numeric_columns:
        if col in df.columns:
            summary[col] = calculate_metrics(df, col)
    
    return summary
