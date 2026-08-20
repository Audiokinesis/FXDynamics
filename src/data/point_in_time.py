from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROCESSED_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
)


def load_processed(
    instrument: str,
    timeframe: str,
) -> pd.DataFrame:
    """
    Load a processed dataset.
    """

    path = (
        PROCESSED_DIR
        / instrument
        / f"{instrument}_{timeframe}.parquet"
    )

    if not path.exists():
        raise FileNotFoundError(
            f"Processed dataset not found: {path}"
        )

    df = pd.read_parquet(path)

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        utc=True,
    )

    df["available_at"] = pd.to_datetime(
        df["available_at"],
        utc=True,
    )

    return df.sort_values(
        "available_at"
    ).reset_index(drop=True)


def prepare_feature_dataset(
    df: pd.DataFrame,
    instrument: str,
) -> pd.DataFrame:
    """
    Select and rename the fields needed for a point-in-time join.
    """

    prefix = instrument

    columns = [
        "available_at",
        "timestamp",
        "open",
        "high",
        "low",
        "close",
        "volume",
    ]

    available_columns = [
        c for c in columns
        if c in df.columns
    ]

    result = df[available_columns].copy()

    result = result.rename(
        columns={
            "timestamp": f"{prefix}_timestamp",
            "available_at": f"{prefix}_available_at",
            "open": f"{prefix}_open",
            "high": f"{prefix}_high",
            "low": f"{prefix}_low",
            "close": f"{prefix}_close",
            "volume": f"{prefix}_volume",
        }
    )

    return result.sort_values(
        f"{prefix}_available_at"
    )


def point_in_time_join(
    prediction_df: pd.DataFrame,
    feature_df: pd.DataFrame,
    feature_name: str,
) -> pd.DataFrame:
    """
    Attach the latest feature observation whose available_at
    is less than or equal to the prediction timestamp.
    """

    prediction = prediction_df.copy()

    feature = prepare_feature_dataset(
        feature_df,
        feature_name,
    )

    prediction = prediction.sort_values(
        "prediction_time"
    )

    result = pd.merge_asof(
        prediction,
        feature,
        left_on="prediction_time",
        right_on=f"{feature_name}_available_at",
        direction="backward",
    )

    return result