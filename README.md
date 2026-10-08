# Property Listing Intelligence & Monitoring System

A Python-based system for collecting publicly available property listings from Ouedkniss and monitoring changes in those listings over time.

The system collects property data through Ouedkniss' public GraphQL endpoint, stores historical snapshots, compares current listings with previous runs, and records newly added, removed, or price-changed listings.

## Features

* Collect property listings through a GraphQL API
* Search and paginate through multiple result pages
* Extract structured listing information
* Classify listings as sale or rental based on their titles
* Store collected listings in CSV format
* Maintain a previous snapshot for historical comparison
* Detect:

  * New listings
  * Removed listings
  * Price changes
* Record detected events with timestamps
* Handle HTTP and API-level errors
* Use request timeouts to prevent indefinitely hanging requests
* Run the monitoring process automatically using Windows Task Scheduler

## Architecture

```text
                    Ouedkniss
                        |
                        v
                  GraphQL API
                        |
                        v
                  collector.py
                        |
                        v
                Current listings
                        |
                        v
                   monitor.py
                        |
             +----------+----------+
             |          |          |
             v          v          v
            NEW      REMOVED   PRICE CHANGED
             |          |          |
             +----------+----------+
                        |
                        v
                   events.csv


             previous_listings.csv
              (historical snapshot)
                        |
                        |
                        +-----> monitor.py
```

## Data Collected

For each listing, the system currently collects:

| Field              | Description                     |
| ------------------ | ------------------------------- |
| `id`               | Unique listing identifier       |
| `title`            | Original listing title          |
| `createdAt`        | Timestamp returned by the API   |
| `price`            | Price value returned by the API |
| `slug`             | Listing slug                    |
| `city`             | Listing city                    |
| `transaction_type` | Sale, rent, or unknown          |

The original listing title and raw price value are preserved rather than attempting to guess or reinterpret seller-specific pricing conventions.

## Change Detection

The monitoring system uses the listing ID as the stable identifier when comparing snapshots.

### New Listings

A listing is considered new when its ID appears in the current collection but not in the previous snapshot.

### Removed Listings

A listing is considered removed when its ID appears in the previous snapshot but not in the current collection.

### Price Changes

A price change is detected when the same listing exists in both snapshots but its numeric price differs.

Detected events are stored in `events.csv` with a timestamp and relevant listing information.

## Project Structure

```text
property-monitor/
|
├── collector.py
|   └── Collects and processes property listings
|
├── monitor.py
|   └── Compares listing snapshots and detects changes
|
├── experiments/
|   ├── dictionary_experiment.py
|   ├── graphql_experiment.py
|   └── request_experiment.py
|       └── Exploratory scripts used during development
|
├── .gitignore
└── README.md
```

The following files are generated locally and excluded from version control:

```text
listings.csv
previous_listings.csv
events.csv
```

## Requirements

* Python 3
* `requests`
* Internet connection
* Access to the Ouedkniss public GraphQL endpoint

## Installation

Clone the repository and create a virtual environment:

```bash
python -m venv .venv
```

Activate the virtual environment on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Install the required package:

```powershell
pip install requests
```

## Running the Monitor

Run the monitoring system with:

```powershell
python monitor.py
```

The system will:

1. Collect the current property listings.
2. Compare them with the previous snapshot.
3. Detect new, removed, and price-changed listings.
4. Record detected events.
5. Save the current collection as the new snapshot.

The collector is currently limited to a small number of pages during development to avoid unnecessary requests to the website.

## Automation

The monitoring script can be executed automatically using Windows Task Scheduler.

This allows the system to periodically collect new data without requiring manual execution.

## Design Considerations

### Public Data

The project uses publicly accessible property listing information and does not attempt to bypass authentication, CAPTCHAs, paywalls, or other access controls.

### Raw Data Preservation

The system does not attempt to infer the meaning of unusual seller-entered price values. The raw value returned by the API is preserved.

### Stable Identifiers

Listing IDs are used instead of titles as the primary identifier because titles can change while the listing itself remains the same.

### API Validation

The collector validates the structure of API responses before processing them and handles HTTP request failures without crashing the entire collection process.

## Current Limitations

* Currently focused on Ouedkniss.
* Monitoring is limited to a small number of pages during development.
* Data is stored in CSV files rather than a database.
* Notifications are not yet implemented.
* No web dashboard is currently included.

## Future Improvements

Possible future improvements include:

* Persistent database storage
* Monitoring additional property sources
* More advanced property filtering
* Historical price analysis
* Automated notifications
* Data visualization
* A web-based monitoring dashboard

## Technologies

* Python
* Requests
* GraphQL
* CSV
* Git / GitHub
* Windows Task Scheduler
