from .config import (
    FRED_END_DATE,
    FRED_START_DATE,
    INSTRUMENTS,
    TIMEFRAMES,
    INTERIM_DATA_DIR,
    PROCESSED_DATA_DIR,
    RAW_DATA_DIR,
)

from .availability import add_available_at
from .clean import clean_market_data
from .resample import resample_ohlc
from .validate import validate_market_data
from .providers.factory import create_provider


def process_yahoo_instrument(
    instrument_name: str,
    config: dict,
    timeframe_name: str,
    timeframe_config: dict,
):
    """
    Process a Yahoo Finance instrument.
    """

    provider = create_provider(
        "yahoo",
        RAW_DATA_DIR,
    )

    provider_interval = timeframe_config[
        "provider_interval"
    ]

    provider_period = timeframe_config[
        "provider_period"
    ]

    raw_path = (
        RAW_DATA_DIR
        / instrument_name
        / f"{instrument_name}_{timeframe_name}_raw.parquet"
    )

    print()
    print("=" * 80)
    print(
        f"YAHOO | {instrument_name} | "
        f"{timeframe_name}"
    )
    print("=" * 80)

    # ---------------------------------------------------------------
    # Download
    # ---------------------------------------------------------------

    df = provider.download(
        symbol=config["symbol"],
        instrument=instrument_name,
        interval=provider_interval,
        period=provider_period,
        data_type=config["data_type"],
    )

    provider.save_raw(
        df,
        instrument_name,
        timeframe_name,
    )

    # ---------------------------------------------------------------
    # Resampling
    # ---------------------------------------------------------------

    if timeframe_config.get("resample"):

        df = resample_ohlc(
            df,
            timeframe_name,
        )

        # Recalculate availability after resampling.
        df = add_available_at(
            df,
            timeframe_name,
        )

    # ---------------------------------------------------------------
    # Save intermediate
    # ---------------------------------------------------------------

    interim_path = (
        INTERIM_DATA_DIR
        / instrument_name
        / f"{instrument_name}_{timeframe_name}.parquet"
    )

    interim_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_parquet(
        interim_path,
        index=False,
    )

    # ---------------------------------------------------------------
    # Validate
    # ---------------------------------------------------------------

    validation = validate_market_data(
        interim_path
    )

    print_validation(
        validation
    )

    # ---------------------------------------------------------------
    # Clean
    # ---------------------------------------------------------------

    processed_path = (
        PROCESSED_DATA_DIR
        / instrument_name
        / f"{instrument_name}_{timeframe_name}.parquet"
    )

    cleaned = clean_market_data(
        interim_path,
        processed_path,
    )

    print(
        f"Processed: {processed_path}"
    )

    return cleaned


def process_fred_instrument(
    instrument_name: str,
    config: dict,
):
    """
    Process a FRED macroeconomic series.
    """

    provider = create_provider(
        "fred",
        RAW_DATA_DIR,
    )

    print()
    print("=" * 80)
    print(
        f"FRED | {instrument_name}"
    )
    print("=" * 80)

    # ---------------------------------------------------------------
    # Download
    # ---------------------------------------------------------------

    df = provider.download(
        series_id=config["series_id"],
        start=FRED_START_DATE,
        end=FRED_END_DATE,
        instrument=instrument_name,
    )

    # ---------------------------------------------------------------
    # Save raw
    # ---------------------------------------------------------------

    raw_path = provider.save_raw(
        df,
        instrument_name,
    )

    # ---------------------------------------------------------------
    # Save intermediate
    # ---------------------------------------------------------------

    interim_path = (
        INTERIM_DATA_DIR
        / instrument_name
        / f"{instrument_name}_1d.parquet"
    )

    interim_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_parquet(
        interim_path,
        index=False,
    )

    # ---------------------------------------------------------------
    # Validate
    # ---------------------------------------------------------------

    validation = validate_market_data(
        interim_path
    )

    print_validation(
        validation
    )

    # ---------------------------------------------------------------
    # Clean
    # ---------------------------------------------------------------

    processed_path = (
        PROCESSED_DATA_DIR
        / instrument_name
        / f"{instrument_name}_1d.parquet"
    )

    cleaned = clean_market_data(
        interim_path,
        processed_path,
    )

    print(
        f"Processed: {processed_path}"
    )

    return cleaned


def print_validation(
    validation: dict,
):
    """
    Print a standardized validation summary.
    """

    print()
    print("Validation:")
    print(
        f"  Valid: {validation['valid']}"
    )
    print(
        f"  Rows: {validation['rows']:,}"
    )
    print(
        f"  Start: {validation['start']}"
    )
    print(
        f"  End: {validation['end']}"
    )

    if validation["errors"]:

        print("\nErrors:")

        for error in validation["errors"]:
            print(
                f"  - {error}"
            )

    if validation["warnings"]:

        print("\nWarnings:")

        for warning in validation["warnings"]:
            print(
                f"  - {warning}"
            )


def run_yahoo_pipeline(
    instruments=None,
    timeframes=None,
):
    """
    Run Yahoo instruments through requested timeframes.
    """

    instruments = instruments or {
        name: config
        for name, config in INSTRUMENTS.items()
        if config["provider"] == "yahoo"
    }

    timeframes = timeframes or TIMEFRAMES

    for instrument_name, config in instruments.items():

        for timeframe_name, timeframe_config in timeframes.items():

            process_yahoo_instrument(
                instrument_name,
                config,
                timeframe_name,
                timeframe_config,
            )


def run_fred_pipeline(
    instruments=None,
):
    """
    Run FRED instruments at their native daily frequency.
    """

    instruments = instruments or {
        name: config
        for name, config in INSTRUMENTS.items()
        if config["provider"] == "fred"
    }

    for instrument_name, config in instruments.items():

        process_fred_instrument(
            instrument_name,
            config,
        )


if __name__ == "__main__":

    run_yahoo_pipeline()

    run_fred_pipeline()