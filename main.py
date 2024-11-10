import re
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import pandas as pd
import concurrent.futures
import os
import requests

# Define column names
columns = ['Date', 'Last trade price', 'Max', 'Min', 'Avg.', 'Price %chg.', 'Volume', 'Turnover in BEST in denars',
           'Total turnover in denars']

# Set up the base URL and number of years
base_url = "https://www.mse.mk/en/stats/symbolhistory/"
years = 10


# Function to check leap year
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


def retrieve_data_for_period(code, start_date, end_date): #filter 3
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
        data = [cell.get_text(strip=True) for cell in cells]
        period_data.append(data)

    print(f"Retrieved data for {code} from {start_date} to {end_date}")
    return period_data

def process_data_frame(df):
    # Change date format to 'dd.mm.yyyy'
    df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y').dt.strftime('%d.%m.%Y')

    # Replace commas in price columns
    price_columns = ['Last trade price', 'Max', 'Min', 'Avg.', 'Price %chg.', 'Turnover in BEST in denars', 'Total turnover in denars']
    for col in price_columns:
        df[col] = df[col].str.replace('.', ';').str.replace(',', '.').str.replace(';', ',')
        #10,000.00
        #10.000,00

    df = df[df['Volume'] != 0]

    return df


def read_latest_date_from_csv(code): # filter 2
    path = os.path.join("storage", f"{code}.csv")

    if os.path.exists(path):
        with open(path, 'r') as f:
            f.readline()  # Read the first line
            second_line = f.readline()  # Read the second line
            return second_line.split(",")[0]

    return None


def retrieve_data_for_code(code):
    all_data = []
    exists = False
    start_date = datetime.now()
    leap_years_count = sum(is_leap_year(start_date.year - i) for i in range(years))
    latest_date = read_latest_date_from_csv(code)

    if latest_date is not None:
        exists = True
        latest_date = datetime.strptime(latest_date, '%d.%m.%Y')
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

        # Handle any remaining leap days in the last interval
        if leap_years_count > 0:
            end_date = start_date
            start_date = end_date - timedelta(days=leap_years_count)
            period_data = retrieve_data_for_period(code, start_date, end_date)
            all_data.extend(period_data)

    path = os.path.join("storage", f"{code}.csv")
    new_df = pd.DataFrame(all_data, columns=columns)
    new_df = process_data_frame(new_df)

    if os.path.exists(path):
        existing_df = pd.read_csv(path)
        if not exists:
            combined_df = pd.concat([new_df, existing_df], ignore_index=True)
            combined_df.to_csv(path, index=False)
    else:
        new_df.to_csv(path, index=False)
    print(f"Data saved to {path} for {code}")



if __name__ == "__main__":
    os.makedirs("storage", exist_ok=True)  # Ensure storage directory exists
    codes = get_symbols()

    start_time = datetime.now()
    # with concurrent.futures.ThreadPoolExecutor() as executor:
    with ProcessPoolExecutor(max_workers=16) as executor:
        futures = {executor.submit(retrieve_data_for_code, code): code for code in codes}
        for future in concurrent.futures.as_completed(futures):
            code = futures[future]
            try:
                future.result()
                print(f"Completed retrieval for {code}")
            except Exception as e:
                print(f"Error retrieving data for {code}: {e}")

    end_time = datetime.now()
    print(f"Total time taken: {(end_time - start_time).total_seconds()} seconds")
