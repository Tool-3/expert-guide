import streamlit as st
import nsepy as nse
import pandas as pd
import numpy as np
from scipy.stats import norm
import datetime
import plotly.express as px

# Function to fetch historical stock price using NSEpy
def get_historical_stock_price(symbol, start_date, end_date):
    try:
        data = nse.get_history(symbol=symbol, start=start_date, end=end_date)
        if data.empty:
            st.error(f"No historical stock data available for {symbol} between {start_date} and {end_date}")
            return None
        return data
    except Exception as e:
        st.error(f"Error fetching historical data for {symbol}: {str(e)}")
        return None

# Function to fetch options data (only indices with NSEpy)
def get_options_data(symbol, start_date, end_date):
    try:
        options_data = nse.get_history(symbol=symbol, start=start_date, end=end_date, index=True)
        if options_data.empty:
            st.error(f"No options data available for {symbol} between {start_date} and {end_date}")
            return None
        return options_data
    except Exception as e:
        st.error(f"Error fetching options data: {str(e)}")
        return None

# Greeks calculation
def calculate_greeks(option_df, stock_price, risk_free_rate=0.01):
    try:
        T = (pd.to_datetime(option_df['Expiry']) - pd.to_datetime('today')).dt.days / 365
        option_df['d1'] = (np.log(stock_price / option_df['Strike Price']) + (risk_free_rate + 0.5 * option_df['Implied Volatility'] ** 2) * T) / (option_df['Implied Volatility'] * np.sqrt(T))
        option_df['d2'] = option_df['d1'] - option_df['Implied Volatility'] * np.sqrt(T)
        
        option_df['Delta'] = norm.cdf(option_df['d1'])
        option_df['Gamma'] = norm.pdf(option_df['d1']) / (stock_price * option_df['Implied Volatility'] * np.sqrt(T))
        option_df['Theta'] = - (stock_price * norm.pdf(option_df['d1']) * option_df['Implied Volatility']) / (2 * np.sqrt(T))
        option_df['Theta'] -= risk_free_rate * option_df['Strike Price'] * np.exp(-risk_free_rate * T) * norm.cdf(option_df['d2'])
        option_df['Vega'] = stock_price * norm.pdf(option_df['d1']) * np.sqrt(T)
        option_df['Rho'] = option_df['Strike Price'] * T * np.exp(-risk_free_rate * T) * norm.cdf(option_df['d2'])
        
        return option_df
    except Exception as e:
        st.error(f"Error calculating Greeks: {str(e)}")
        return option_df

# Streamlit App
def main():
    st.set_page_config(page_title="Indian Stock Market Analytics Tool", page_icon="📈")
    st.title("Indian Stock Market Analytics Tool")

    # Sidebar inputs for ticker symbol and date range
    st.sidebar.header("User Inputs")
    symbol = st.sidebar.text_input("Enter Stock Symbol (e.g., RELIANCE)", value="RELIANCE")
    start_date = st.sidebar.date_input("Start Date", value=datetime.date(2023, 1, 1))
    end_date = st.sidebar.date_input("End Date", value=datetime.date.today())

    # Fetch historical stock price data
    if symbol:
        st.subheader(f"Stock Data for {symbol}")
        stock_data = get_historical_stock_price(symbol, start_date, end_date)
        if stock_data is not None:
            st.line_chart(stock_data['Close'])

    # Fetch options data
    st.sidebar.subheader("Options Data")
    if symbol:
        options_data = get_options_data(symbol, start_date, end_date)
        if options_data is not None:
            st.subheader("Options Chain")
            st.write(options_data)

            # Example Greeks calculation (replace with actual data)
            stock_price = stock_data['Close'].iloc[-1] if stock_data is not None else None
            if stock_price:
                st.subheader(f"Greeks for Options Expiring on {end_date}")
                options_data['Expiry'] = end_date
                options_data['Strike Price'] = np.nan  # Replace with actual strike prices
                options_data['Implied Volatility'] = np.nan  # Replace with actual volatilities
                options_with_greeks = calculate_greeks(options_data, stock_price)
                st.write(options_with_greeks)

if __name__ == "__main__":
    main()
