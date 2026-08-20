from pathlib import Path

import pandas as pd


def clean_market_data(
    input_path: Path,
    output_path: Path,
) -> pd.DataFrame:
    """
    Create a model-usable dataset from normalized market data.

    Rules:
    1. Remove candles that have not completed.
    2. Flag historical OHLC anomalies.
    3. Preserve data-quality metadata.
    """

    df = pd.read_parquet(input_path)

    # ---------------------------------------------------------------
    # Timestamp normalization
    # ---------------------------------------------------------------

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        utc=True,
    )

    df["available_at"] = pd.to_datetime(
        df["available_at"],
        utc=True,
    )

    # ---------------------------------------------------------------
    # Determine whether candle is complete
    # ---------------------------------------------------------------

    now_utc = pd.Timestamp.now(tz="UTC")

    df["candle_complete"] = (
        df["available_at"] <= now_utc
    )

    # ---------------------------------------------------------------
    # Remove incomplete candles
    # ---------------------------------------------------------------

    df = df[
        df["candle_complete"]
    ].copy()

    # ---------------------------------------------------------------
    # OHLC quality flags
    # ---------------------------------------------------------------

    df["invalid_high"] = (
        df["high"]
        < df[["open", "close"]].max(axis=1)
    )

    df["invalid_low"] = (
        df["low"]
        > df[["open", "close"]].min(axis=1)
    )

    df["ohlc_anomaly"] = (
        df["invalid_high"]
        | df["invalid_low"]
    )

    df["data_type"] = df["data_type"].astype(str)
    df["instrument"] = df["instrument"].astype(str)
    df["provider"] = df["provider"].astype(str)

    # ---------------------------------------------------------------
    # Sort
    # ---------------------------------------------------------------

    df = df.sort_values(
        "timestamp"
    )

    df = df.reset_index(
        drop=True
    )

    # ---------------------------------------------------------------
    # Save
    # ---------------------------------------------------------------

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_parquet(
        output_path,
        index=False,
    )

    return df