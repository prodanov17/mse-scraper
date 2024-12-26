import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.metrics import mean_squared_error, r2_score
import math
from tensorflow.keras.callbacks import EarlyStopping

def get_symbols():
    codes = []
    with open('../../shared/storage/codes.txt', 'r') as f:
        for line in f:
            codes.append(line.strip())
    return codes

# Ensure that a 'models' directory exists
if not os.path.exists('models'):
    os.makedirs('models')

# List of features you want to use
features = ['Close', 'RSI', 'Stoch_K', 'Stoch_D', 'WilliamsR', 'CCI', 'MFI', 'SMA', 'EMA', 'WMA']

symbols = get_symbols()

for symbol in symbols:
    print(f"Processing symbol: {symbol}")
    file_path = f"../indicators/{symbol}_oscillators_ma_1.csv"

    # ---------------------------
    # Step 1: Load and Prepare Data
    # ---------------------------
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"File for symbol {symbol} not found. Skipping.")
        continue

    # Ensure date and sort
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')
    df = df.set_index('Date')

    # Drop rows with missing values
    df = df.fillna(method='ffill').dropna()

    # Check if there are enough rows for processing
    if len(df) < 60 + 1:  # 60 sequence length + 1 future target
        print(f"Not enough data in {file_path}. Skipping.")
        continue

    # Check for missing features
    missing_features = [feat for feat in features if feat not in df.columns]
    if missing_features:
        print(f"Missing features {missing_features} for {file_path}. Skipping.")
        continue

    # Prepare data for scaling
    data = df[features].values
    if data.shape[0] == 0:
        print(f"No data available after preprocessing for {file_path}. Skipping.")
        continue

    # Scale the data
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data)

    # ---------------------------
    # Step 2: Create Sequences
    # ---------------------------
    sequence_length = 60
    future_target = 1  # predict 1 day ahead close price
    close_index = features.index('Close')

    X = []
    y = []
    for i in range(sequence_length, len(scaled_data)-future_target+1):
        X.append(scaled_data[i-sequence_length:i])
        y.append(scaled_data[i+future_target-1, close_index])

    X, y = np.array(X), np.array(y)

    if len(X) == 0:
        print(f"Not enough data for symbol {symbol} after processing. Skipping.")
        continue

    # ---------------------------
    # Step 3: Train/Validation Split
    # ---------------------------
    train_size = int(len(X) * 0.8)
    X_train, X_val = X[:train_size], X[train_size:]
    y_train, y_val = y[:train_size], y[train_size:]

    if len(X_val) == 0:
        print(f"No validation data available for symbol {symbol}. Skipping.")
        continue

    # ---------------------------
    # Step 4: Build the LSTM Model
    # ---------------------------
    model = Sequential()
    model.add(LSTM(64, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])))
    model.add(Dropout(0.2))
    model.add(LSTM(64))
    model.add(Dropout(0.2))
    model.add(Dense(1))

    model.compile(loss='mean_squared_error', optimizer='adam')

    # ---------------------------
    # Step 5: Train the Model
    # ---------------------------
    early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
    history = model.fit(X_train, y_train,
                        epochs=50,
                        batch_size=32,
                        validation_data=(X_val, y_val),
                        shuffle=False,
                        callbacks=[early_stopping],
                        verbose=1)

    # ---------------------------
    # Step 6: Evaluate the Model
    # ---------------------------
    y_pred = model.predict(X_val)

    # Inverse transform predictions and actual values
    inv_y_val = []
    inv_y_pred = []

    for i in range(len(y_val)):
        # Inverse transform the actual values
        dummy_val = np.zeros((1, len(features)))
        dummy_val[0, close_index] = y_val[i]
        val_unscaled = scaler.inverse_transform(dummy_val)[0, close_index]
        inv_y_val.append(val_unscaled)

        # Inverse transform the predicted values
        dummy_pred = np.zeros((1, len(features)))
        dummy_pred[0, close_index] = y_pred[i][0]  # Extract the scalar value
        pred_unscaled = scaler.inverse_transform(dummy_pred)[0, close_index]
        inv_y_pred.append(pred_unscaled)

    inv_y_val = np.array(inv_y_val)
    inv_y_pred = np.array(inv_y_pred)

    # Calculate RMSE and R^2
    rmse = math.sqrt(mean_squared_error(inv_y_val, inv_y_pred))
    r2 = r2_score(inv_y_val, inv_y_pred)

    print(f"{symbol} - RMSE on validation: {rmse}")
    print(f"{symbol} - R^2 on validation: {r2}")

    # ---------------------------
    # Step 7: Predicting Future Prices
    # ---------------------------
    last_60_days = scaled_data[-sequence_length:]
    last_60_days = last_60_days.reshape(1, sequence_length, len(features))

    predicted_price_scaled = model.predict(last_60_days)
    dummy_future = np.zeros((1, len(features)))
    dummy_future[0, close_index] = predicted_price_scaled
    predicted_price = scaler.inverse_transform(dummy_future)[0, close_index]

    print(f"{symbol} - Predicted price for next day: {predicted_price}")

    # ---------------------------
    # Save the model
    # ---------------------------
    model.save(f"models/{symbol}.h5")

    print(f"Model saved for {symbol}\n")
