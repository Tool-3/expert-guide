import streamlit as st

# Create a sidebar for user input
st.sidebar.title("Indian Options Analytical Tool")
st.sidebar.header("Select Option")
option_type = st.sidebar.selectbox("Select Option Type", ["Call", "Put"])
strike_price = st.sidebar.number_input("Enter Strike Price")
expiration_date = st.sidebar.date_input("Select Expiration Date")
symbol = st.sidebar.selectbox("Select Underlying Symbol", ["NIFTY", "BANKNIFTY", "OTHER"])

if symbol == "OTHER":
    underlying_stock = st.sidebar.text_input("Enter Underlying Stock Symbol")
else:
    underlying_stock = symbol

import alpha_vantage.timeseries as av

# Set Alpha Vantage API key
av_api_key = "1VOMFY36F61VJZKC"

# Create an Alpha Vantage client
av_client = av.TimeSeries(key=av_api_key, output_format='pandas')

# Define a function to fetch options data from Alpha Vantage
def fetch_options_data(symbol, option_type, strike_price, expiration_date):
    params = {
        'function': 'OPTION_CHAINS',
        'symbol': symbol,
        'expiration': expiration_date.strftime('%Y-%m-%d'),
        'strike': strike_price,
        'option_type': option_type
    }
    response = av_client.get(params)
    return response
    
import pandas as pd
import yfinance as yf

# Define a function to process and analyze options data
def process_options_data(options_data):
    # Convert data to a Pandas DataFrame
    df = pd.DataFrame(options_data)
    
    # Calculate Greeks (Delta, Gamma, Theta, Vega)
    df['delta'] = df['call_delta'] if option_type == 'Call' else df['put_delta']
    df['gamma'] = df['call_gamma'] if option_type == 'Call' else df['put_gamma']
    df['theta'] = df['call_theta'] if option_type == 'Call' else df['put_theta']
    df['vega'] = df['call_vega'] if option_type == 'Call' else df['put_vega']
    
    # Add underlying stock price data
    stock_data = yf.download(underlying_stock, start=expiration_date, end=expiration_date)
    df['underlying_price'] = stock_data['Close'][0]
    
    # Calculate additional metrics (e.g., ROI, Breakeven Point)
    df['roi'] = (df['strike'] - df['underlying_price']) / df['strike']
    df['breakeven_point'] = df['strike'] + (df['strike'] * df['roi'])
    
    return df

# Create a Streamlit app
st.title("Indian Options Analytical Tool")

# Fetch options data from Alpha Vantage
options_data = fetch_options_data(underlying_stock, option_type, strike_price, expiration_date)

# Process and analyze options data
df = process_options_data(options_data)

# Display results
st.header("Options Data")
st.write(df)

st.header("Greeks and Metrics")
st.write(df[['delta', 'gamma', 'theta', 'vega', 'roi', 'breakeven_point']])

# Add a button to download data
@st.cache
def download_data(df):
    return df.to_csv(index=False)

download_button = st.button("Download Data")
if download_button:
    st.markdown(get_table_download_link(download_data(df)), unsafe_allow_html=True)

def get_table_download_link(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}" download="options_data.csv">Download CSV</a>'
    return href
