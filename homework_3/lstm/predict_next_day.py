from flask import Flask, request, jsonify
import os
import math
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import load_model

# ---------------------------
# Configuration
# ---------------------------
sequence_length = 60
features = ['Close', 'RSI', 'Stoch_K', 'Stoch_D', 'WilliamsR', 'CCI', 'MFI', 'SMA', 'EMA', 'WMA']
close_index = features.index('Close')

app = Flask(__name__)

def predict_next_day(symbol):
    model_path = f"models/{symbol}.h5"
    data_path = f"../indicators/{symbol}_oscillators_ma_1.csv"

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"No model found for symbol {symbol} at {model_path}.")

    if not os.path.exists(data_path):
        raise FileNotFoundError(f"No data file found for symbol {symbol} at {data_path}.")

    model = load_model(model_path)

    df = pd.read_csv(data_path)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')
    df = df.set_index('Date')

    for feat in features:
        if feat not in df.columns:
            raise ValueError(f"Feature {feat} not found in {data_path}")

    df = df.fillna(method='ffill').dropna()

    if len(df) < sequence_length:
        raise ValueError(f"Not enough data to generate a {sequence_length}-day sequence for {symbol}.")

    data = df[features].values

    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data)

    last_sequence = scaled_data[-sequence_length:].reshape(1, sequence_length, len(features))

    predicted_price_scaled = model.predict(last_sequence)

    dummy_future = np.zeros((1, len(features)))
    dummy_future[0, close_index] = predicted_price_scaled
    predicted_price = scaler.inverse_transform(dummy_future)[0, close_index]

    return predicted_price

@app.route('/predict', methods=['GET'])
def predict():
    symbol = request.args.get('symbol')
    if not symbol:
        return jsonify({"error": "Symbol parameter is required."}), 400

    try:
        prediction = predict_next_day(symbol)
        return jsonify({"symbol": symbol, "predicted_price": prediction}), 200
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred.", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5002)
