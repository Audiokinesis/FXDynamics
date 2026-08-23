from __future__ import annotations

import pandas as pd


EURUSD_FEATURES = [
    "EURUSD_ret_1",
    "EURUSD_ret_3",
    "EURUSD_ret_12",
    "EURUSD_ret_48",

    "EURUSD_vol_12",
    "EURUSD_vol_48",
    "EURUSD_vol_288",

    "EURUSD_return_to_vol",
]


CROSS_MARKET_FEATURES = EURUSD_FEATURES + [
    "DXY_ret_1",
    "DXY_ret_3",
    "DXY_ret_12",
    "DXY_ret_48",

    "DXY_vol_12",
    "DXY_vol_48",
    "DXY_vol_288",

    "EURUSD_DXY_ret_product",
    "EURUSD_DXY_ret_difference",
    "EURUSD_DXY_momentum_product",

    "US2Y_yield",
    "US2Y_change_1d",
    "US2Y_change_5d",

    "US10Y_yield",
    "US10Y_change_1d",
    "US10Y_change_5d",

    "US10Y_US2Y_spread",
    "US10Y_US2Y_spread_change",
]


def validate_features(
    df: pd.DataFrame,
    features: list[str],
) -> None:

    missing = [
        feature
        for feature in features
        if feature not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing feature columns: {missing}"
        )