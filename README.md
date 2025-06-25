# Bitcoin Market Sentiment & Trading Analytics Dashboard

A comprehensive data science project analyzing the relationship between Bitcoin market sentiment (Fear & Greed Index) and trader performance on the Hyperliquid platform.

## 🎯 Project Overview

This project explores how market sentiment correlates with trading behavior and outcomes, providing actionable insights for smarter trading strategies. Built as part of a data science hiring assignment for a Web3 trading company.

## 📊 Datasets

- **Bitcoin Market Sentiment Dataset**: Fear & Greed Index with daily sentiment classifications
- **Historical Trader Data**: Hyperliquid trading records with execution prices, volumes, P&L, and timestamps

## 🚀 Features

- **Interactive Dashboard**: Multi-tab Streamlit interface for comprehensive analysis
- **Correlation Analysis**: Statistical relationships between sentiment and trading performance
- **Advanced Analytics**: Rolling correlations, risk metrics, and performance comparisons
- **Data Visualization**: Interactive charts showing sentiment trends, P&L distributions, and trading patterns
- **Export Capabilities**: Results exportable in CSV/JSON formats

## 📈 Key Insights

- Correlation analysis between Fear/Greed sentiment levels and trading outcomes
- Performance metrics (win rates, Sharpe ratios, drawdowns) by sentiment category
- Temporal patterns in sentiment vs trading behavior
- Risk analysis across different market sentiment regimes

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **Data Processing**: Pandas, NumPy (CSV-based, no database required)
- **Visualization**: Plotly
- **Statistics**: SciPy
- **Language**: Python 3.11
- **Data Storage**: File-based CSV processing (no database setup needed)

## 📦 Installation & Setup

**No database required!** This solution works entirely with CSV files.

1. Clone the repository:
```bash
git clone https://github.com/yourusername/bitcoin-sentiment-analytics.git
cd bitcoin-sentiment-analytics
```

2. Install dependencies:
```bash
pip install -r requirements-export.txt
```

3. Run the dashboard:
```bash
streamlit run app.py
```

That's it! The dashboard will load sample data automatically or you can upload your own CSV files.

## 📁 Project Structure

```
├── app.py                 # Main Streamlit application
├── data_processor.py      # Data loading and preprocessing
├── analysis.py           # Statistical analysis and correlations
├── visualizations.py     # Chart generation and dashboard visuals
├── utils.py              # Utility functions and metrics
├── data/                 # Sample datasets
│   ├── fear_greed_index.csv
│   └── historical_data.csv
├── requirements.txt      # Python dependencies
└── README.md            # Project documentation
```

## 💡 Usage

1. **Load Data**: Upload your CSV files or use the sample data
2. **Explore Tabs**: Navigate through Overview, Sentiment Analysis, Trading Performance, Correlations, and Advanced Analytics
3. **Interactive Analysis**: Use filters and controls to explore different time periods and metrics
4. **Export Results**: Download analysis results for further use

## 📊 Analysis Capabilities

### Overview Dashboard
- Data quality metrics and summary statistics
- Timeline overview of sentiment and trading activity

### Sentiment Analysis
- Distribution of Fear/Greed classifications
- Monthly sentiment trends and patterns

### Trading Performance
- P&L distributions and cumulative performance
- Volume analysis and trading patterns

### Correlation Analysis
- Sentiment vs performance scatter plots
- Statistical correlation heatmaps

### Advanced Analytics
- Rolling correlation analysis
- Volatility and regime analysis
- Risk metrics by sentiment category

## 🎯 Assignment Objectives Met

✅ Explored relationship between trader performance and market sentiment  
✅ Uncovered hidden patterns in trading behavior  
✅ Delivered actionable insights for trading strategies  
✅ Professional presentation suitable for data science portfolio  

## 🔧 Technical Features

- **Zero Database Setup**: Works entirely with CSV file processing
- **Plug-and-Play**: Upload your data files and start analyzing immediately
- **Modular Architecture**: Clean separation of concerns for easy extension
- **Memory-Efficient**: Processes large datasets entirely in RAM using pandas
- **Self-Contained**: No external dependencies beyond Python packages
- **Portable**: Runs on any system with Python 3.11+

## 📝 License

This project is created for educational and portfolio purposes.



Created as part of a Junior Data Scientist application demonstrating analytical capabilities in cryptocurrency trading and market sentiment analysis.

---

*This dashboard demonstrates proficiency in data science, statistical analysis, and interactive visualization development for financial trading applications.*
