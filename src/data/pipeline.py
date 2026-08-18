from pathlib import Path

from .config import (
    INSTRUMENTS,
    TIMEFRAMES,
    RAW_DATA_DIR,
    INTERIM_DATA_DIR,
)

from .downloader import download_market_data
from .normalize import normalize_market_data
from .validate import validate_market_data


def run_pipeline(
    instruments=None,
    timeframes=None,
):
    """
    Execute the market-data ingestion pipeline.
    """

    instruments = instruments or INSTRUMENTS
    timeframes = timeframes or TIMEFRAMES

    for instrument_name, config in instruments.items():

        provider_symbol = config["symbol"]

        for timeframe in timeframes:

            print()
            print("=" * 70)
            print(
                f"{instrument_name} | {timeframe}"
            )
            print("=" * 70)

            # -------------------------------------------------------
            # Download
            # -------------------------------------------------------

            raw_path = download_market_data(
                instrument_name=instrument_name,
                provider_symbol=provider_symbol,
                interval=timeframe,
            )

            # -------------------------------------------------------
            # Normalize
            # -------------------------------------------------------

            normalized_path = (
                INTERIM_DATA_DIR
                / instrument_name
                / f"{instrument_name}_{timeframe}.parquet"
            )

            normalize_market_data(
                input_path=raw_path,
                output_path=normalized_path,
            )

            # -------------------------------------------------------
            # Validate
            # -------------------------------------------------------

            result = validate_market_data(
                normalized_path
            )

            print()
            print("Validation")
            print("-" * 30)
            print(f"Valid: {result['valid']}")
            print(f"Rows:  {result.get('rows')}")
            print(f"Start: {result.get('start')}")
            print(f"End:   {result.get('end')}")

            if result["errors"]:
                print("\nERRORS:")

                for error in result["errors"]:
                    print(f"  - {error}")

            if result["warnings"]:
                print("\nWARNINGS:")

                for warning in result["warnings"]:
                    print(f"  - {warning}")


if __name__ == "__main__":
    run_pipeline()