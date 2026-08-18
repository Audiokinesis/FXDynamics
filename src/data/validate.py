from pathlib import Path
from datetime import datetime, timezone

import pandas as pd


REQUIRED_COLUMNS = {
    "timestamp",
    "open",
    "high",
    "low",
    "close",
    "volume",
}


def validate_market_data(
    path: Path,
) -> dict:
    """
    Validate a normalized market-data Parquet file.

    Future-dated records are treated as errors.

    Historical OHLC inconsistencies are reported as
    data-quality anomalies but do not automatically
    invalidate the entire dataset.
    """

    df = pd.read_parquet(path)

    errors = []
    warnings = []

    # ---------------------------------------------------------------
    # Columns
    # ---------------------------------------------------------------

    missing_columns = REQUIRED_COLUMNS - set(df.columns)

    if missing_columns:
        errors.append(
            f"Missing columns: {sorted(missing_columns)}"
        )

    if df.empty:
        errors.append("Dataset is empty.")

        return {
            "valid": False,
            "rows": 0,
            "errors": errors,
            "warnings": warnings,
        }

    # ---------------------------------------------------------------
    # Timestamp
    # ---------------------------------------------------------------

    if not pd.api.types.is_datetime64_any_dtype(
        df["timestamp"]
    ):
        errors.append(
            "timestamp is not a datetime type."
        )

    # Make sure timestamps are UTC
    timestamps = pd.to_datetime(
        df["timestamp"],
        utc=True,
    )

    # ---------------------------------------------------------------
    # Timestamp ordering
    # ---------------------------------------------------------------

    if not timestamps.is_monotonic_increasing:
        errors.append(
            "Timestamps are not monotonically increasing."
        )

    # ---------------------------------------------------------------
    # Duplicate timestamps
    # ---------------------------------------------------------------

    duplicate_count = timestamps.duplicated().sum()

    if duplicate_count:
        errors.append(
            f"Found {duplicate_count} duplicate timestamps."
        )

    # ---------------------------------------------------------------
    # Future records
    # ---------------------------------------------------------------

    now_utc = pd.Timestamp.now(tz="UTC")

    future_rows = df[
        timestamps > now_utc
    ]

    future_count = len(future_rows)

    if future_count:
        errors.append(
            f"Found {future_count} future-dated records."
        )

    # ---------------------------------------------------------------
    # NaNs
    # ---------------------------------------------------------------

    for column in [
        "open",
        "high",
        "low",
        "close",
    ]:

        missing = df[column].isna().sum()

        if missing:
            warnings.append(
                f"{column} contains {missing} missing values."
            )

    # ---------------------------------------------------------------
    # OHLC consistency
    # ---------------------------------------------------------------

    invalid_high = df[
        df["high"]
        < df[["open", "close"]].max(axis=1)
    ]

    invalid_low = df[
        df["low"]
        > df[["open", "close"]].min(axis=1)
    ]

    if len(invalid_high):

        warnings.append(
            f"{len(invalid_high)} rows have "
            f"invalid high values."
        )

    if len(invalid_low):

        warnings.append(
            f"{len(invalid_low)} rows have "
            f"invalid low values."
        )

    # ---------------------------------------------------------------
    # Summary
    # ---------------------------------------------------------------

    return {
        "valid": len(errors) == 0,

        "rows": len(df),

        "start": timestamps.min(),

        "end": timestamps.max(),

        "future_rows": future_count,

        "invalid_high_rows": len(invalid_high),

        "invalid_low_rows": len(invalid_low),

        "errors": errors,

        "warnings": warnings,
    }