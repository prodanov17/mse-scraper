import re
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import pandas as pd
import concurrent.futures
import os
import requests
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv()

# Database connection string from .env
DATABASE_URL = os.getenv("DATABASE_URL")  # Example: "mysql+pymysql://user:password@localhost/db_name"

# Define column names
columns = ['company_key', 'Date', 'Last trade price', 'Max', 'Min', 'Avg.', 'Price %chg.', 'Volume', 'Turnover in BEST in denars',
           'Total turnover in denars']

db_cols = ['company_key', 'date', 'price', 'max', 'min', 'average_price', 'price_change', 'volume', 'best_turnover', 'total_turnover']

# Set up the base URL and number of years
base_url = "https://www.mse.mk/en/stats/symbolhistory/"
years = 10


def is_leap_year(year):
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def has_numbers(inputString):
    return bool(re.search(r'\d', inputString))


def get_symbols():
    url = "https://www.mse.mk/en/stats/symbolhistory/REPL"
    response = requests.get(url)

    soup = BeautifulSoup(response.text, 'html.parser')
    codes = soup.select('#Code > option')
    code_list = [code['value'] for code in codes if not has_numbers(code['value'])]

    return code_list


def retrieve_data_for_period(code, start_date, end_date):  # Filter 3
    if start_date > end_date:
        raise ValueError("start_date must be less than end_date")
    if end_date - start_date > timedelta(days=365):
        raise ValueError("end_date must be greater than start date")
    url = base_url + code

    data = requests.post(url,
                         json={'FromDate': start_date.strftime('%m/%d/%Y'), 'ToDate': end_date.strftime('%m/%d/%Y')})

    # Parse the HTML and extract the table rows
    soup = BeautifulSoup(data.text, 'html.parser')
    rows = soup.select("#resultsTable tbody tr")

    # Collect the data
    period_data = []
    for row in rows:
        cells = row.find_all("td")
        row_data = [code] + [cell.get_text(strip=True) for cell in cells]  # Include `company_key` as the first value
        period_data.append(row_data)

    print(f"Retrieved data for {code} from {start_date} to {end_date}")
    return period_data


def process_data_frame(df):
    # Change date format to 'yyyy-mm-dd'
    df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y').dt.strftime('%Y-%m-%d')

    # Replace commas in price columns
    price_columns = ['Last trade price', 'Max', 'Min', 'Avg.', 'Price %chg.', 'Turnover in BEST in denars',
                     'Total turnover in denars']
    for col in price_columns:
        df[col] = df[col].str.replace(',', '')
    df = df[df['Volume'] != '0']
    df = df.dropna(subset=['company_key', 'Date'])


    return df


def safe_float_conversion(value):
    """
    Safely convert a string with commas to a float.
    If the value is an empty string or None, return None.
    """
    try:
        return float(value.replace(',', '')) if value else None
    except ValueError:
        print(f"Error converting value to float: {value}")
        return None

def insert_data_to_db(df):
    engine = create_engine(DATABASE_URL, isolation_level="AUTOCOMMIT")

    db_cols = [
        "company_key", "date", "price", "max", "min",
        "average_price", "price_change", "volume",
        "best_turnover", "total_turnover"
    ]

    # Prepare the list of parameter dictionaries for bulk insert
    bulk_params = []
    for _, row in df.iterrows():
        # Skip rows with missing required data
        if not row["company_key"] or not row["Date"]:
            print(f"Skipping row with missing data: {row}")
            continue

        params = {
            "company_key": row["company_key"].strip(),
            "date": row["Date"],
            "price": safe_float_conversion(row["Last trade price"]),
            "max": safe_float_conversion(row["Max"]),
            "min": safe_float_conversion(row["Min"]),
            "average_price": safe_float_conversion(row["Avg."]),
            "price_change": safe_float_conversion(row["Price %chg."]),
            "volume": safe_float_conversion(row["Volume"]),
            "best_turnover": safe_float_conversion(row["Turnover in BEST in denars"]),
            "total_turnover": safe_float_conversion(row["Total turnover in denars"]),
        }

        bulk_params.append(params)

    if not bulk_params:
        print("No data to insert.")
        return

    # Execute the bulk insert in a single transaction
    with engine.connect() as connection:
        try:
            query = text(f"""
                INSERT INTO stock_data ({", ".join(db_cols)})
                VALUES (:company_key, :date, :price, :max, :min, :average_price, :price_change, :volume, :best_turnover, :total_turnover);
            """)
            print(query)
            print(bulk_params)
            connection.execute(query, bulk_params)  # Execute bulk insert
            print(f"Successfully inserted {len(bulk_params)} rows.")
        except Exception as e:
            print("Failed to insert bulk data.")
            print(f"Error: {e}")




def read_latest_dates_from_db():
    """
    Retrieve the latest date for each company_key from the database and return as a dictionary.
    """
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        result = connection.execute(text("SELECT company_key, MAX(date) AS latest_date FROM stock_data GROUP BY company_key"))
        scores = list(result)  # Convert the iterator into a list
        print(f"Retrieved {len(scores)} latest dates from the database.")
        print(scores)
        # Use the list to build the dictionary
        latest_dates = {row[0]: row[1] for row in scores}

    return latest_dates



def retrieve_data_for_code(code, latest_dates, years=5):
    """
    Retrieve data for a specific code, considering the latest date available in the database.
    """
    all_data = []
    exists = False
    start_date = datetime.now()
    leap_years_count = sum(is_leap_year(start_date.year - i) for i in range(years))

    # Check the latest date for the code
    latest_date = latest_dates.get(code) 

    if latest_date is not None:
        print(f"Latest date for {code} is {latest_date}")
        exists = True
        latest_date = datetime.strptime(latest_date, '%Y-%m-%d')
        start_date = latest_date + timedelta(days=1)
        end_date = datetime.now()
        period_data = retrieve_data_for_period(code, start_date, end_date)
        all_data.extend(period_data)
    else:
        for i in range(years):
            end_date = start_date
            start_date = end_date - timedelta(days=365)
            period_data = retrieve_data_for_period(code, start_date, end_date)
            all_data.extend(period_data)

        if leap_years_count > 0:
            end_date = start_date
            start_date = end_date - timedelta(days=leap_years_count)
            period_data = retrieve_data_for_period(code, start_date, end_date)
            all_data.extend(period_data)

    new_df = pd.DataFrame(all_data, columns=columns)  # Add `company_key` to columns
    new_df = process_data_frame(new_df)
    insert_data_to_db(new_df)
    print(f"Data inserted for {code}")


if __name__ == "__main__":
    start_time = datetime.now()
    codes = get_symbols()

    # Retrieve the latest dates for each company_key from the database
    latest_dates = read_latest_dates_from_db()
    with ProcessPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(retrieve_data_for_code, code, latest_dates): code for code in codes}
        for future in concurrent.futures.as_completed(futures):
            code = futures[future]
            try:
                future.result()
                print(f"Completed retrieval for {code}")
            except Exception as e:
                print(f"Error retrieving data for {code}: {e}")

    end_time = datetime.now()
    print(f"Total time taken: {(end_time - start_time).total_seconds()} seconds")

