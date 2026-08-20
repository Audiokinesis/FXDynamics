from __future__ import annotations

import pandas as pd


def resample_ohlc(
    df: pd.DataFrame,
    timeframe: str,
) -> pd.DataFrame:
    """
    Resample OHLC data while preserving instrument metadata.

    The resulting candle represents a completed higher-timeframe
    interval. Availability is calculated separately after resampling.
    """

    if timeframe != "4h":
        raise ValueError(
            f"Unsupported resampling timeframe: {timeframe}"
        )

    df = df.copy()

    # ---------------------------------------------------------------
    # Timestamp
    # ---------------------------------------------------------------

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        utc=True,
    )

    df = df.sort_values(
        "timestamp"
    )

    df = df.set_index(
        "timestamp"
    )

    # ---------------------------------------------------------------
    # Resample OHLC
    # ---------------------------------------------------------------

    result = df.resample(
        "4h",
        label="left",
        closed="left",
    ).agg(
        {
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last",
            "volume": "sum",
        }
    )

    # Remove incomplete/empty 4H intervals
    result = result.dropna(
        subset=[
            "open",
            "high",
            "low",
            "close",
        ]
    )

    result = result.reset_index()

    # ---------------------------------------------------------------
    # Preserve semantic metadata
    #
    # These should be constant for the entire source dataset.
    # ---------------------------------------------------------------

    metadata_columns = [
        "instrument",
        "data_type",
        "provider",
    ]

    for column in metadata_columns:

        if column in df.columns:

            values = (
                df[column]
                .dropna()
                .unique()
            )

            if len(values) != 1:
                raise ValueError(
                    f"Expected exactly one value for "
                    f"metadata column '{column}', "
                    f"found: {values}"
                )

            result[column] = values[0]

    # ---------------------------------------------------------------
    # Canonical ordering
    # ---------------------------------------------------------------

    column_order = [
        "timestamp",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "instrument",
        "data_type",
        "provider",
    ]

    result = result[
        [
            column
            for column in column_order
            if column in result.columns
        ]
    ]

    return result.reset_index(
        drop=True
    )