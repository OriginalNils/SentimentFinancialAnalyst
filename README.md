# 🤖 AI Sentiment Financial Analyst

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Framework-Streamlit-ff4b4b)
![NLP](https://img.shields.io/badge/AI-NLTK%20VADER-green)

An advanced financial dashboard that correlates real-time news sentiment with stock price movements. It scrapes headlines, analyzes them using Natural Language Processing (NLP), and visualizes the impact of public opinion on market trends.



---

## 🚀 Features

* **Real-Time News Scraping:** Automatically fetches the latest headlines for any stock ticker from FinViz.
* **AI Sentiment Analysis:** Uses **VADER** (Valence Aware Dictionary and sEntiment Reasoner) to calculate a compound sentiment score (-1 to +1) for every single headline.
* **Professional Visualization:**
    * **Dual-Axis Technical Chart:** Overlays stock price (Candlesticks) with a smoothed sentiment trend line to spot correlations.
    * **Sentiment Gauge:** Donut chart showing the ratio of Bullish vs. Bearish news.
    * **Detail Scatter Plot:** Every headline is plotted as a data point to identify specific news events that moved the market.
* **Smart Data Processing:** Aggregates irregular news updates into daily metrics and handles time-series alignment with market data.

---

## 🛠️ Technology Stack

* **Frontend:** Streamlit (with custom CSS metrics)
* **Data Visualization:** Plotly (Candlesticks, Areas, Pies)
* **Data Source:** `yfinance` (Market Data) & `BeautifulSoup` (News Scraping)
* **NLP Engine:** `NLTK` (VADER Sentiment Module)

---

## 📦 Installation & Usage

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your_username/SentimentFinancialAnalyst.git](https://github.com/your_username/SentimentFinancialAnalyst.git)
    cd SentimentFinancialAnalyst
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the App:**
    ```bash
    streamlit run app.py
    ```

---

## 🧠 How It Works

1.  **Extraction:** The app scrapes the news table from `finviz.com` based on the user's ticker input.
2.  **Processing:** It parses the "Date/Time" formats and converts headlines into text strings.
3.  **Analysis:** The NLTK VADER analyzer evaluates each headline.
    * *Example:* "Tesla profits soar" -> **Positive (+0.6)**
    * *Example:* "Production halted due to fire" -> **Negative (-0.7)**
4.  **Correlation:** The app aligns these scores with the daily closing prices of the stock to visualize if sentiment predicts price action.

---

## 📄 License

This project is licensed under the MIT License.