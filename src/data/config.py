from pathlib import Path


# -------------------------------------------------------------------
# Project paths
# -------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
INTERIM_DATA_DIR = DATA_DIR / "interim"
PROCESSED_DATA_DIR = DATA_DIR / "processed"


# -------------------------------------------------------------------
# Instruments
# -------------------------------------------------------------------

INSTRUMENTS = {
    "EURUSD": {
        "provider": "yfinance",
        "symbol": "EURUSD=X",
        "asset_class": "fx",
    },
    "DXY": {
        "provider": "yfinance",
        "symbol": "DX-Y.NYB",
        "asset_class": "index",
    },
    "US2Y": {
        "provider": "yfinance",
        "symbol": "^UST2Y",
        "asset_class": "rates",
    },
    "DE2Y": {
        "provider": "yfinance",
        "symbol": "^DE2Y",
        "asset_class": "rates",
    },
    "US10Y": {
        "provider": "yfinance",
        "symbol": "^TNX",
        "asset_class": "rates",
    },
}


# -------------------------------------------------------------------
# Timeframes
# -------------------------------------------------------------------

TIMEFRAMES = [
    "5m",
    "15m",
    "1h",
    "4h",
    "1d",
]