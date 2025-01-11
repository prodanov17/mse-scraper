from datetime import datetime
import pandas as pd
from ta.momentum import RSIIndicator, StochasticOscillator, WilliamsRIndicator
from ta.trend import CCIIndicator, SMAIndicator, EMAIndicator, WMAIndicator
from ta.volume import MFIIndicator

# Function to read CSV files and format columns appropriately
def read_csv(filename) -> pd.DataFrame:
    df = pd.read_csv(filename)
    df['Date'] = pd.to_datetime(df['Date'], format='%d.%m.%Y')
    df = df.sort_values('Date')
    df = df.set_index('Date')
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
    s = s.replace('"', '')
    s = s.replace('.', '').replace(',', '.')
    return float(s)

# Function to save DataFrame to CSV file
def save(df: pd.DataFrame, filename: str):
    df_copy = df.reset_index()
    df_copy.to_csv(filename, index=False)

# Function to get a list of symbols from a file
def get_symbols():
    codes = []
    with open('../shared/storage/codes.txt', 'r') as f:
        for line in f:
            codes.append(line.strip())
    return codes

# ---------------------------
# RSI (Relative Strength Index)
# ---------------------------

def rsi(df: pd.DataFrame, rsi_period=14) -> pd.DataFrame:
    rsi_indicator = RSIIndicator(close=df['Close'], window=rsi_period)
    df['RSI'] = rsi_indicator.rsi()
    return df

def get_rsi_signal(rsi):
    if rsi < 30:
        return "BUY"
    elif rsi > 70:
        return "SELL"
    else:
        return "HOLD"

def rsi_indicator(df: pd.DataFrame) -> pd.DataFrame:
    df['RSI_Signal'] = df['RSI'].apply(get_rsi_signal)
    return df

# ---------------------------
# Stochastic Oscillator
# ---------------------------

def stochastic(df: pd.DataFrame, k_window=14, d_window=3, smooth_window=3) -> pd.DataFrame:
    stoch = StochasticOscillator(high=df['Max'], low=df['Min'], close=df['Close'],
                                 window=k_window, smooth_window=smooth_window)
    df['Stoch_K'] = stoch.stoch()
    df['Stoch_D'] = stoch.stoch_signal()
    return df

def get_stoch_signal(k):
    if k < 20:
        return "BUY"
    elif k > 80:
        return "SELL"
    else:
        return "HOLD"

def stochastic_indicator(df: pd.DataFrame) -> pd.DataFrame:
    df['Stoch_Signal'] = df['Stoch_K'].apply(get_stoch_signal)
    return df

# ---------------------------
# Williams %R
# ---------------------------

def williams_r(df: pd.DataFrame, lbp=14) -> pd.DataFrame:
    willr = WilliamsRIndicator(high=df['Max'], low=df['Min'], close=df['Close'], lbp=lbp)
    df['WilliamsR'] = willr.williams_r()
    return df

def get_willr_signal(wr):
    if wr < -80:
        return "BUY"
    elif wr > -20:
        return "SELL"
    else:
        return "HOLD"

def williams_r_indicator(df: pd.DataFrame) -> pd.DataFrame:
    df['WilliamsR_Signal'] = df['WilliamsR'].apply(get_willr_signal)
    return df

# ---------------------------
# CCI (Commodity Channel Index)
# ---------------------------

def cci(df: pd.DataFrame, cci_period=20) -> pd.DataFrame:
    cci_ind = CCIIndicator(high=df['Max'], low=df['Min'], close=df['Close'], window=cci_period)
    df['CCI'] = cci_ind.cci()
    return df

def get_cci_signal(cci_val):
    if cci_val < -100:
        return "BUY"
    elif cci_val > 100:
        return "SELL"
    else:
        return "HOLD"

def cci_indicator(df: pd.DataFrame) -> pd.DataFrame:
    df['CCI_Signal'] = df['CCI'].apply(get_cci_signal)
    return df

# ---------------------------
# MFI (Money Flow Index)
# ---------------------------

def mfi(df: pd.DataFrame, mfi_period=14) -> pd.DataFrame:
    mfi_ind = MFIIndicator(high=df['Max'], low=df['Min'], close=df['Close'], volume=df['Volume'], window=mfi_period)
    df['MFI'] = mfi_ind.money_flow_index()
    return df

def get_mfi_signal(mfi_val):
    if mfi_val < 20:
        return "BUY"
    elif mfi_val > 80:
        return "SELL"
    else:
        return "HOLD"

def mfi_indicator(df: pd.DataFrame) -> pd.DataFrame:
    df['MFI_Signal'] = df['MFI'].apply(get_mfi_signal)
    return df

# ---------------------------
# Moving Averages
# ---------------------------

def sma(df: pd.DataFrame, window=14) -> pd.DataFrame:
    sma_ind = SMAIndicator(close=df['Close'], window=window)
    df['SMA'] = sma_ind.sma_indicator()
    return df

def ema(df: pd.DataFrame, window=14) -> pd.DataFrame:
    ema_ind = EMAIndicator(close=df['Close'], window=window)
    df['EMA'] = ema_ind.ema_indicator()
    return df

def wma(df: pd.DataFrame, window=14) -> pd.DataFrame:
    wma_ind = WMAIndicator(close=df['Close'], window=window)
    df['WMA'] = wma_ind.wma()
    return df

def get_ma_signal(price, ma_value):
    if pd.isna(ma_value):
        return "HOLD"
    if price > ma_value:
        return "BUY"
    elif price < ma_value:
        return "SELL"
    else:
        return "HOLD"

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
        return df
    elif timeframe == 7:
        df_resampled = df.resample('7D').agg({
            'Close': 'last',
            'Max': 'max',
            'Min': 'min',
            'Volume': 'sum'
        }).dropna()
        return df_resampled
    elif timeframe == 30:
        df_resampled = df.resample('30D').agg({
            'Close': 'last',
            'Max': 'max',
            'Min': 'min',
            'Volume': 'sum'
        }).dropna()
        return df_resampled
    else:
        raise ValueError("Invalid timeframe specified.")

# ---------------------------
# Main Execution
# ---------------------------

if __name__ == '__main__':
    symbols = get_symbols()
    timeframes = [1, 7, 30]
    start_time = datetime.now()
    for symbol in symbols:
        df = read_csv(f"../shared/storage/{symbol}.csv")
        df = infer_close_price(df)

        for timeframe in timeframes:
            df_tf = resample_df(df, timeframe)

            # Apply oscillators
            df_tf = rsi(df_tf, rsi_period=14)
            df_tf = rsi_indicator(df_tf)

            df_tf = stochastic(df_tf, k_window=14, d_window=3, smooth_window=3)
            df_tf = stochastic_indicator(df_tf)

            df_tf = williams_r(df_tf, lbp=14)
            df_tf = williams_r_indicator(df_tf)

            df_tf = cci(df_tf, cci_period=20)
            df_tf = cci_indicator(df_tf)

            df_tf = mfi(df_tf, mfi_period=14)
            df_tf = mfi_indicator(df_tf)

            # Apply moving averages
            df_tf = sma(df_tf, window=14)
            df_tf = ema(df_tf, window=14)
            df_tf = wma(df_tf, window=14)

            df_tf = ma_indicators(df_tf)

            save(df_tf, filename=f"indicators/{symbol}_oscillators_ma_{timeframe}.csv")

    end_time = datetime.now()
    print(f"Total time taken: {(end_time - start_time).total_seconds()} seconds")
