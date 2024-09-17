import streamlit as st
import nsepy as nse
import pandas as pd
import numpy as np
import datetime
from scipy.stats import norm
import plotly.express as px

def get_stock_price(symbol):
    today = datetime.date.today()
    data = nse.get_history(symbol=symbol, start=today, end=today)
    if not data.empty:
        return data['Close'].iloc[-1]
    else:
        st.error(f"No data found for {symbol}")
        return None

def get_options_chain(symbol, expiry):
    # Fetch current date options data
    expiry_date = datetime.datetime.strptime(expiry, "%Y-%m-%d").date()
    try:
        options_data = nse.get_index_pe_history(symbol=symbol, start=expiry_date, end=expiry_date)
        if options_data.empty:
            st.error(f"No options data found for {symbol}")
            return None, None
    except Exception as e:
        st.error(f"Error fetching options data: {str(e)}")
        return None, None
    
    calls = options_data[options_data['OPTION_TYP'] == 'CE']
    puts = options_data[options_data['OPTION_TYP'] == 'PE']
    
    return calls, puts

def calculate_greeks(option_df, stock_price, risk_free_rate=0.01):
    T = (pd.to_datetime(option_df['expiry']) - pd.Timestamp('today')).dt.days / 365.0
    d1 = (np.log(stock_price / option_df['strike']) + (risk_free_rate + 0.5 * option_df['impliedVolatility'] ** 2) * T) / (option_df['impliedVolatility'] * np.sqrt(T))
    d2 = d1 - option_df['impliedVolatility'] * np.sqrt(T)
    
    option_df['Delta'] = norm.cdf(d1)
    option_df['Gamma'] = norm.pdf(d1) / (stock_price * option_df['impliedVolatility'] * np.sqrt(T))
    option_df['Theta'] = (-stock_price * norm.pdf(d1) * option_df['impliedVolatility']) / (2 * np.sqrt(T)) - risk_free_rate * option_df['strike'] * np.exp(-risk_free_rate * T) * norm.cdf(d2)
    option_df['Vega'] = stock_price * norm.pdf(d1) * np.sqrt(T)
    option_df['Rho'] = option_df['strike'] * T * np.exp(-risk_free_rate * T) * norm.cdf(d2)
    
    return option_df

st.title("📈 Indian Stock Market Options Trading Analytics Tool (NSEpy Integrated)")
st.sidebar.header("User Inputs")

# List of symbols (you can add more stock symbols here)
INDIAN_TICKERS = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ITC', 'SBIN']

# Stock symbol selection
symbol = st.sidebar.selectbox("Select Stock Symbol", options=INDIAN_TICKERS)

# Select expiry date for options
expiry = st.sidebar.date_input("Select Expiry Date", min_value=datetime.date.today())

if symbol:
    # Fetch stock price
    stock_price = get_stock_price(symbol)
    
    if stock_price:
        st.write(f"**{symbol} Current Price**: ₹{stock_price}")
        
        # Fetch options chain
        calls, puts = get_options_chain(symbol, expiry.strftime("%Y-%m-%d"))
        
        if calls is not None:
            # Select Calls or Puts
            option_type = st.sidebar.radio("Select Option Type", ('Calls', 'Puts'))
            options_data = calls if option_type == 'Calls' else puts

            # Calculate Greeks
            options_data = calculate_greeks(options_data, stock_price)
            
            # Display Options Data
            st.write(f"### {option_type} Options for {symbol}")
            st.dataframe(options_data)
            
            # Plot Greeks
            fig = px.scatter(options_data, x='strike', y='Delta', size='openInterest', color='impliedVolatility',
                             hover_data=['Gamma', 'Theta', 'Vega', 'Rho'], title=f"{option_type} Greeks")
            st.plotly_chart(fig)
