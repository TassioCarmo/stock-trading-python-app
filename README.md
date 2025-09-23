# stock-trading-python-app
This uses the Polygon.io to extrack data about stocks

# Stock Ticker Data Pipeline

A Python project to fetch, store, and schedule updates of all active stock tickers using the [Polygon.io API](https://polygon.io/). This pipeline includes resume functionality to handle interruptions and can be automated with a scheduler.

---

## Features

- Fetches all active stock tickers from Polygon.io.
- Supports resuming downloads if interrupted.
- Saves partial results to CSV during execution.
- Produces a clean, final CSV file (`tickers_final.csv`) with all relevant columns.
- Optional scheduler to run the fetch job at regular intervals.

---

## Requirements

- Python 3.8+
- Libraries (see `requirements.txt`):

```text
requests
openai
python-dotenv
pandas
schedule
