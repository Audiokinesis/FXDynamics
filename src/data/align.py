from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_processed(path: str | Path) -> pd.DataFrame:
    """
    Load a processed Parquet dataset and enforce UTC timestamps.
    """

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
        "timestamp"
    ).reset_index(drop=True)


def prepare_features(
    df: pd.DataFrame,
    prefix: str,
    ) -> pd.DataFrame:
    """
    Rename feature columns with an instrument prefix.
    """

    df = df.copy()

    keep_columns = [
        "available_at",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "instrument",
        "data_type",
    ]

    df = df[
        [
            column
            for column in keep_columns
            if column in df.columns
        ]
    ]

    rename_map = {
        column: f"{prefix}_{column}"
        for column in df.columns
        if column != "available_at"
    }

    df = df.rename(
        columns=rename_map
    )

    return df.sort_values(
        "available_at"
    )

def asof_join(
    prediction_df: pd.DataFrame,
    feature_df: pd.DataFrame,
    ) -> pd.DataFrame:

    prediction = prediction_df.copy()

    prediction = prediction.sort_values(
        "timestamp"
    )

    features = prepare_features(
        feature_df,
        feature_df["instrument"].iloc[0],
    )

    result = pd.merge_asof(
        prediction,
        features,
        left_on="timestamp",
        right_on="available_at",
        direction="backward",
    )

    return result