import os
import pandas as pd
from flask import Flask, jsonify, request

# Initialize Flask application
app = Flask(__name__)

# Define column mappings for each indicator
INDICATOR_COLUMNS = {
    "rsi": ["Date", "Close", "Max", "Min", "Volume", "RSI", "RSI_Signal"],
    "stoch": ["Date", "Close", "Max", "Min", "Volume", "Stoch_K", "Stoch_Signal"],
    "williamsr": ["Date", "Close", "Max", "Min", "Volume", "WilliamsR", "WilliamsR_Signal"],
    "cci": ["Date", "Close", "Max", "Min", "Volume", "CCI", "CCI_Signal"],
    "mfi": ["Date", "Close", "Max", "Min", "Volume", "MFI", "MFI_Signal"],
    "ema": ["Date", "Close", "Max", "Min", "Volume", "EMA", "EMA_Signal"],
    "sma": ["Date", "Close", "Max", "Min", "Volume", "SMA", "SMA_Signal"],
    "wma": ["Date", "Close", "Max", "Min", "Volume", "WMA", "WMA_Signal"],
}

# Helper function to read and filter data for a specific issuer, indicator, and frequency
def get_filtered_data(issuer, indicator, frequency=None, limit=None, offset=None):
    """
    Function to get data by indicator and frequency
    :param issuer: company key
    :param indicator: indicator type (rsi, stoch, williamsr, ema, sma, wma)
    :param frequency: (1,7,30)
    :param limit: limits results
    :param offset: offsets results
    :return: list of data
    """
    folder_path = os.path.join(os.getcwd(), "indicators")  # Path to the folder with data files
    indicator_columns = INDICATOR_COLUMNS.get(indicator.lower())  # Get the column names based on the indicator

    # Check if the indicator is valid
    if not indicator_columns:
        raise ValueError(f"Invalid indicator '{indicator}'")

    result = []
    for filename in os.listdir(folder_path):  # Loop through files in the folder
        # Only read files with "_oscillators_ma_" in the name
        if "_oscillators_ma_" not in filename:
            continue

        # Check if the file corresponds to the specified issuer and ends with ".csv"
        if filename.startswith(issuer + "_") and filename.endswith(".csv"):
            file_frequency = filename.split("_")[-1].replace(".csv", "")  # Get frequency from filename
            if frequency and file_frequency != frequency:  # Filter by frequency if provided
                continue

            file_path = os.path.join(folder_path, filename)  # Get the full path of the file
            try:
                df = pd.read_csv(file_path)  # Read the CSV file into a DataFrame

                #reverse the df
                df = df[::-1]

                # Ensure required columns are present in the file
                missing_columns = [col for col in indicator_columns if col not in df.columns]
                if missing_columns:
                    raise ValueError(f"Columns {missing_columns} not found in file '{filename}'")

                # Filter columns for the indicator
                df = df[indicator_columns]

                # Rename columns for output to a consistent format based on the indicator
                if indicator == "rsi":
                    df = df.rename(columns={"RSI": "indicator", "RSI_Signal": "signal"})
                elif indicator == "stoch":
                    df = df.rename(columns={"Stoch_K": "indicator", "Stoch_Signal": "signal"})
                elif indicator == "williamsr":
                    df = df.rename(columns={"WilliamsR": "indicator", "WilliamsR_Signal": "signal"})
                elif indicator == "cci":
                    df = df.rename(columns={"CCI": "indicator", "CCI_Signal": "signal"})
                elif indicator == "mfi":
                    df = df.rename(columns={"MFI": "indicator", "MFI_Signal": "signal"})
                elif indicator == "ema":
                    df = df.rename(columns={"EMA": "indicator", "EMA_Signal": "signal"})
                elif indicator == "sma":
                    df = df.rename(columns={"SMA": "indicator", "SMA_Signal": "signal"})
                elif indicator == "wma":
                    df = df.rename(columns={"WMA": "indicator", "WMA_Signal": "signal"})

                # Replace NaN values with None (null in JSON) for proper JSON serialization
                df = df.replace([float('nan'), float('inf'), float('-inf')], None)

                # Convert column names to lowercase for consistent output
                df.columns = [col.lower() for col in df.columns]


                # Add rows to the result list
                result.extend(df.to_dict(orient="records"))
            except Exception as e:
                # Handle any errors encountered while reading the file
                raise ValueError(f"Error reading file '{filename}': {e}")

    # Apply pagination (limit and offset) to the result set
    if limit is not None:
        result = result[offset:offset + limit]

    return result


# Define the endpoint with dynamic route parameters to retrieve indicator values
@app.route("/<string:issuer>/indicators/<string:indicator>", methods=["GET"])
def get_indicator_values(issuer, indicator):
    """
    Route for getting data by indicator and frequency
    :param issuer: company key
    :param indicator: rsi, stoch, williamsr, ema, sma, wma
    :return: json
    """
    try:
        # Extract frequency query parameter (optional)
        frequency = request.args.get("frequency")
        if frequency and not frequency.isdigit():
            return jsonify({"error": "Frequency must be a numeric value"}), 400  # Handle invalid frequency input

        # Extract pagination query parameters (optional)
        page = request.args.get("page", default=1, type=int)
        limit = request.args.get("limit", default=10, type=int)

        # Calculate the offset for pagination
        offset = (page - 1) * limit

        # Extract data for the specified issuer, indicator, and frequency
        data = get_filtered_data(issuer, indicator, frequency, limit, offset)
        if not data:
            return jsonify({"error": f"No data found for indicator '{indicator}' for issuer '{issuer}' with frequency '{frequency}'"}), 404
        return jsonify(data)  # Return the filtered data as JSON response
    except ValueError as e:
        # Handle validation errors
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        # Handle general errors
        return jsonify({"error": str(e)}), 500


# Start the Flask application
if __name__ == "__main__":
    port = os.getenv("PORT", 5000)  # Get port from environment variable or default to 5000
    app.run(debug=True, host="0.0.0.0", port=port)  # Run the app in debug mode
