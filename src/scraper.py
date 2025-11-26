# src/scraper.py

from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

def get_news(ticker):
    url = f'https://finviz.com/quote.ashx?t={ticker}'
    req = Request(url=url, headers={'User-Agent': 'Mozilla/5.0'})

    try:
        response = urlopen(req)
        html = BeautifulSoup(response, features="html.parser")
        news_table = html.find(id='news-table')

        if not news_table:
            return pd.DataFrame()

        parsed_data = []
        current_date = None

        for row in news_table.find_all('tr'):
            a_tag = row.find('a')
            if not a_tag:
                continue
            
            headline = a_tag.text
            
            # Extract date and time from the first column
            cols = row.find_all('td')
            if len(cols) < 2:
                continue
                
            date_data = cols[0].text.strip().split()
            
            # Format: "Feb-26-25 09:30AM" (Date + Time) or "10:45AM" (Time only)
            if len(date_data) == 2:
                date_str = date_data[0]
                time_str = date_data[1]
                current_date = date_str # Update cache
            elif len(date_data) == 1:
                time_str = date_data[0]
                date_str = current_date # Use cached date
            else:
                continue

            # Convert to datetime object
            full_datetime_str = f"{date_str} {time_str}"
            
            try:
                if "Today" in date_str:
                    dt_obj = datetime.combine(datetime.now().date(), 
                                            datetime.strptime(time_str, "%I:%M%p").time())
                else:
                    dt_obj = datetime.strptime(full_datetime_str, "%b-%d-%y %I:%M%p")
                
                parsed_data.append([ticker, dt_obj, headline])
                
            except ValueError:
                continue

        df = pd.DataFrame(parsed_data, columns=['Ticker', 'Datetime', 'Headline'])
        df.sort_values(by='Datetime', ascending=False, inplace=True)
        
        return df

    except Exception as e:
        print(f"Error scraping {ticker}: {e}")
        return pd.DataFrame()