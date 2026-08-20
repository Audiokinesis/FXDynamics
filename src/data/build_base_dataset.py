from __future__ import annotations

from pathlib import Path

import pandas as pd

from .point_in_time import (
    load_processed,
    point_in_time_join,
)


PROJECT_ROOT = Path(r"C:\Users\mdesc\Documents\Projects\FXDynamics\src\data\build_base_dataset.py").resolve().parents[2]


def build_base_dataset() -> pd.DataFrame:

    # ---------------------------------------------------------------
    # EURUSD 5-minute candles
    # ---------------------------------------------------------------

    eurusd = load_processed(
        "EURUSD",
        "5m",
    )

    # A completed EURUSD candle becomes available at
    # available_at. That becomes our prediction clock.
    dataset = eurusd[
        [
            "timestamp",
            "available_at",
            "open",
            "high",
            "low",
            "close",
            "volume",
        ]
    ].copy()

    dataset = dataset.rename(
        columns={
            "timestamp": "EURUSD_timestamp",
            "available_at": "EURUSD_available_at",
            "open": "EURUSD_open",
            "high": "EURUSD_high",
            "low": "EURUSD_low",
            "close": "EURUSD_close",
            "volume": "EURUSD_volume",
        }
    )

    dataset["prediction_time"] = (
        dataset["EURUSD_available_at"]
    )

    dataset = dataset.sort_values(
        "prediction_time"
    )

    # ---------------------------------------------------------------
    # DXY 5-minute
    # ---------------------------------------------------------------

    dxy = load_processed(
        "DXY",
        "5m",
    )

    dataset = point_in_time_join(
        dataset,
        dxy,
        "DXY",
    )

    # ---------------------------------------------------------------
    # US2Y daily
    # ---------------------------------------------------------------

    us2y = load_processed(
        "US2Y",
        "1d",
    )

    dataset = point_in_time_join(
        dataset,
        us2y,
        "US2Y",
    )

    # ---------------------------------------------------------------
    # US10Y daily
    # ---------------------------------------------------------------

    us10y = load_processed(
        "US10Y",
        "1d",
    )

    dataset = point_in_time_join(
        dataset,
        us10y,
        "US10Y",
    )

    return dataset.sort_values(
        "prediction_time"
    ).reset_index(drop=True)


if __name__ == "__main__":

    df = build_base_dataset()

    print("=" * 100)
    print("POINT-IN-TIME DATASET")
    print("=" * 100)

    print(
        df.tail(20).to_string(index=False)
    )

    print("\nColumns:")
    print(df.columns.tolist())

    print("\nShape:")
    print(df.shape)

#from .leakage import check_point_in_time_integrity

#integrity = check_point_in_time_integrity(
#    df
#   )

#print("\nPoint-in-time integrity:")
#print(integrity)

