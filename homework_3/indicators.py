from datetime import datetime
import pandas as pd
from ta.momentum import RSIIndicator, StochasticOscillator, WilliamsRIndicator
from ta.trend import CCIIndicator, SMAIndicator, EMAIndicator, WMAIndicator
from ta.volume import MFIIndicator

# Function to read CSV files and format columns appropriately
def read_csv(filename) -> pd.DataFrame:
    df = pd.read_csv(filename)
    df['Date'] = pd.to_datetime(df['Date'], format='%d.%m.%Y')  # Parse the Date column
    df = df.sort_values('Date')  # Sort values by Date
    df = df.set_index('Date')  # Set Date as the index
    return df

# Function to convert price columns from strings to floats
def infer_close_price(df: pd.DataFrame) -> pd.DataFrame:
    df['Last trade price'] = df['Last trade price'].apply(price_str_to_float)
    df['Close'] = df['Last trade price']
    df['Max'] = df['Max'].apply(price_str_to_float)
    df['Min'] = df['Min'].apply(price_str_to_float)
    df['Volume'] = df['Volume'].apply(lambda x: float(str(x).replace('.', '').replace(',', '.')))
    return df

# Helper function to convert price string to float
def price_str_to_float(s):
    s = s.replace('"', '')  # Remove quotation marks
    s = s.replace('.', '').replace(',', '.')  # Replace commas and periods
    return float(s)

# Function to save DataFrame to CSV file
def save(df: pd.DataFrame, filename: str):
    df_copy = df.reset_index()  # Reset the index before saving
    df_copy.to_csv(filename, index=False)  # Save DataFrame to CSV

# Function to get a list of symbols from a file
def get_symbols():
    codes = []
    with open('../shared/storage/codes.txt', 'r') as f:  # Open the file with stock symbols
        for line in f:
            codes.append(line.strip())  # Add symbols to the list
    return codes

# ---------------------------
# RSI (Relative Strength Index)
# ---------------------------

def rsi(df: pd.DataFrame, rsi_period=14) -> pd.DataFrame:
    rsi_indicator = RSIIndicator(close=df['Close'], window=rsi_period)
    df['RSI'] = rsi_indicator.rsi()  # Compute RSI values
    return df

def get_rsi_signal(rsi):
    if rsi < 30:
        return "BUY"  # Signal to buy
    elif rsi > 70:
        return "SELL"  # Signal to sell
    else:
        return "HOLD"  # Signal to hold

def rsi_indicator(df: pd.DataFrame) -> pd.DataFrame:
    df['RSI_Signal'] = df['RSI'].apply(get_rsi_signal)  # Get signals based on RSI values
    return df

# ---------------------------
# Stochastic Oscillator
# ---------------------------

def stochastic(df: pd.DataFrame, k_window=14, d_window=3, smooth_window=3) -> pd.DataFrame:
    stoch = StochasticOscillator(high=df['Max'], low=df['Min'], close=df['Close'],
                                 window=k_window, smooth_window=smooth_window)
    df['Stoch_K'] = stoch.stoch()  # Compute Stochastic %K values
    df['Stoch_D'] = stoch.stoch_signal()  # Compute Stochastic %D values
    return df

def get_stoch_signal(k):
    if k < 20:
        return "BUY"  # Signal to buy
    elif k > 80:
        return "SELL"  # Signal to sell
    else:
        return "HOLD"  # Signal to hold

def stochastic_indicator(df: pd.DataFrame) -> pd.DataFrame:
    df['Stoch_Signal'] = df['Stoch_K'].apply(get_stoch_signal)  # Get signals based on Stochastic %K values
    return df

# ---------------------------
# Williams %R
# ---------------------------

def williams_r(df: pd.DataFrame, lbp=14) -> pd.DataFrame:
    willr = WilliamsRIndicator(high=df['Max'], low=df['Min'], close=df['Close'], lbp=lbp)
    df['WilliamsR'] = willr.williams_r()  # Compute Williams %R values
    return df

def get_willr_signal(wr):
    if wr < -80:
        return "BUY"  # Signal to buy
    elif wr > -20:
        return "SELL"  # Signal to sell
    else:
        return "HOLD"  # Signal to hold

def williams_r_indicator(df: pd.DataFrame) -> pd.DataFrame:
    df['WilliamsR_Signal'] = df['WilliamsR'].apply(get_willr_signal)  # Get signals based on Williams %R values
    return df

# ---------------------------
# CCI (Commodity Channel Index)
# ---------------------------

def cci(df: pd.DataFrame, cci_period=20) -> pd.DataFrame:
    cci_ind = CCIIndicator(high=df['Max'], low=df['Min'], close=df['Close'], window=cci_period)
    df['CCI'] = cci_ind.cci()  # Compute CCI values
    return df

def get_cci_signal(cci_val):
    if cci_val < -100:
        return "BUY"  # Signal to buy
    elif cci_val > 100:
        return "SELL"  # Signal to sell
    else:
        return "HOLD"  # Signal to hold

def cci_indicator(df: pd.DataFrame) -> pd.DataFrame:
    df['CCI_Signal'] = df['CCI'].apply(get_cci_signal)  # Get signals based on CCI values
    return df

# ---------------------------
# MFI (Money Flow Index)
# ---------------------------

def mfi(df: pd.DataFrame, mfi_period=14) -> pd.DataFrame:
    mfi_ind = MFIIndicator(high=df['Max'], low=df['Min'], close=df['Close'], volume=df['Volume'], window=mfi_period)
    df['MFI'] = mfi_ind.money_flow_index()  # Compute MFI values
    return df

def get_mfi_signal(mfi_val):
    if mfi_val < 20:
        return "BUY"  # Signal to buy
    elif mfi_val > 80:
        return "SELL"  # Signal to sell
    else:
        return "HOLD"  # Signal to hold

def mfi_indicator(df: pd.DataFrame) -> pd.DataFrame:
    df['MFI_Signal'] = df['MFI'].apply(get_mfi_signal)  # Get signals based on MFI values
    return df

# ---------------------------
# Moving Averages
# ---------------------------

def sma(df: pd.DataFrame, window=14) -> pd.DataFrame:
    sma_ind = SMAIndicator(close=df['Close'], window=window)
    df['SMA'] = sma_ind.sma_indicator()  # Compute Simple Moving Average (SMA)
    return df

def ema(df: pd.DataFrame, window=14) -> pd.DataFrame:
    ema_ind = EMAIndicator(close=df['Close'], window=window)
    df['EMA'] = ema_ind.ema_indicator()  # Compute Exponential Moving Average (EMA)
    return df

def wma(df: pd.DataFrame, window=14) -> pd.DataFrame:
    wma_ind = WMAIndicator(close=df['Close'], window=window)
    df['WMA'] = wma_ind.wma()  # Compute Weighted Moving Average (WMA)
    return df

def get_ma_signal(price, ma_value):
    if pd.isna(ma_value):
        return "HOLD"  # Hold if moving average is NaN
    if price > ma_value:
        return "BUY"  # Signal to buy
    elif price < ma_value:
        return "SELL"  # Signal to sell
    else:
        return "HOLD"  # Signal to hold

def ma_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df['SMA_Signal'] = df.apply(lambda row: get_ma_signal(row['Close'], row['SMA']), axis=1)
    df['EMA_Signal'] = df.apply(lambda row: get_ma_signal(row['Close'], row['EMA']), axis=1)
    df['WMA_Signal'] = df.apply(lambda row: get_ma_signal(row['Close'], row['WMA']), axis=1)
    return df

# ---------------------------
# Resampling DataFrame
# ---------------------------

def resample_df(df: pd.DataFrame, timeframe: int) -> pd.DataFrame:
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError("DataFrame index must be a DatetimeIndex before resampling.")

    if timeframe == 1:
        return df  # Return the original DataFrame
    elif timeframe == 7:
        df_resampled = df.resample('7D').agg({
            'Close': 'last',
            'Max': 'max',
            'Min': 'min',
            'Volume': 'sum'
        }).dropna()  # Resample data with a 7-day timeframe
        return df_resampled
    elif timeframe == 30:
        df_resampled = df.resample('30D').agg({
            'Close': 'last',
            'Max': 'max',
            'Min': 'min',
            'Volume': 'sum'
        }).dropna()  # Resample data with a 30-day timeframe
        return df_resampled
    else:
        raise ValueError("Invalid timeframe specified.")  # Raise error for invalid timeframe

# ---------------------------
# Main Execution
# ---------------------------

if __name__ == '__main__':
    symbols = get_symbols()  # Get list of symbols from file
    timeframes = [1, 7, 30]  # Define timeframes for resampling
    start_time = datetime.now()  # Start execution time

    for symbol in symbols:
        df = read_csv(f"../shared/storage/{symbol}.csv")  # Read CSV for each symbol
        df = infer_close_price(df)  # Process price columns

        for timeframe in timeframes:
            df_resampled = resample_df(df, timeframe)  # Resample data based on timeframe
            df_resampled = rsi(df_resampled)  # Apply RSI indicator
            df_resampled = rsi_indicator(df_resampled)  # Apply RSI signal
            df_resampled = stochastic(df_resampled)  # Apply Stochastic Oscillator
            df_resampled = stochastic_indicator(df_resampled)  # Apply Stochastic signal
            df_resampled = williams_r(df_resampled)  # Apply Williams %R
            df_resampled = williams_r_indicator(df_resampled)  # Apply Williams %R signal
            df_resampled = cci(df_resampled)  # Apply CCI
            df_resampled = cci_indicator(df_resampled)  # Apply CCI signal
            df_resampled = mfi(df_resampled)  # Apply MFI
            df_resampled = mfi_indicator(df_resampled)  # Apply MFI signal
            df_resampled = sma(df_resampled)  # Apply SMA
            df_resampled = ema(df_resampled)  # Apply EMA
            df_resampled = wma(df_resampled)  # Apply WMA
            df_resampled = ma_indicators(df_resampled)  # Apply Moving Average signals

            save(df_resampled, f"../shared/storage/{symbol}_resampled_{timeframe}.csv")  # Save resampled data

    print(f"Execution completed in {datetime.now() - start_time}")  # Print total execution time
