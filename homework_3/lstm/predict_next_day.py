from flask import Flask, request, jsonify
import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import load_model

# ---------------------------
# Configuration
# ---------------------------
sequence_length = 60  # Length of the sequence used for prediction (60 days)
features = ['Close', 'RSI', 'Stoch_K', 'Stoch_D', 'WilliamsR', 'CCI', 'MFI', 'SMA', 'EMA', 'WMA']  # Features used for prediction
close_index = features.index('Close')  # Index of the 'Close' feature

# Initialize Flask app
app = Flask(__name__)

# Function to predict the next day's price for a given symbol
def predict_next_day(symbol):
    model_path = f"models/{symbol}.h5"  # Path to the trained model for the symbol
    data_path = f"../indicators/{symbol}_oscillators_ma_1.csv"  # Path to the CSV data for the symbol

    # Check if model file exists
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"No model found for symbol {symbol} at {model_path}.")

    # Check if data file exists
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"No data file found for symbol {symbol} at {data_path}.")

    # Load the trained model
    model = load_model(model_path)

    # Load the data for the symbol
    df = pd.read_csv(data_path)
    df['Date'] = pd.to_datetime(df['Date'])  # Convert 'Date' column to datetime
    df = df.sort_values('Date')  # Sort the data by date
    df = df.set_index('Date')  # Set 'Date' as the index of the DataFrame

    # Check if all required features are present in the data
    for feat in features:
        if feat not in df.columns:
            raise ValueError(f"Feature {feat} not found in {data_path}")

    # Preprocess the data: fill missing values and drop rows with NaN values
    df = df.fillna(method='ffill').dropna()

    # Ensure that there is enough data for generating sequences
    if len(df) < sequence_length:
        raise ValueError(f"Not enough data to generate a {sequence_length}-day sequence for {symbol}.")

    # Extract the values for the features and scale them
    data = df[features].values
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data)

    # Prepare the last sequence of data for prediction
    last_sequence = scaled_data[-sequence_length:].reshape(1, sequence_length, len(features))

    # Predict the scaled price using the trained model
    predicted_price_scaled = model.predict(last_sequence)

    # Reverse the scaling to obtain the actual predicted price
    dummy_future = np.zeros((1, len(features)))
    dummy_future[0, close_index] = predicted_price_scaled
    predicted_price = scaler.inverse_transform(dummy_future)[0, close_index]

    # Return the predicted price
    return predicted_price

# Flask route for predicting the next day's price
@app.route('/predict', methods=['GET'])
def predict():
    symbol = request.args.get('symbol')  # Get the symbol parameter from the request
    if not symbol:
        return jsonify({"error": "Symbol parameter is required."}), 400  # Return error if symbol is not provided

    try:
        # Call the predict_next_day function to get the predicted price
        prediction = predict_next_day(symbol)
        return jsonify({"symbol": symbol, "predicted_price": prediction}), 200  # Return the prediction in JSON format
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404  # Handle file not found error
    except ValueError as e:
        return jsonify({"error": str(e)}), 400  # Handle missing feature or insufficient data error
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred.", "details": str(e)}), 500  # Handle unexpected errors

# Start the Flask app
if __name__ == '__main__':
    port = os.getenv("PORT", 5000)
    app.run(debug=True, host='0.0.0.0', port=port)
