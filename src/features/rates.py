from __future__ import annotations

import pandas as pd


def build_rate_features(
    us2y: pd.DataFrame,
    us10y: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build native-frequency Treasury features.

    Rate changes are calculated BEFORE the data is joined to the
    5-minute EURUSD prediction clock. This prevents repeatedly
    calculating daily changes after forward-filling the rates.
    """

    us2y = us2y.copy()
    us10y = us10y.copy()

    # ---------------------------------------------------------------
    # Normalize timestamps
    # ---------------------------------------------------------------

    for df in (us2y, us10y):

        df["timestamp"] = pd.to_datetime(
            df["timestamp"],
            utc=True,
        )

        df["available_at"] = pd.to_datetime(
            df["available_at"],
            utc=True,
        )

    # ---------------------------------------------------------------
    # Sort chronologically
    # ---------------------------------------------------------------

    us2y = us2y.sort_values("timestamp").reset_index(drop=True)
    us10y = us10y.sort_values("timestamp").reset_index(drop=True)

    # ---------------------------------------------------------------
    # US 2Y
    # ---------------------------------------------------------------

    us2y["US2Y_change_1d"] = (
        us2y["close"].diff(1)
    )

    us2y["US2Y_change_5d"] = (
        us2y["close"].diff(5)
    )

    # ---------------------------------------------------------------
    # US 10Y
    # ---------------------------------------------------------------

    us10y["US10Y_change_1d"] = (
        us10y["close"].diff(1)
    )

    us10y["US10Y_change_5d"] = (
        us10y["close"].diff(5)
    )

    # ---------------------------------------------------------------
    # Select fields
    # ---------------------------------------------------------------

    us2y = us2y[
        [
            "timestamp",
            "available_at",
            "close",
            "US2Y_change_1d",
            "US2Y_change_5d",
        ]
    ].rename(
        columns={
            "close": "US2Y_yield",
        }
    )

    us10y = us10y[
        [
            "timestamp",
            "available_at",
            "close",
            "US10Y_change_1d",
            "US10Y_change_5d",
        ]
    ].rename(
        columns={
            "close": "US10Y_yield",
        }
    )

    # ---------------------------------------------------------------
    # Point-in-time merge the native daily rates
    # ---------------------------------------------------------------

    rates = pd.merge_asof(
        us2y.sort_values("available_at"),
        us10y.sort_values("available_at"),
        on="available_at",
        direction="backward",
        suffixes=("", "_10Y"),
    )

    # ---------------------------------------------------------------
    # Treasury curve
    # ---------------------------------------------------------------

    rates["US10Y_US2Y_spread"] = (
        rates["US10Y_yield"]
        - rates["US2Y_yield"]
    )

    rates["US10Y_US2Y_spread_change"] = (
        rates["US10Y_US2Y_spread"].diff()
    )

    return rates.reset_index(drop=True)