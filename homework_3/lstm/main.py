import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.metrics import mean_squared_error, r2_score
import math
from tensorflow.keras.callbacks import EarlyStopping

# Function to load the list of symbols from a file
def get_symbols():
    codes = []
    with open('../../shared/storage/codes.txt', 'r') as f:
        for line in f:
            codes.append(line.strip())  # Remove newline characters
    return codes

# Ensure that a 'models' directory exists to save trained models
if not os.path.exists('models'):
    os.makedirs('models')

# List of features to use for model training
features = ['Close', 'RSI', 'Stoch_K', 'Stoch_D', 'WilliamsR', 'CCI', 'MFI', 'SMA', 'EMA', 'WMA']

# Load symbols from the file
symbols = get_symbols()

# Loop through each symbol and process the corresponding data
for symbol in symbols:
    print(f"Processing symbol: {symbol}")
    file_path = f"../indicators/{symbol}_oscillators_ma_1.csv"

    # ---------------------------
    # Step 1: Load and Prepare Data
    # ---------------------------
    try:
        df = pd.read_csv(file_path)  # Read the CSV file containing data
    except FileNotFoundError:
        print(f"File for symbol {symbol} not found. Skipping.")
        continue

    # Convert the 'Date' column to datetime format and sort the data
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')
    df = df.set_index('Date')  # Set 'Date' as the index of the DataFrame

    # Fill missing values using forward fill and drop any remaining NaNs
    df = df.fillna(method='ffill').dropna()

    # Ensure that there is enough data (at least 60 rows for sequence and 1 for target)
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

    # Scale the data using MinMaxScaler to normalize the values
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data)

    # ---------------------------
    # Step 2: Create Sequences for LSTM
    # ---------------------------
    sequence_length = 60  # Length of the sequence used for input to the LSTM
    future_target = 1  # Predict the close price 1 day ahead
    close_index = features.index('Close')  # Index of the 'Close' feature

    X = []  # Input sequences for LSTM
    y = []  # Corresponding target values for prediction

    # Create sequences of length 'sequence_length' and corresponding target values
    for i in range(sequence_length, len(scaled_data)-future_target+1):
        X.append(scaled_data[i-sequence_length:i])  # Sequence of data for X
        y.append(scaled_data[i+future_target-1, close_index])  # Close price for the target

    X, y = np.array(X), np.array(y)

    # Ensure there is enough data after processing
    if len(X) == 0:
        print(f"Not enough data for symbol {symbol} after processing. Skipping.")
        continue

    # ---------------------------
    # Step 3: Train/Validation Split
    # ---------------------------
    train_size = int(len(X) * 0.8)  # 80% of data for training, 20% for validation
    X_train, X_val = X[:train_size], X[train_size:]  # Split data
    y_train, y_val = y[:train_size], y[train_size:]  # Split targets

    # Ensure there is validation data
    if len(X_val) == 0:
        print(f"No validation data available for symbol {symbol}. Skipping.")
        continue

    # ---------------------------
    # Step 4: Build the LSTM Model
    # ---------------------------
    model = Sequential()
    model.add(LSTM(64, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])))  # LSTM layer
    model.add(Dropout(0.2))  # Dropout layer to prevent overfitting
    model.add(LSTM(64))  # Another LSTM layer
    model.add(Dropout(0.2))  # Dropout layer
    model.add(Dense(1))  # Dense layer for output (predicting close price)

    # Compile the model with mean squared error loss and Adam optimizer
    model.compile(loss='mean_squared_error', optimizer='adam')

    # ---------------------------
    # Step 5: Train the Model
    # ---------------------------
    early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)  # Early stopping callback
    history = model.fit(X_train, y_train,
                        epochs=50,
                        batch_size=32,
                        validation_data=(X_val, y_val),
                        shuffle=False,
                        callbacks=[early_stopping],  # Apply early stopping
                        verbose=1)

    # ---------------------------
    # Step 6: Evaluate the Model
    # ---------------------------
    y_pred = model.predict(X_val)  # Make predictions on the validation data

    # Inverse transform the scaled predictions and actual values back to the original scale
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

    # Calculate RMSE (Root Mean Squared Error) and R-squared metrics
    rmse = math.sqrt(mean_squared_error(inv_y_val, inv_y_pred))
    r2 = r2_score(inv_y_val, inv_y_pred)

    print(f"{symbol} - RMSE on validation: {rmse}")
    print(f"{symbol} - R^2 on validation: {r2}")

    # ---------------------------
    # Step 7: Predict Future Prices
    # ---------------------------
    last_60_days = scaled_data[-sequence_length:]  # Get the last 60 days of data
    last_60_days = last_60_days.reshape(1, sequence_length, len(features))  # Reshape for LSTM input

    predicted_price_scaled = model.predict(last_60_days)  # Predict the next day's price
    dummy_future = np.zeros((1, len(features)))
    dummy_future[0, close_index] = predicted_price_scaled
    predicted_price = scaler.inverse_transform(dummy_future)[0, close_index]  # Inverse transform to original scale

    print(f"{symbol} - Predicted price for next day: {predicted_price}")

    # ---------------------------
    # Save the trained model
    # ---------------------------
    model.save(f"models/{symbol}.h5")  # Save the model for the symbol

    print(f"Model saved for {symbol}\n")
