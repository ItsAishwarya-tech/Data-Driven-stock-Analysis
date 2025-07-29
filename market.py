import streamlit as st
import pandas as pd
import sqlite3
import seaborn as sns
import matplotlib.pyplot as plt

# Database path
DB_PATH = r"C:\Users\asus\Desktop\stock_analysis1\output\market_analysis.db"

# Connect to SQLite database
conn = sqlite3.connect(DB_PATH)

# Load tables
@st.cache_data
def load_data():
    stock_prices = pd.read_sql("SELECT * FROM stock_prices", conn)
    gain_loss = pd.read_sql("SELECT * FROM gain_loss", conn)
    volatility = pd.read_sql("SELECT * FROM volatility_summary", conn)
    cumulative = pd.read_sql("SELECT * FROM cumulative_return_summary", conn)
    sector_perf = pd.read_sql("SELECT * FROM sector_performance", conn)

    # ✅ Do NOT plot here
    return stock_prices, gain_loss, volatility, cumulative, sector_perf



    return stock_prices, gain_loss, volatility, cumulative, sector_perf

stock_prices, gain_loss, volatility, cumulative, sector_perf = load_data()

# ✅ Normalize column names to avoid case/key errors
gain_loss.columns = [col.strip() for col in gain_loss.columns]

# Streamlit UI
st.title("📈 Stock Market Analysis Dashboard")

# Sidebar filters
st.sidebar.header("Filters")
selected_month = st.sidebar.selectbox("Select Month", gain_loss['Month'].unique())
selected_stock = st.sidebar.selectbox("Select Stock", stock_prices.columns[1:])

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Top Gainers/Losers", "Correlation", "Sector Performance"])

# ✅ Tab 1: Overview
with tab1:
    st.subheader("Market Overview")
    st.write("### Cumulative Returns")
    st.dataframe(cumulative)
    st.write("### Volatility Summary")
    st.dataframe(volatility)

# ✅ Tab 2: Top Gainers & Losers
with tab2:
    st.subheader(f"Top 5 Gainers & Losers - {selected_month}")
    month_data = gain_loss[gain_loss['Month'] == selected_month]

    if month_data.empty:
        st.warning("No data available for this month.")
    else:
        top_gainers = month_data.nlargest(5, 'Return(%)')
        top_losers = month_data.nsmallest(5, 'Return(%)')

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 🚀 Top Gainers")
            st.bar_chart(top_gainers.set_index('Stock')['Return(%)'])
        with col2:
            st.markdown("#### 📉 Top Losers")
            st.bar_chart(top_losers.set_index('Stock')['Return(%)'])

# ✅ Tab 3: Correlation Heatmap
with tab3:
    st.subheader("Stock Price Correlation")

    # ✅ Check if 'date' column exists and drop it
    if 'date' in stock_prices.columns:
        corr_data = stock_prices.drop(columns=['date'])
    else:
        corr_data = stock_prices.copy()  # No date column

    # ✅ Keep only numeric columns for correlation
    numeric_data = corr_data.select_dtypes(include=['float64', 'int64'])
    corr = numeric_data.corr()

    # ✅ Create a larger figure for better readability
    fig, ax = plt.subplots(figsize=(18, 14))
    sns.heatmap(corr, annot=False, cmap="coolwarm", cbar=True, ax=ax)

    # ✅ Rotate labels for better fit
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.title("Stock Price Correlation (Based on Daily Returns)", fontsize=18)

    st.pyplot(fig)

    # ✅ Option to download correlation CSV
    csv_corr = corr.to_csv().encode('utf-8')
    st.download_button("Download Correlation CSV", data=csv_corr, file_name="correlation_matrix.csv", mime="text/csv")

# ✅ Tab 4: Sector Performance
# ✅ Tab 4: Sector Performance
with tab4:
    st.subheader("Sector Performance")

    # Debug to see column names
    st.write("Columns in sector_perf:", sector_perf.columns.tolist())

    # Normalize
    sector_perf.columns = [col.strip().lower() for col in sector_perf.columns]

    # Dynamic handling
    if 'sector' in sector_perf.columns and 'final cumulative return' in sector_perf.columns:
        st.bar_chart(sector_perf.set_index('sector')['final cumulative return'])
    elif 'sector' in sector_perf.columns and 'performance(%)' in sector_perf.columns:
        st.bar_chart(sector_perf.set_index('sector')['performance(%)'])
    else:
        st.error(f"Expected columns not found. Found: {sector_perf.columns.tolist()}")


# Close DB connection
conn.close()


