# FLY

FLY is a small data pipeline for gathering financial information about companies traded on B3. It scrapes company metadata and sequential document numbers (NSD) and stores them in a local SQLite database.

## Technologies

- **Python 3.11**
- **SQLite** with **SQLAlchemy**
- Hexagonal Architecture (Ports and Adapters)

## Installation

1. Create a virtual environment and install the dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Run the CLI application:
   ```bash
   python run.py
   ```

The CLI invokes the application services to synchronize companies and NSD records. Logs are written to `fly_logger.log` in the project root.

## Services

Two main services can be triggered individually:

- `sync_companies` – Fetch company listings and details from B3.
- `sync_nsd` – Download sequential document information.

Both services are started from `presentation/cli.py` when you execute `run.py`.

## Project Layout

```
domain/         # DTOs and ports
application/    # services and use cases
infrastructure/ # scrapers, repositories, helpers
presentation/   # CLI entry point
```

Development and production runs use the same entry point. Adjust configuration files in `infrastructure/config` if you need to change paths or logging levels.
