from __future__ import annotations

import numpy as np
import pandas as pd


def add_market_features(
    df: pd.DataFrame,
    prefix: str,
) -> pd.DataFrame:
    """
    Calculate features on the instrument's native timeframe.

    Features are calculated BEFORE point-in-time joining with the
    EURUSD prediction clock.
    """

    df = df.copy()

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        utc=True,
    )

    df["available_at"] = pd.to_datetime(
        df["available_at"],
        utc=True,
    )

    df = df.sort_values(
        "timestamp"
    ).reset_index(drop=True)

    close = df["close"]

    # ---------------------------------------------------------------
    # Log returns
    # ---------------------------------------------------------------

    df[f"{prefix}_ret_1"] = np.log(
        close / close.shift(1)
    )

    df[f"{prefix}_ret_3"] = np.log(
        close / close.shift(3)
    )

    df[f"{prefix}_ret_12"] = np.log(
        close / close.shift(12)
    )

    df[f"{prefix}_ret_48"] = np.log(
        close / close.shift(48)
    )

    # ---------------------------------------------------------------
    # Rolling volatility
    #
    # min_periods prevents us from pretending a partially populated
    # rolling window is equivalent to a complete window.
    # ---------------------------------------------------------------

    df[f"{prefix}_vol_12"] = (
        df[f"{prefix}_ret_1"]
        .rolling(
            window=12,
            min_periods=12,
        )
        .std()
    )

    df[f"{prefix}_vol_48"] = (
        df[f"{prefix}_ret_1"]
        .rolling(
            window=48,
            min_periods=48,
        )
        .std()
    )

    df[f"{prefix}_vol_288"] = (
        df[f"{prefix}_ret_1"]
        .rolling(
            window=288,
            min_periods=288,
        )
        .std()
    )

    # ---------------------------------------------------------------
    # Data availability / age
    # ---------------------------------------------------------------

    df[f"{prefix}_timestamp_gap_minutes"] = (
        df["timestamp"]
        .diff()
        .dt.total_seconds()
        .div(60)
    )

    return df