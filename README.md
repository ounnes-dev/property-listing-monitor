
# Property Listing Intelligence

A Python project that collects property listings from Ouedkniss, stores them in SQLite, detects listing and price changes, and provides a dashboard for exploring the results.

## Features

- Collects property listings using the Ouedkniss GraphQL API.
- Stores listing information in a local SQLite database.
- Detects new listings and price changes.
- Tracks prices becoming available or unavailable.
- Records monitoring events for individual listings.
- Provides a FastAPI backend and browser-based dashboard.
- Includes market analytics and automated tests.

## Tech Stack

- Python
- Requests
- SQLite
- FastAPI
- Uvicorn
- Pytest
- HTML, CSS, and JavaScript

## Project Structure

```text
property-monitor/
├── app.py
├── collector.py
├── monitor.py
├── database.py
├── analytics.py
├── test_collector.py
├── test_monitor.py
├── test_monitor_safety.py
├── test_database.py
├── test_analytics.py
├── requirements.txt
└── README.md
```

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/ounnes-dev/property-listing-monitor
cd property-monitor
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the API and dashboard

```bash
python -m uvicorn app:app --reload --port 8001
```

Open the dashboard:

http://127.0.0.1:8001/dashboard

Interactive API documentation:

http://127.0.0.1:8001/docs

### 5. Run the monitoring process

In a separate terminal with the virtual environment activated:

```bash
python monitor.py
```

The monitoring process collects listings, compares them with the stored data, records detected events, and updates the database.

Collection can be limited using the `PROPERTY_MONITOR_MAX_PAGES` environment variable.

PowerShell example:

```powershell
$env:PROPERTY_MONITOR_MAX_PAGES = "3"
python monitor.py
```

### 6. Run the tests

```bash
pytest -q
```

## Data Storage

Listing information and monitoring events are stored in a local SQLite database. The database file is generated when the application initializes.

## Project Goals

This project explores practical data collection, data persistence, change detection, API development, analytics, and automated testing.

## Future Improvements

- Scheduled monitoring.
- More advanced property-market analytics.
- Configurable cities and property categories.
- Historical price trend visualizations.
- Notifications for significant listing changes.
