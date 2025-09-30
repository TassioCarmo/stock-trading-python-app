# Stock Ticker Data Fetcher from Polygon API
# Downloads all active stock ticker information and uploads to Snowflake

# Import necessary libraries
import requests  # For making API calls to Polygon
import os  # For accessing environment variables and operating system functions
from dotenv import load_dotenv  # For loading environment variables from .env file
import pandas as pd  # For data manipulation and analysis
from datetime import datetime  # For working with dates and times
import time  # For adding delays between API calls
import snowflake.connector  # For connecting to Snowflake database
from snowflake.connector.pandas_tools import write_pandas  # For writing pandas DataFrames to Snowflake

# Load environment variables from .env file
# This keeps sensitive information like API keys and passwords secure
load_dotenv()

# =========================
# Polygon API configuration
# =========================
API_KEY = os.getenv("POLYGON_API_KEY")  # Get API key from environment variables
LIMIT = 1000  # Number of records to fetch per API call (max allowed by Polygon)

# =========================
# Snowflake configuration
# =========================
# Get all Snowflake connection details from environment variables
SNOWFLAKE_ACCOUNT   = os.getenv("SNOWFLAKE_ACCOUNT")    # Your Snowflake account identifier
SNOWFLAKE_USER      = os.getenv("SNOWFLAKE_USER")       # Your Snowflake username
SNOWFLAKE_PASSWORD  = os.getenv("SNOWFLAKE_PASSWORD")   # Your Snowflake password
SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE")  # Compute resource for queries
SNOWFLAKE_DATABASE  = os.getenv("SNOWFLAKE_DATABASE")   # Database to store data in
SNOWFLAKE_SCHEMA    = os.getenv("SNOWFLAKE_SCHEMA")     # Schema (namespace) within database
SNOWFLAKE_ROLE      = os.getenv("SNOWFLAKE_ROLE")       # Security role with permissions

# =========================
# Columns to keep
# =========================
# We define which columns we want to extract from the API response
# This helps us focus only on the important information
COLUMNS = [
    "ticker",           # Stock symbol (e.g., AAPL for Apple)
    "name",             # Company name
    "market",           # Market type (stocks, crypto, etc.)
    "locale",           # Geographic region (us, global, etc.)
    "primary_exchange", # Main stock exchange (NASDAQ, NYSE, etc.)
    "type",             # Security type (CS for Common Stock, ETF, etc.)
    "active",           # Whether the ticker is currently active
    "currency_name",    # Currency used for trading (USD, CAD, etc.)
    "cik",              # Central Index Key (SEC identifier)
    "composite_figi",   # Financial Instrument Global Identifier
    "share_class_figi", # Share class specific identifier
    "last_updated_utc"  # When this information was last updated
]

def fetch_all_tickers():
    """
    Fetch all active stock tickers from Polygon API.
    
    This function handles pagination - Polygon returns data in pages, so we need
    to make multiple requests to get all the data.
    
    Returns:
        list: A list of dictionaries containing ticker information
    """
    tickers = []  # Empty list to store all our ticker data
    # Initial API URL - note the parameters:
    # - market=stocks: Only get stock tickers
    # - active=true: Only currently active tickers  
    # - order=asc: Ascending order by ticker symbol
    # - limit=1000: Maximum records per request
    # - sort=ticker: Sort by ticker symbol
    url = f"https://api.polygon.io/v3/reference/tickers?market=stocks&active=true&order=asc&limit={LIMIT}&sort=ticker&apiKey={API_KEY}"
    request_count = 1  # Counter to track how many API calls we've made

    # Keep making requests until there are no more pages
    while url:
        print(f"Requesting page #{request_count}...")
        
        # Make the API call
        response = requests.get(url)
        data = response.json()  # Convert JSON response to Python dictionary

        # Check if the API returned an error
        if data.get('status') == 'ERROR':
            print(f"API Error: {data.get('error')}")
            break  # Stop if there's an error

        # Extract the results from the API response
        results = data.get('results', [])
        tickers.extend(results)  # Add this page's results to our main list
        print(f"Retrieved {len(results)} tickers. Total so far: {len(tickers)}")

        # Check if there's a next page
        url = data.get('next_url')  # Polygon provides the next page URL if exists
        if url:
            # Add API key to the next page URL
            url += f"&apiKey={API_KEY}"
            time.sleep(12)  # Wait 12 seconds to respect Polygon's rate limits (5 requests/minute)
        
        request_count += 1  # Increment our request counter

    print(f"Completed fetching. Total tickers collected: {len(tickers)}")
    return tickers

def clean_and_prepare_df(tickers):
    """
    Convert the raw ticker data into a clean DataFrame for Snowflake.
    
    Steps:
    1. Ensure all tickers have all required columns (fill missing with None)
    2. Convert to pandas DataFrame
    3. Add a 'ds' (date stamp) column with today's date
    4. Convert all column names to uppercase for Snowflake compatibility
    
    Args:
        tickers (list): List of dictionaries containing ticker data
        
    Returns:
        pandas.DataFrame: Cleaned and prepared DataFrame
    """
    # Step 1: Ensure every ticker dictionary has all the columns we want
    # Some tickers might be missing certain fields in the API response
    for ticker in tickers:
        for col in COLUMNS:
            if col not in ticker:
                ticker[col] = None  # Fill missing columns with None

    # Step 2: Convert list of dictionaries to pandas DataFrame
    df = pd.DataFrame(tickers, columns=COLUMNS)
    
    # Step 3: Add a date column to track when we fetched this data
    # This is useful for data versioning and tracking
    df['ds'] = datetime.today().strftime('%Y-%m-%d')  # Format as YYYY-MM-DD
    
    # Step 4: Convert column names to uppercase (Snowflake convention)
    df.columns = [col.upper() for col in df.columns]
    
    return df

def upload_to_snowflake(df):
    """
    Upload the DataFrame to Snowflake database.
    
    Steps:
    1. Establish connection to Snowflake
    2. Activate the warehouse (compute resource)
    3. Create the table if it doesn't exist
    4. Upload the data
    5. Close the connection
    
    Args:
        df (pandas.DataFrame): The prepared DataFrame to upload
    """
    # Step 1: Connect to Snowflake using our environment variables
    conn = snowflake.connector.connect(
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        account=SNOWFLAKE_ACCOUNT,
        database=SNOWFLAKE_DATABASE,
        schema=SNOWFLAKE_SCHEMA,
        role=SNOWFLAKE_ROLE
    )

    # Step 2: Use a cursor to execute SQL commands
    with conn.cursor() as cur:
        # Activate our warehouse (like turning on a computer for processing)
        cur.execute(f"USE WAREHOUSE {SNOWFLAKE_WAREHOUSE}")

        # Step 3: Create the table if it doesn't exist
        # This ensures our script won't fail if the table hasn't been created yet
        create_table_query = """
        CREATE TABLE IF NOT EXISTS STOCK_TICKERS (
            TICKER STRING,              -- Stock symbol
            NAME STRING,                -- Company name  
            MARKET STRING,              -- Market type
            LOCALE STRING,              -- Geographic region
            PRIMARY_EXCHANGE STRING,    -- Main exchange
            TYPE STRING,                -- Security type
            ACTIVE BOOLEAN,             -- Active status
            CURRENCY_NAME STRING,       -- Trading currency
            CIK STRING,                 -- SEC identifier
            COMPOSITE_FIGI STRING,      -- Global identifier
            SHARE_CLASS_FIGI STRING,    -- Share class identifier
            LAST_UPDATED_UTC STRING,    -- Last update timestamp
            DS DATE                     -- Our data collection date
        )
        """
        cur.execute(create_table_query)
        print("Table STOCK_TICKERS is ready (will append data).")

    # Step 4: Upload the DataFrame to Snowflake
    # write_pandas automatically handles the data conversion and insertion
    success, nchunks, nrows, _ = write_pandas(conn, df, "STOCK_TICKERS")
    print(f"Upload complete: {nrows} rows inserted.")

    # Step 5: Close the connection to free up resources
    conn.close()

def main():
    """
    Main function that orchestrates the entire process:
    1. Fetch data from Polygon API
    2. Clean and prepare the data
    3. Upload to Snowflake
    """
    # Step 1: Get all ticker data from Polygon
    tickers = fetch_all_tickers()
    
    # Step 2: Clean the data and convert to DataFrame
    df = clean_and_prepare_df(tickers)
    
    # Step 3: Upload to Snowflake
    upload_to_snowflake(df)

# This condition ensures the script only runs when executed directly
# (not when imported as a module)
if __name__ == "__main__":
    main()