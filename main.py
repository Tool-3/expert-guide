import streamlit as st
import pandas as pd
from alpha_vantage.timeseries import TimeSeries
import matplotlib.pyplot as plt

# Set up Alpha Vantage API
api_key = '1VOMFY36F61VJZKC'
ts = TimeSeries(key=api_key, output_format='pandas')

st.title('Indian Stock Market Analysis Tool')

# Input for stock symbol
symbol = st.text_input('Enter stock symbol', 'TCS')

# Fetch stock data
if symbol:
    try:
        data, meta_data = ts.get_daily(symbol=symbol, outputsize='full')
        st.write(f"Data for {symbol}:")
        st.write(data.head())

        # Plot data
        st.write("Closing Price Chart:")
        plt.figure(figsize=(10, 5))
        plt.plot(data.index, data['4. close'], label='Closing Price')
        plt.title(f'{symbol} Closing Price')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.legend()
        st.pyplot(plt)
    except Exception as e:
        st.error(f"Error fetching data: {e}")
