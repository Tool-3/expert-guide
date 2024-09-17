import streamlit as st
import pandas as pd
import requests
from io import StringIO
import datetime

# Function to fetch historical stock data from NSE
def fetch_nse_data(symbol, start_date, end_date):
    url = f"https://www.nseindia.com/api/historical/fo/stock-ssi?symbol={symbol}&expiryDate={end_date}&instrument=OPTSTK&segmentLink=17"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data['records']['data'])
        return df
    else:
        st.error(f"Error fetching data from NSE: HTTP {response.status_code}")
        return None

# Function to process and clean data
def process_data(df):
    if df is not None:
        df = pd.json_normalize(df['CE'])  # Extract Call data
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values(by=['date'])
        return df
    return pd.DataFrame()

# Streamlit App
def main():
    st.set_page_config(page_title="NSE Stock Data Analysis", page_icon="📈")
    st.title("NSE Stock Data Analysis Tool")

    # Sidebar for user input
    st.sidebar.header("User Inputs")
    symbol = st.sidebar.text_input("Enter Stock Symbol (e.g., RELIANCE)", value="RELIANCE")
    end_date = st.sidebar.date_input("End Date", value=datetime.date.today())
    start_date = st.sidebar.date_input("Start Date", value=datetime.date(2023, 1, 1))

    # Fetch and process data
    if symbol:
        st.subheader(f"Fetching Data for {symbol}")
        data = fetch_nse_data(symbol, start_date, end_date)
        if data is not None:
            st.write("Raw Data:")
            st.write(data.head())

            processed_data = process_data(data)
            if not processed_data.empty:
                st.write("Processed Data:")
                st.write(processed_data)
                st.line_chart(processed_data.set_index('date')['close'])
            else:
                st.info("No data available for the selected parameters.")

if __name__ == "__main__":
    main()
