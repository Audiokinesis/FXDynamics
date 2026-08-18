from pathlib import Path

import pandas as pd


EXPECTED_COLUMNS = [
    "timestamp",
    "open",
    "high",
    "low",
    "close",
    "volume",
]


def normalize_market_data(
    input_path: Path,
    output_path: Path,
) -> pd.DataFrame:
    """
    Convert provider-specific OHLC data into the FXDynamics
    canonical market-data format.
    """

    df = pd.read_parquet(input_path)

    # ---------------------------------------------------------------
    # Handle Yahoo Finance MultiIndex columns
    # ---------------------------------------------------------------

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [
            column[0] if isinstance(column, tuple) else column
            for column in df.columns
        ]

    # ---------------------------------------------------------------
    # Reset index so timestamp becomes a normal column
    # ---------------------------------------------------------------

    df = df.reset_index()

    # ---------------------------------------------------------------
    # Normalize column names
    # ---------------------------------------------------------------

    df.columns = [
        str(column).strip().lower().replace(" ", "_")
        for column in df.columns
    ]

    # ---------------------------------------------------------------
    # Identify timestamp column
    # ---------------------------------------------------------------

    timestamp_candidates = [
        "timestamp",
        "datetime",
        "date",
        "index",
    ]

    timestamp_column = next(
        (
            column
            for column in timestamp_candidates
            if column in df.columns
        ),
        None,
    )

    if timestamp_column is None:
        raise ValueError(
            "Could not identify timestamp column. "
            f"Available columns: {list(df.columns)}"
        )

    if timestamp_column != "timestamp":
        df = df.rename(
            columns={
                timestamp_column: "timestamp"
            }
        )

    # ---------------------------------------------------------------
    # Convert timestamp to UTC
    # ---------------------------------------------------------------

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        utc=True,
    )

    # ---------------------------------------------------------------
    # Normalize OHLC column names
    # ---------------------------------------------------------------

    rename_map = {
        "open": "open",
        "high": "high",
        "low": "low",
        "close": "close",
        "volume": "volume",
    }

    df = df.rename(columns=rename_map)

    # ---------------------------------------------------------------
    # Verify required columns
    # ---------------------------------------------------------------

    required = [
        "timestamp",
        "open",
        "high",
        "low",
        "close",
    ]

    missing = [
        column
        for column in required
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}. "
            f"Available columns: {list(df.columns)}"
        )

    # ---------------------------------------------------------------
    # Volume isn't always meaningful/available for FX.
    # Create it if necessary.
    # ---------------------------------------------------------------

    if "volume" not in df.columns:
        df["volume"] = 0

    # ---------------------------------------------------------------
    # Select canonical schema
    # ---------------------------------------------------------------

    df = df[
        [
            "timestamp",
            "open",
            "high",
            "low",
            "close",
            "volume",
        ]
    ]

    # ---------------------------------------------------------------
    # Sort chronologically
    # ---------------------------------------------------------------

    df = df.sort_values(
        "timestamp"
    )

    # ---------------------------------------------------------------
    # Remove duplicate timestamps
    # ---------------------------------------------------------------

    df = df.drop_duplicates(
        subset=["timestamp"],
        keep="last",
    )

    # ---------------------------------------------------------------
    # Reset row index
    # ---------------------------------------------------------------

    df = df.reset_index(drop=True)

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