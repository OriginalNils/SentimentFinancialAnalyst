import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
from datetime import timedelta

# Import your modules
from src.scraper import get_news
from src.sentiment import analyze_sentiment

# --- Page Config ---
st.set_page_config(page_title="AI Financial Analyst", layout="wide")
st.title("🤖 AI Sentiment Financial Analyst")

# --- Sidebar ---
st.sidebar.header("Configuration")
ticker = st.sidebar.text_input("Enter Ticker Symbol", value="TSLA").upper()
show_raw_data = st.sidebar.checkbox("Show Raw News Data")

# --- Main App Logic ---
if st.sidebar.button("Analyze"):
    with st.spinner(f"Scraping news and analyzing sentiment for {ticker}..."):
        
        # 1. GET DATA (Use your scraper)
        # TODO: Call get_news(ticker) and store it in 'news_df'
        news_df = get_news(ticker)

        if news_df.empty:
            st.error(f"No news found for {ticker}. Check the symbol or try again later.")
        else:
            # 2. APPLY SENTIMENT ANALYSIS
            # TODO: Apply your analyze_sentiment function to the 'Headline' column.
            # Save the result in a new column called 'Score'.
            news_df['Score'] = news_df['Headline'].apply(analyze_sentiment)

            # 3. AGGREGATE DATA (Group by Date)
            # We convert the datetime to just 'Date' to group them
            news_df['Date'] = news_df['Datetime'].dt.date
            
            # TODO: Group by 'Date' and calculate the mean of 'Score'.
            # Store this in a dataframe called 'daily_sentiment'
            daily_sentiment = news_df.groupby('Date')['Score'].mean()

            # 4. FETCH STOCK PRICE (Comparison)
            # We fetch data from the earliest news date until today
            start_date = daily_sentiment.index.min()
            end_date = daily_sentiment.index.max() + timedelta(days=1)
            
            stock_data = yf.download(ticker, start=start_date, end=end_date)

            # --- VISUALIZATION SECTION ---
            
            # Metrics Row
            avg_sentiment = news_df['Score'].mean()
            sentiment_label = "Positive" if avg_sentiment > 0 else "Negative"
            
            col1, col2 = st.columns(2)
            col1.metric("Total News Analyzed", len(news_df))
            col2.metric("Overall Sentiment", f"{avg_sentiment:.2f}", sentiment_label)

            # Plot: Sentiment vs Stock Price
            st.subheader("Sentiment vs. Stock Price")
            
            # Create a Plotly figure with 2 y-axes (Dual Axis Chart)
            fig = go.Figure()

            # Trace 1: Sentiment (Bar Chart)
            fig.add_trace(go.Bar(
                x=daily_sentiment.index,
                y=daily_sentiment.values,
                name="Daily Sentiment",
                marker_color=daily_sentiment.values, # Color by value
                marker_colorscale="RdYlGn",          # Red to Green
                opacity=0.6
            ))

            # Trace 2: Stock Price (Line Chart)
            # TODO: Add a line trace using stock_data.index and stock_data['Close']
            # Hint: fig.add_trace(go.Scatter(x=..., y=..., name="Stock Price", yaxis="y2"))
            if not stock_data.empty:
                 fig.add_trace(go.Scatter(
                    x=stock_data.index,
                    y=stock_data['Close'],
                    name="Stock Price",
                    yaxis="y2", # Maps to the second y-axis
                    line=dict(color='blue', width=2)
                ))

            # Layout for Dual Axis
            fig.update_layout(
                title=f"{ticker} Sentiment & Price Analysis",
                yaxis=dict(title="Sentiment Score (-1 to 1)"),
                yaxis2=dict(title="Stock Price ($)", overlaying="y", side="right"),
                xaxis=dict(title="Date"),
                showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)

            # 5. SHOW RAW DATA (Optional)
            if show_raw_data:
                st.subheader("Raw Headlines & Scores")
                st.dataframe(news_df[['Datetime', 'Headline', 'Score']])