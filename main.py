import streamlit as st
import pandas as pd
import requests
from io import StringIO
import datetime

# Function to fetch historical stock data from NSE using a direct CSV link
def fetch_nse_data(symbol, start_date, end_date):
    # Convert dates to the format used by NSE
    start_date_str = start_date.strftime("%d-%b-%Y").upper()
    end_date_str = end_date.strftime("%d-%b-%Y").upper()
    
    # Construct the download link for the historical data
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
    
    # Headers for the request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Convert the response JSON to DataFrame
        data = response.json()
        calls_df = pd.json_normalize(data['records']['data'])
        
        # Process call options data
        if 'CE' in data['records']:
            ce_data = pd.json_normalize(data['records']['data'])
            ce_data['date'] = pd.to_datetime(ce_data['date'])
            ce_data = ce_data.sort_values(by=['date'])
            return ce_data
        
        return pd.DataFrame()
        
    except requests.RequestException as e:
        st.error(f"Error fetching data from NSE: {str(e)}")
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
        
        if not data.empty:
            st.write("Processed Data:")
            st.write(data)
            st.line_chart(data.set_index('date')['close'])
        else:
            st.info("No data available for the selected parameters.")

if __name__ == "__main__":
    main()
