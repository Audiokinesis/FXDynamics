from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.data.point_in_time import load_processed
from src.data.build_base_dataset import build_base_dataset

from .targets import add_next_return_target
from .returns import add_price_returns
from .volatility import add_rolling_volatility
from .cross_market import add_cross_market_features
from .rates import build_rate_features


PROJECT_ROOT = Path(r"C:\Users\mdesc\Documents\Projects\FXDynamics\src\features\build_features.py").resolve().parents[2]



def build_features(
    base_dataset: pd.DataFrame,
) -> pd.DataFrame:

    df = base_dataset.copy()

    df = df.sort_values(
        "prediction_time"
    ).reset_index(drop=True)

    # ---------------------------------------------------------------
    # Target
    # ---------------------------------------------------------------

    df = add_next_return_target(df)

    # ---------------------------------------------------------------
    # Price returns
    # ---------------------------------------------------------------

    df = add_price_returns(df)

    # ---------------------------------------------------------------
    # Rolling volatility
    # ---------------------------------------------------------------

    df = add_rolling_volatility(df)

    # ---------------------------------------------------------------
    # Cross-market interactions
    # ---------------------------------------------------------------

    df = add_cross_market_features(df)

    # ---------------------------------------------------------------
    # Native Treasury features
    # ---------------------------------------------------------------

    us2y = load_processed(
        "US2Y",
        "1d",
    )

    us10y = load_processed(
        "US10Y",
        "1d",
    )

    rates = build_rate_features(
        us2y,
        us10y,
    )

    # ---------------------------------------------------------------
    # Point-in-time rate join
    # ---------------------------------------------------------------

    rate_columns = [
        "available_at",
        "US2Y_yield",
        "US2Y_change_1d",
        "US2Y_change_5d",
        "US10Y_yield",
        "US10Y_change_1d",
        "US10Y_change_5d",
        "US10Y_US2Y_spread",
        "US10Y_US2Y_spread_change",
    ]

    rate_features = rates[
        rate_columns
    ].sort_values(
        "available_at"
    )

    df = pd.merge_asof(
        df.sort_values("prediction_time"),
        rate_features,
        left_on="prediction_time",
        right_on="available_at",
        direction="backward",
    )

    # The rate-side availability timestamp is only needed during
    # validation and can be renamed for clarity.
    df = df.rename(
        columns={
            "available_at": "rates_available_at"
        }
    )

    return df.reset_index(drop=True)


if __name__ == "__main__":

    base = build_base_dataset()

    features = build_features(
        base
    )


    output_dir = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "features"
    )

    output_dir.mkdir(
    parents=True,
    exist_ok=True,
    )

    features.to_parquet(
    output_dir
    / "EURUSD_feature_matrix_5m.parquet",
    index=False,
    )

    print(
        features.tail(10).to_string(
            index=False
        )
    )

    print("\nFeature count:")
    print(len(features.columns))

    print(
    features[
        [
            "prediction_time",
            "rates_available_at",
            "US2Y_yield",
            "US2Y_change_1d",
            "US10Y_yield",
            "US10Y_change_1d",
            "US10Y_US2Y_spread",
        ]
    ].tail(20).to_string(index=False)
    )
    violations = features[
    features["rates_available_at"]
    > features["prediction_time"]
    ]

    print("Rate leakage rows:", len(violations))

    from src.features.quality import feature_quality_report

    report = feature_quality_report(
        features,
        "target_next_5m_return",
    )

    print(
        report.to_string(index=False)
    )