import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import yfinance as yf
from datetime import timedelta
import numpy as np

# Import your modules
from src.scraper import get_news
from src.sentiment import analyze_sentiment

# --- Page Config (Muss die erste Zeile sein) ---
st.set_page_config(
    page_title="AI Financial Terminal", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- Custom CSS für den "Profi-Look" ---
st.markdown("""
<style>
    .metric-card {
        background-color: #0E1117;
        border: 1px solid #262730;
        padding: 20px;
        border-radius: 10px;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

st.title("AI Sentiment Financial Terminal")

# --- Sidebar ---
with st.sidebar:
    st.header("Asset Selection")
    ticker = st.text_input("Ticker Symbol", value="NVDA").upper()
    st.markdown("---")
    st.write("Analysis Settings")
    show_tables = st.checkbox("Show Raw Data Tables", value=True)
    
    if st.button("Run Analysis", type="primary"):
        run_analysis = True
    else:
        run_analysis = False

# --- Main Logic ---
if run_analysis or ticker: # Führt es auch beim Start aus
    with st.spinner(f"Processing data for {ticker}..."):
        
        # 1. LOAD & PROCESS DATA
        news_df = get_news(ticker)

        if news_df.empty:
            st.error(f"No news found for {ticker}. Please check the symbol.")
        else:
            # Sentiment berechnen
            news_df['Score'] = news_df['Headline'].apply(analyze_sentiment)
            
            # Daten aggregieren (Täglich)
            news_df['Date_Only'] = news_df['Datetime'].dt.date
            daily_stats = news_df.groupby('Date_Only').agg(
                Avg_Score=('Score', 'mean'),
                Count=('Score', 'count')
            ).sort_index()

            # Aktienkurs laden (Zeitraum an News anpassen)
            start_date = daily_stats.index.min() - timedelta(days=5) # Puffer für Moving Averages
            end_date = daily_stats.index.max() + timedelta(days=1)
            stock_data = yf.download(ticker, start=start_date, end=end_date, progress=False)

            # --- REPARATUR-BLOCK START ---
            # 1. Prüfen, ob Daten leer sind
            if stock_data.empty:
                st.warning("Keine Aktienkurse für diesen Zeitraum gefunden.")
            else:
                # 2. MultiIndex Header entfernen (das ist der Hauptgrund für leere Charts!)
                if isinstance(stock_data.columns, pd.MultiIndex):
                    stock_data.columns = stock_data.columns.get_level_values(0)
                
                # 3. Zeitzone entfernen (Plotly mag manchmal keine Zeitzonen im Index)
                if stock_data.index.tz is not None:
                    stock_data.index = stock_data.index.tz_localize(None)
            # --- REPARATUR-BLOCK ENDE ---

            # --- DASHBOARD LAYOUT ---

            # 2. KEY PERFORMANCE INDICATORS (KPIs)
            # Berechne Veränderungen
            latest_price = float(stock_data['Close'].iloc[-1])
            start_price = float(stock_data['Close'].iloc[0])
            
            price_change = latest_price - start_price
            price_pct = (price_change / start_price) * 100
            
            avg_sentiment_total = news_df['Score'].mean()
            sentiment_delta = daily_stats['Avg_Score'].iloc[-1] - daily_stats['Avg_Score'].iloc[0]

            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Current Price", f"${latest_price:.2f}", f"{price_pct:.2f}%")
            with col2:
                st.metric("News Volume", len(news_df), f"Last 24h: {len(news_df[news_df['Datetime'] > (pd.Timestamp.now() - pd.Timedelta(days=1))])}")
            with col3:
                sent_label = "Bullish" if avg_sentiment_total > 0.05 else "Bearish" if avg_sentiment_total < -0.05 else "Neutral"
                st.metric("Market Mood", sent_label, f"{avg_sentiment_total:.2f} Score")
            with col4:
                st.metric("Sentiment Momentum", f"{daily_stats['Avg_Score'].iloc[-1]:.2f}", f"{sentiment_delta:.2f} vs Start")

            st.markdown("---")

            # 3. VISUALISIERUNG (Die "Heavy Lifter")
            
            # ROW 1: Der Hauptchart (Preis + Sentiment Balken)
            col_main, col_dist = st.columns([2, 1])
            
            with col_main:
                st.subheader("Price vs. Sentiment Trend")
                
                # Daten vorbereiten: Wir brauchen gemeinsame Datenpunkte
                # Wir glätten das Sentiment (3-Tage Durchschnitt), um den "Trend" zu sehen
                daily_stats['Sentiment_MA'] = daily_stats['Avg_Score'].rolling(window=3, min_periods=1).mean()
                
                # Subplots erstellen (2 Reihen: Oben Preis, Unten Sentiment)
                fig = make_subplots(
                    rows=2, cols=1, 
                    shared_xaxes=True, 
                    vertical_spacing=0.05,
                    row_heights=[0.7, 0.3],
                    subplot_titles=("Stock Price (Candlestick)", "Sentiment Trend (3-Day Moving Avg)")
                )

                # 1. Oben: Candlestick Chart (Wie bei TradingView)
                if not stock_data.empty:
                    fig.add_trace(go.Candlestick(
                        x=stock_data.index,
                        open=stock_data['Open'],
                        high=stock_data['High'],
                        low=stock_data['Low'],
                        close=stock_data['Close'],
                        name="OHLC"
                    ), row=1, col=1)

                # 2. Unten: Sentiment Area Chart
                # Wir färben die Fläche je nach Positiv/Negativ
                fig.add_trace(go.Scatter(
                    x=daily_stats.index,
                    y=daily_stats['Sentiment_MA'],
                    name="Sentiment Trend",
                    line=dict(color='white', width=1),
                    fill='tozeroy', # Füllt Fläche bis zur Nulllinie
                    # Kleiner Hack für dynamische Farbe im Line-Chart ist schwer, 
                    # daher nehmen wir hier neutrales Lila oder Weiß mit Füllung
                    fillcolor='rgba(100, 100, 255, 0.2)' 
                ), row=2, col=1)

                # Nulllinie beim Sentiment hinzufügen
                fig.add_hline(y=0, line_dash="dot", line_color="gray", row=2, col=1)

                # Layout verschönern
                fig.update_layout(
                    height=500,
                    xaxis_rangeslider_visible=False, # Den Standard-Slider entfernen wir
                    showlegend=False,
                    margin=dict(l=0, r=0, t=20, b=0),
                    hovermode="x unified" # Cooles Feature: Zeigt Werte für beide Charts gleichzeitig beim Hovern
                )
                
                # Y-Achsen Beschriftung
                fig.update_yaxes(title_text="Price ($)", row=1, col=1)
                fig.update_yaxes(title_text="Sentiment", row=2, col=1)

                st.plotly_chart(fig, use_container_width=True)

            with col_dist:
                st.subheader("Sentiment Distribution")
                
                # Kategorisieren für Pie Chart
                def get_category(score):
                    if score > 0.05: return 'Positive'
                    if score < -0.05: return 'Negative'
                    return 'Neutral'
                
                news_df['Category'] = news_df['Score'].apply(get_category)
                counts = news_df['Category'].value_counts()
                
                # KORREKTUR: Wir nutzen px.pie statt px.donut
                fig_pie = px.pie(
                    values=counts.values, 
                    names=counts.index, 
                    color=counts.index,
                    color_discrete_map={'Positive':'#00CC96', 'Negative':'#EF553B', 'Neutral':'#636EFA'},
                    hole=0.4 # Das macht es zum Donut
                )
                fig_pie.update_layout(height=450, margin=dict(l=0, r=0, t=0, b=0))
                st.plotly_chart(fig_pie, use_container_width=True)

            # ROW 2: Detail Analyse (Scatter Plot)
            st.subheader("Deep Dive: Every Single Headline")
            st.caption("Jeder Punkt ist eine Nachricht. Hover für Details.")
            
            fig_scatter = px.scatter(
                news_df, 
                x="Datetime", 
                y="Score", 
                color="Score",
                color_continuous_scale="RdYlGn",
                hover_data=["Headline"],
                size_max=10
            )
            # Eine Nulllinie hinzufügen
            fig_scatter.add_hline(y=0, line_dash="dash", line_color="white", opacity=0.3)
            fig_scatter.update_layout(height=350)
            st.plotly_chart(fig_scatter, use_container_width=True)

            # 4. DATA TABLES (Gestylt)
            if show_tables:
                st.subheader("Raw Data Feed")
                
                # Wir formatieren die Tabelle schön
                st.dataframe(
                    news_df[['Datetime', 'Headline', 'Score']],
                    column_config={
                        "Datetime": st.column_config.DatetimeColumn("Time", format="D. MMM HH:mm"),
                        "Score": st.column_config.ProgressColumn(
                            "Sentiment Score",
                            help="VADER Score von -1 (negativ) bis +1 (positiv)",
                            min_value=-1,
                            max_value=1,
                            format="%.2f",
                        ),
                        "Headline": st.column_config.TextColumn("News Headline", width="large")
                    },
                    use_container_width=True,
                    hide_index=True,
                    height=400
                )