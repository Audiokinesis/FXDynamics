from pathlib import Path

import pandas as pd


def clean_market_data(
    input_path: Path,
    output_path: Path,
) -> pd.DataFrame:
    """
    Create a model-usable dataset from normalized market data.

    Rules:
    1. Remove future-dated records.
    2. Preserve historical OHLC anomalies.
    3. Add data-quality flags.
    """

    df = pd.read_parquet(input_path)

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        utc=True,
    )

    # ---------------------------------------------------------------
    # Future data
    # ---------------------------------------------------------------

    now_utc = pd.Timestamp.now(tz="UTC")

    df["future_data"] = (
        df["timestamp"] > now_utc
    )

    # Remove future records
    df = df[
        ~df["future_data"]
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