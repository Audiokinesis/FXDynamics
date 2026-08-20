from pathlib import Path


# -------------------------------------------------------------------
# Project paths
# -------------------------------------------------------------------

PROJECT_ROOT = Path(r"C:/Users/mdesc/Documents/Projects/FXDynamics/src/data/config.py").resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"

RAW_DATA_DIR = DATA_DIR / "raw"

INTERIM_DATA_DIR = DATA_DIR / "interim"

PROCESSED_DATA_DIR = DATA_DIR / "processed"


# -------------------------------------------------------------------
# Instruments
# -------------------------------------------------------------------

INSTRUMENTS = {

    "EURUSD": {
        "provider": "yahoo",
        "symbol": "EURUSD=X",
        "asset_class": "fx",
        "data_type": "price",
    },

    "DXY": {
        "provider": "yahoo",
        "symbol": "DX-Y.NYB",
        "asset_class": "index",
        "data_type": "index",
    },

    "US2Y": {
        "provider": "fred",
        "series_id": "DGS2",
        "asset_class": "rates",
        "data_type": "yield",
    },

    "US10Y": {
        "provider": "fred",
        "series_id": "DGS10",
        "asset_class": "rates",
        "data_type": "yield",
    },
}


# -------------------------------------------------------------------
# Yahoo timeframes
# -------------------------------------------------------------------

TIMEFRAMES = {

    "5m": {
        "provider_interval": "5m",
        "provider_period": "5d",
    },

    "15m": {
        "provider_interval": "15m",
        "provider_period": "60d",
    },

    "1h": {
        "provider_interval": "1h",
        "provider_period": "730d",
    },

    "4h": {
        "provider_interval": "1h",
        "provider_period": "730d",
        "resample": "4h",
    },

    "1d": {
        "provider_interval": "1d",
        "provider_period": "max",
    },
}


# -------------------------------------------------------------------
# FRED configuration
# -------------------------------------------------------------------

FRED_START_DATE = "2000-01-01"

FRED_END_DATE = None