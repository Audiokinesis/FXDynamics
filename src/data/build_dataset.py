from pathlib import Path

import pandas as pd

from .align import load_processed


PROJECT_ROOT = Path(r"C:\Users\mdesc\Documents\Projects\FXDynamics\src\data\build_dataset.py").resolve().parents[2]

PROCESSED = PROJECT_ROOT / "data" / "processed"


def build_base_dataset() -> pd.DataFrame:

    eurusd = load_processed(
        PROCESSED
        / "EURUSD"
        / "EURUSD_5m.parquet"
    )

    dxy = load_processed(
        PROCESSED
        / "DXY"
        / "DXY_5m.parquet"
    )

    us2y = load_processed(
        PROCESSED
        / "US2Y"
        / "US2Y_1d.parquet"
    )

    us10y = load_processed(
        PROCESSED
        / "US10Y"
        / "US10Y_1d.parquet"
    )

    # ---------------------------------------------------------------
    # EURUSD becomes the prediction clock.
    # ---------------------------------------------------------------

    dataset = eurusd[
        [
            "timestamp",
            "available_at",
            "open",
            "high",
            "low",
            "close",
        ]
    ].copy()

    dataset = dataset.rename(
        columns={
            "open": "EURUSD_open",
            "high": "EURUSD_high",
            "low": "EURUSD_low",
            "close": "EURUSD_close",
        }
    )

    # ---------------------------------------------------------------
    # DXY
    # ---------------------------------------------------------------

    dxy_features = dxy[
        [
            "available_at",
            "close",
        ]
    ].rename(
        columns={
            "close": "DXY_close",
        }
    )

    dataset = pd.merge_asof(
        dataset.sort_values("timestamp"),
        dxy_features.sort_values("available_at"),
        left_on="timestamp",
        right_on="available_at",
        direction="backward",
    )

    dataset = dataset.drop(
        columns=["available_at_y"],
        errors="ignore",
    )

    dataset = dataset.rename(
        columns={
            "available_at_x": "EURUSD_available_at"
        }
    )

    # ---------------------------------------------------------------
    # US2Y
    # ---------------------------------------------------------------

    us2y_features = us2y[
        [
            "available_at",
            "close",
        ]
    ].rename(
        columns={
            "close": "US2Y_yield",
        }
    )

    dataset = pd.merge_asof(
        dataset.sort_values("timestamp"),
        us2y_features.sort_values("available_at"),
        left_on="timestamp",
        right_on="available_at",
        direction="backward",
    )

    dataset = dataset.drop(
        columns=["available_at"],
        errors="ignore",
    )

    # ---------------------------------------------------------------
    # US10Y
    # ---------------------------------------------------------------

    us10y_features = us10y[
        [
            "available_at",
            "close",
        ]
    ].rename(
        columns={
            "close": "US10Y_yield",
        }
    )

    dataset = pd.merge_asof(
        dataset.sort_values("timestamp"),
        us10y_features.sort_values("available_at"),
        left_on="timestamp",
        right_on="available_at",
        direction="backward",
    )

    dataset = dataset.drop(
        columns=["available_at"],
        errors="ignore",
    )

    return dataset.sort_values(
        "timestamp"
    ).reset_index(drop=True)


if __name__ == "__main__":

    df = build_base_dataset()

    print(
        df.head(20).to_string(index=False)
    )

    print("\nColumns:")
    print(df.columns.tolist())