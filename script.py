# Stock Ticker Data Fetcher from Polygon API
# This script downloads all active stock ticker information from Polygon.io
# It includes resume functionality in case the process gets interrupted

# Import necessary libraries
import requests  # For making HTTP requests to APIs
import os       # For interacting with the operating system (file paths, environment variables)
from dotenv import load_dotenv  # For loading environment variables from .env file
import pandas as pd  # For data manipulation and creating CSV files
import time     # For adding delays between API requests
import json     # For reading/writing JSON files

# Load environment variables from .env file (this contains your API key)
load_dotenv()

# Configuration constants
API_kEY = os.getenv("POLYGON_API_KEY")  # Get API key from environment variables (safer than hardcoding)
LIMIT = 1000  # Number of tickers to request per API call (maximum allowed by Polygon)
PROGRESS_FILE = "progress.json"  # File to store our progress in case we need to resume
TICKERS_FILE = "tickers_partial.csv"  # File to store partial results as backup

def save_progress(next_url, tickers):
    """
    Save current progress to files so we can resume if interrupted
    
    Args:
        next_url: The URL for the next page of results from the API
        tickers: List of ticker dictionaries we've collected so far
    """
    # Create a progress dictionary with current state
    progress = {"next_url": next_url, "ticker_count": len(tickers)}
    
    # Save progress to JSON file
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f)
    
    # Save current tickers to CSV as backup
    if tickers:  # Only save if we have tickers
        df = pd.DataFrame(tickers)  # Convert list of dictionaries to DataFrame
        df.to_csv(TICKERS_FILE, index=False)  # Save to CSV without row numbers
    
    print(f"Progress saved: {len(tickers)} tickers collected")

def load_progress():
    """
    Load previous progress if script was interrupted and restarted
    
    Returns:
        next_url: URL to resume from (None if starting fresh)
        tickers: List of previously collected tickers (empty if starting fresh)
    """
    tickers = []  # Initialize empty list for tickers
    next_url = None  # Initialize as None (means start from beginning)
    
    # Try to load previous progress
    if os.path.exists(PROGRESS_FILE):  # Check if progress file exists
        with open(PROGRESS_FILE, 'r') as f:
            progress = json.load(f)  # Load the JSON data
            next_url = progress.get("next_url")  # Get the next URL to continue from
            print(f"Found previous progress: {progress.get('ticker_count', 0)} tickers")
    
    # Try to load previously saved tickers
    if os.path.exists(TICKERS_FILE):  # Check if partial results file exists
        df = pd.read_csv(TICKERS_FILE)  # Load CSV into DataFrame
        tickers = df.to_dict('records')  # Convert DataFrame back to list of dictionaries
        print(f"Loaded {len(tickers)} existing tickers from {TICKERS_FILE}")
    
    return next_url, tickers

def run_stock_job():
    # Main execution starts here
    # Check if we're resuming from previous run or starting fresh
    resume_url, tickers = load_progress()

    # Set up the initial API request URL
    if resume_url:
        # We're resuming - use the saved URL and add our API key
        print(f"Resuming from: {resume_url}")
        url = resume_url + f'&apiKey={API_kEY}'
    else:
        # Starting fresh - build the initial request URL
        print("Starting fresh")
        # API endpoint with parameters:
        # - market=stocks: only stock tickers
        # - active=true: only currently active tickers
        # - order=asc: alphabetical order
        # - limit=1000: maximum results per request
        # - sort=ticker: sort by ticker symbol
        url = f"https://api.polygon.io/v3/reference/tickers?market=stocks&active=true&order=asc&limit={LIMIT}&sort=ticker&apiKey={API_kEY}"

    # Make the first API request
    response = requests.get(url)  # Send HTTP GET request
    data = response.json()  # Convert response to Python dictionary

    # Check if the API returned an error
    if data.get('status') == 'ERROR':
        print(f"API Error: {data.get('error')}")
        exit(1)  # Stop the program if there's an API error

    # Add results from first request (only if not resuming to avoid duplicates)
    if not resume_url and 'results' in data:
        for ticker in data['results']:  # Loop through each ticker in the results
            tickers.append(ticker)  # Add ticker dictionary to our list

    # Keep track of how many requests we've made
    request_count = 1
    print(f"Current total: {len(tickers)} tickers")

    # Main loop: continue requesting pages until we get all data
    while 'next_url' in data:  # As long as there's a next page URL
        # Save our progress before making the next request (in case something goes wrong)
        save_progress(data['next_url'], tickers)
        
        # Wait 12 seconds between requests to respect rate limits
        # (Polygon allows 5 requests per minute for free accounts)
        print("Waiting 12 seconds before next request...")
        time.sleep(12)
        
        # Make the next request
        print(f'Requesting next page (Request #{request_count + 1}): {data["next_url"]}')
        response = requests.get(data['next_url'] + f'&apiKey={API_kEY}')  # Add API key to next URL
        data = response.json()  # Convert response to dictionary
        
        # Check for API errors (especially rate limiting)
        if data.get('status') == 'ERROR':
            print(f"API Error: {data.get('error')}")
            
            # Special handling for rate limit errors
            if 'exceeded the maximum requests' in data.get('error', ''):
                print("Rate limit hit - waiting 60 seconds before retrying...")
                time.sleep(60)  # Wait longer and try the same request again
                continue  # Go back to start of while loop with same URL
            else:
                # Different error - stop the program
                print("Different API error occurred. Stopping.")
                break  # Exit the while loop
        
        # Process the results from this request
        if 'results' in data:
            for ticker in data['results']:  # Loop through each ticker
                tickers.append(ticker)  # Add to our master list
            print(f"Retrieved {len(data['results'])} more tickers. Total: {len(tickers)}")
        else:
            # No results in response - something went wrong
            print("No results in response. Stopping.")
            break  # Exit the while loop
        
        request_count += 1  # Increment our request counter

    # We're done collecting data
    print(f"Completed after {request_count} requests. Total tickers collected: {len(tickers)}")

    # Define the columns we want in our final CSV file
    columns = [
        "ticker", "name", "market", "locale", "primary_exchange", "type", 
        "active", "currency_name", "cik", "composite_figi", "share_class_figi", "last_updated_utc"
    ]

    # Ensure all tickers have all columns (some might be missing certain fields)
    for t in tickers:  # Loop through each ticker dictionary
        for col in columns:  # Check each column we want
            if col not in t:  # If the ticker doesn't have this field
                t[col] = None  # Set it to None (will show as empty in CSV)

    # Create final DataFrame with specified column order
    df = pd.DataFrame(tickers, columns=columns)

    # Save the final results to CSV
    df.to_csv("tickers_final.csv", index=False)  # Save without row numbers
    print(f"Saved {len(tickers)} tickers to tickers_final.csv")

    # Clean up temporary files since we're done
    if os.path.exists(PROGRESS_FILE):  # If progress file exists
        os.remove(PROGRESS_FILE)  # Delete it
    if os.path.exists(TICKERS_FILE):  # If partial results file exists
        os.remove(TICKERS_FILE)  # Delete it
    print("Cleanup completed - removed progress files")


# allow running standalone
if __name__ == "__main__":
    run_stock_job()