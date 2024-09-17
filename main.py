import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
from scipy.stats import norm

# Fetch stock price and option chain
def fetch_data(ticker):
    stock = yf.Ticker(ticker)
    stock_price = stock.history(period="1d")['Close'].iloc[0]
    
    try:
        expirations = stock.options
        option_chain = stock.option_chain(expirations[0])
        calls = option_chain.calls
        puts = option_chain.puts
    except:
        st.error("Error fetching options data.")
        return None, None, None
    
    return stock_price, calls, puts, expirations
  # Calculate Greeks using the Black-Scholes model
def calculate_greeks(option_df, stock_price, risk_free_rate=0.01):
    T = (pd.to_datetime(option_df['lastTradeDate']) - pd.Timestamp('today')).dt.days / 365.0
    d1 = (np.log(stock_price / option_df['strike']) + (risk_free_rate + 0.5 * option_df['impliedVolatility'] ** 2) * T) / (option_df['impliedVolatility'] * np.sqrt(T))
    d2 = d1 - option_df['impliedVolatility'] * np.sqrt(T)
    
    option_df['Delta'] = norm.cdf(d1)
    option_df['Gamma'] = norm.pdf(d1) / (stock_price * option_df['impliedVolatility'] * np.sqrt(T))
    option_df['Theta'] = (-stock_price * norm.pdf(d1) * option_df['impliedVolatility']) / (2 * np.sqrt(T)) - risk_free_rate * option_df['strike'] * np.exp(-risk_free_rate * T) * norm.cdf(d2)
    option_df['Vega'] = stock_price * norm.pdf(d1) * np.sqrt(T)
    option_df['Rho'] = option_df['strike'] * T * np.exp(-risk_free_rate * T) * norm.cdf(d2)
    
    return option_df
  
  def calculate_probability_of_profit(option_df, stock_price):
    # Assuming log-normal distribution and using Delta to approximate the probability of profit
    option_df['POP'] = norm.cdf(option_df['Delta'])  # Simplified, adjust based on conditions (e.g., Call/Put)
    return option_df
  import plotly.express as px

st.title("📈 Indian Stock Market Options Trading Analytics Tool")
st.sidebar.header("User Inputs")

# Ticker List
INDIAN_TICKERS = ['RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS', 'HINDUNILVR.NS', 'ITC.NS', 'ICICIBANK.NS', 'SBIN.NS', 'LT.NS', 'BHARTIARTL.NS']
ticker = st.sidebar.selectbox("Select Stock Symbol", options=INDIAN_TICKERS)

if ticker:
    # Fetch stock and option data
    stock_price, calls, puts, expirations = fetch_data(ticker)
    
    if stock_price and not calls.empty:
        # Display stock price
        st.write(f"**{ticker} Current Price**: ₹{stock_price}")
        
        # Select option type
        option_type = st.sidebar.radio("Select Option Type", ('Calls', 'Puts'))
        options_data = calls if option_type == 'Calls' else puts

        # Calculate Greeks
        options_data = calculate_greeks(options_data, stock_price)
        
        # Calculate Probability of Profit
        options_data = calculate_probability_of_profit(options_data, stock_price)
        
        # Display Options Data
        st.write(f"### {option_type} Options for {ticker}")
        st.dataframe(options_data)
        
        # Plot Greeks
        fig = px.scatter(options_data, x='strike', y='Delta', size='openInterest', color='impliedVolatility',
                         hover_data=['Gamma', 'Theta', 'Vega', 'Rho'], title=f"{option_type} Greeks")
        st.plotly_chart(fig)
