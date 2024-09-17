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
        return data['Close']
    except Exception as e:
        st.error(f"Error fetching historical data for {symbol}: {str(e)}")
        return None

# Function to fetch historical options chain data (NSEpy only supports options for indices like NIFTY)
def get_options_chain(symbol, expiry):
    expiry_date = datetime.datetime.strptime(expiry, "%Y-%m-%d").date()
    try:
        options_data = nse.get_history(symbol=symbol, start=expiry_date, end=expiry_date, index=True, option_type='CE')
        if options_data.empty:
            st.error(f"No options data available for {symbol} on {expiry_date}")
            return None
        calls = options_data[options_data['OPTION_TYP'] == 'CE']
        puts = options_data[options_data['OPTION_TYP'] == 'PE']
        return calls, puts
    except Exception as e:
        st.error(f"Error fetching options data: {str(e)}")
        return None, None

# Greeks calculation
def calculate_greeks(option_df, stock_price, risk_free_rate=0.01):
    try:
        T = (pd.to_datetime(option_df['expiry']) - pd.to_datetime('today')).dt.days / 365
        option_df['d1'] = (np.log(stock_price / option_df['strike']) + (risk_free_rate + 0.5 * option_df['impliedVolatility'] ** 2) * T) / (option_df['impliedVolatility'] * np.sqrt(T))
        option_df['d2'] = option_df['d1'] - option_df['impliedVolatility'] * np.sqrt(T)
        
        option_df['Delta'] = norm.cdf(option_df['d1'])
        option_df['Gamma'] = norm.pdf(option_df['d1']) / (stock_price * option_df['impliedVolatility'] * np.sqrt(T))
        option_df['Theta'] = - (stock_price * norm.pdf(option_df['d1']) * option_df['impliedVolatility']) / (2 * np.sqrt(T))
        option_df['Theta'] -= risk_free_rate * option_df['strike'] * np.exp(-risk_free_rate * T) * norm.cdf(option_df['d2'])
        option_df['Vega'] = stock_price * norm.pdf(option_df['d1']) * np.sqrt(T)
        option_df['Rho'] = option_df['strike'] * T * np.exp(-risk_free_rate * T) * norm.cdf(option_df['d2'])
        
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
    symbol = st.sidebar.text_input("Enter Stock Symbol", value="RELIANCE")
    start_date = st.sidebar.date_input("Start Date", value=datetime.date(2023, 1, 1))
    end_date = st.sidebar.date_input("End Date", value=datetime.date.today())

    # Fetch historical stock price data
    if symbol:
        st.subheader(f"Stock Data for {symbol}")
        stock_data = get_historical_stock_price(symbol, start_date, end_date)
        if stock_data is not None:
            st.line_chart(stock_data)

    # Fetch options chain data and calculate Greeks
    st.sidebar.subheader("Options Data")
    expiry_date = st.sidebar.text_input("Enter Expiry Date (YYYY-MM-DD)", value="2023-12-31")
    if expiry_date:
        calls, puts = get_options_chain("NIFTY", expiry_date)
        if calls is not None and puts is not None:
            st.subheader("Options Chain")
            st.write("Calls")
            st.write(calls)
            st.write("Puts")
            st.write(puts)

            # Fetch the current stock price for Greeks calculation
            stock_price = stock_data.iloc[-1] if stock_data is not None else None
            if stock_price:
                st.subheader(f"Greeks for Options Expiring on {expiry_date}")
                calls_with_greeks = calculate_greeks(calls, stock_price)
                puts_with_greeks = calculate_greeks(puts, stock_price)
                st.write("Calls with Greeks")
                st.write(calls_with_greeks)
                st.write("Puts with Greeks")
                st.write(puts_with_greeks)

if __name__ == "__main__":
    main()
