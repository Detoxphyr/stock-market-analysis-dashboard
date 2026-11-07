
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page settings
st.set_page_config(
    page_title="Stock Market Dashboard",
    page_icon="📈",
    layout="wide"
)

# Dashboard title
st.title("📈 Stock Market Analysis Dashboard")
st.write("My first FinTech portfolio project")

# Sidebar
st.sidebar.header("Stock Selection")

ticker = st.sidebar.selectbox(
    "Choose a stock",
    ["AAPL", "NVDA", "TSLA", "MSFT", "AMZN"]
)

# Company information
company_names = {
    "AAPL": "Apple Inc.",
    "NVDA": "NVIDIA Corporation",
    "TSLA": "Tesla, Inc.",
    "MSFT": "Microsoft Corporation",
    "AMZN": "Amazon.com, Inc."
}

sector_names = {
    "AAPL": "Technology",
    "NVDA": "Technology / Semiconductors",
    "TSLA": "Automotive",
    "MSFT": "Technology / Software",
    "AMZN": "Consumer / E-commerce"
}

period = st.sidebar.selectbox(
    "Select time period",
    ["1mo", "3mo", "6mo", "1y", "2y"]
)

# Stock Watchlist
st.divider()
st.subheader("⭐ Market Watchlist")

watchlist = ["AAPL", "NVDA", "TSLA", "MSFT", "AMZN"]

watchlist_data = []

for symbol in watchlist:
    stock = yf.Ticker(symbol)
    history = stock.history(period="5d")

    if len(history) >= 2:
        latest = history["Close"].iloc[-1]
        previous = history["Close"].iloc[-2]

        daily_change = ((latest / previous) - 1) * 100

        watchlist_data.append({
            "Ticker": symbol,
            "Latest Price (USD)": round(latest, 2),
            "Daily Change (%)": round(daily_change, 2)
        })

watchlist_df = pd.DataFrame(watchlist_data)

st.dataframe(
    watchlist_df,
    use_container_width=True,
    hide_index=True
)

st.subheader(company_names[ticker])
st.caption(f"Ticker: {ticker} | Sector: {sector_names[ticker]}")

# Download stock data
@st.cache_data(ttl=300)
def get_stock_data(symbol, selected_period):
    stock = yf.Ticker(symbol)
    return stock.history(period=selected_period)

data = get_stock_data(ticker, period)

if data.empty:
    st.error("No stock data available. Please try again.")
else:
    # Calculate returns
    data["Daily Return (%)"] = (
        data["Close"].pct_change() * 100
    )

    # Calculate moving averages
    data["MA20"] = data["Close"].rolling(window=20).mean()
    data["MA50"] = data["Close"].rolling(window=50).mean()

    latest_price = data["Close"].iloc[-1]

    latest_price = data["Close"].iloc[-1]
    previous_price = data["Close"].iloc[-2] if len(data) > 1 else latest_price

    change = latest_price - previous_price
    change_percent = (change / previous_price) * 100 if previous_price else 0

    
    # Financial performance calculations
    period_return = (
        (data["Close"].iloc[-1] / data["Close"].iloc[0]) - 1
    ) * 100

    daily_returns = data["Close"].pct_change().dropna()

    annualised_volatility = (
        daily_returns.std() * (252 ** 0.5) * 100
    )

    highest_price = data["Close"].max()
    lowest_price = data["Close"].min()

    # Display financial metrics
    st.subheader("Financial Performance")

    col1, col2, col3 = st.columns(3)

    col1.metric("Latest Price", f"${latest_price:.2f}")
    col2.metric("Daily Change", f"${change:.2f}", f"{change_percent:.2f}%")
    col3.metric("Period Return", f"{period_return:.2f}%")

    col4, col5, col6 = st.columns(3)

    col4.metric("Annualised Volatility", f"{annualised_volatility:.2f}%")
    col5.metric("Highest Close", f"${highest_price:.2f}")
    col6.metric("Lowest Close", f"${lowest_price:.2f}")


        # Price chart
    st.subheader(f"{ticker} Stock Price")

    chart = go.Figure()

    # Candlestick chart
    chart.add_trace(
        go.Candlestick(
            x=data.index,
            open=data["Open"],
            high=data["High"],
            low=data["Low"],
            close=data["Close"],
            name=ticker
        )
    )

    # 20-day moving average
    chart.add_trace(
        go.Scatter(
            x=data.index,
            y=data["MA20"],
            mode="lines",
            name="MA20 (20-day average)"
        )
    )

    # 50-day moving average
    chart.add_trace(
        go.Scatter(
            x=data.index,
            y=data["MA50"],
            mode="lines",
            name="MA50 (50-day average)"
        )
    )

    chart.update_layout(
        title=f"{ticker} Candlestick Chart with Moving Averages",
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        template="plotly_dark",
        xaxis_rangeslider_visible=False
    )

    st.plotly_chart(chart, use_container_width=True)

    # Stock comparison
    st.divider()
    st.subheader("📊 Stock Performance Comparison")

    comparison_period = st.selectbox(
        "Comparison period",
        ["1mo", "3mo", "6mo", "1y", "2y"],
        index=3
    )

    comparison_tickers = ["AAPL", "NVDA", "TSLA"]

    comparison_data = yf.download(
        comparison_tickers,
        period=comparison_period,
        auto_adjust=True,
        progress=False
    )["Close"]

    # Normalise prices to a starting value of 100
    normalised_data = (
        comparison_data / comparison_data.iloc[0]
    ) * 100

    comparison_chart = px.line(
        normalised_data,
        title="Relative Stock Performance",
        labels={
            "value": "Performance (Starting at 100)",
            "Date": "Date",
            "variable": "Stock"
        }
    )

    st.plotly_chart(
        comparison_chart,
        use_container_width=True
    )

    # Show data
    with st.expander("View historical stock data"):
        st.dataframe(data)
