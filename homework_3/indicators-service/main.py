import os
import pandas as pd
from flask import Flask, jsonify, request

app = Flask(__name__)

# Define column mappings for each indicator (for output renaming)
INDICATOR_COLUMNS = {
    "rsi": ["Date", "Close", "Max", "Min", "Volume", "RSI", "RSI_Signal"],
    "stoch": ["Date", "Close", "Max", "Min", "Volume", "Stoch_K", "Stoch_D", "Stoch_Signal"],
    "williamsr": ["Date", "Close", "Max", "Min", "Volume", "WilliamsR", "WilliamsR_Signal"],
    "cci": ["Date", "Close", "Max", "Min", "Volume", "CCI", "CCI_Signal"],
    "mfi": ["Date", "Close", "Max", "Min", "Volume", "MFI", "MFI_Signal"]
}


# Helper function to read and filter data for a specific issuer, indicator, and frequency
def get_filtered_data(issuer, indicator, frequency=None, limit=None, offset=None):
    # Correct the path to move one directory up and go into /indicators
    folder_path = os.path.join(os.path.dirname(os.getcwd()),
                               "indicators")  # Go one directory up from /indicators_service
    indicator_columns = INDICATOR_COLUMNS.get(indicator.lower())

    if not indicator_columns:
        raise ValueError(f"Invalid indicator '{indicator}'")

    result = []
    for filename in os.listdir(folder_path):
        # Check if the file matches the issuer and ends with .csv
        if filename.startswith(issuer + "_") and filename.endswith(".csv"):
            # Extract the frequency from the filename
            file_frequency = filename.split("_")[-1].replace(".csv", "")
            if frequency and file_frequency != frequency:
                continue  # Skip files that do not match the requested frequency

            file_path = os.path.join(folder_path, filename)
            try:
                # Read the CSV file and filter columns
                df = pd.read_csv(file_path)
                print(f"Original columns in file '{filename}': {df.columns}")  # Debug: Check original columns

                # Filter columns for the indicator
                df = df[[col for col in df.columns if col in indicator_columns]]
                print(f"Filtered columns in file '{filename}': {df.columns}")  # Debug: Check filtered columns

                df["file"] = filename  # Add the filename for context

                # Rename columns for output to generic names
                if indicator == "rsi":
                    df = df.rename(columns={"RSI": "Indicator", "RSI_Signal": "Signal"})
                elif indicator == "stoch":
                    df = df.rename(columns={
                        "Stoch_K": "Indicator",
                        "Stoch_D": "Signal",  # Renaming Stoch_D to Signal
                        "Stoch_Signal": "Signal"  # Renaming Stoch_Signal to Signal
                    })
                elif indicator == "williamsr":
                    df = df.rename(columns={"WilliamsR": "Indicator", "WilliamsR_Signal": "Signal"})
                elif indicator == "cci":
                    df = df.rename(columns={"CCI": "Indicator", "CCI_Signal": "Signal"})
                elif indicator == "mfi":
                    df = df.rename(columns={"MFI": "Indicator", "MFI_Signal": "Signal"})

                print(f"Renamed columns in file '{filename}': {df.columns}")  # Debug: Check renamed columns

                # Replace NaN values with None (to return actual JSON null)
                df = df.where(pd.notnull(df), None)

                result.extend(df.to_dict(orient="records"))
            except Exception as e:
                raise ValueError(f"Error reading file '{filename}': {e}")

    # Apply pagination (limit and offset)
    if limit is not None:
        result = result[offset:offset + limit]

    return result


# Define the endpoint with dynamic route parameters
@app.route("/<string:issuer>/indicators/<string:indicator>", methods=["GET"])
def get_indicator_values(issuer, indicator):
    try:
        # Extract the frequency query parameter (optional)
        frequency = request.args.get("frequency")
        if frequency and not frequency.isdigit():
            return jsonify({"error": "Frequency must be a numeric value"}), 400

        # Extract pagination query parameters (optional)
        page = request.args.get("page", default=1, type=int)  # Default page is 1
        limit = request.args.get("limit", default=10, type=int)  # Default limit is 10

        # Calculate the offset based on the page number
        offset = (page - 1) * limit

        # Extract values for the specified issuer, indicator, and frequency
        data = get_filtered_data(issuer, indicator, frequency, limit, offset)
        if not data:
            return jsonify({
                "error": f"No data found for indicator '{indicator}' for issuer '{issuer}' with frequency '{frequency}'"}), 404
        return jsonify(data)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = os.getenv("PORT", 5000)
    app.run(debug=True, host='0.0.0.0', port=port)
