from __future__ import annotations

import pandas as pd


def add_cross_market_features(
    df: pd.DataFrame,
) -> pd.DataFrame:

    df = df.copy()

    # ---------------------------------------------------------------
    # EURUSD vs DXY
    # ---------------------------------------------------------------

    df["EURUSD_DXY_ret_product"] = (
        df["EURUSD_ret_1"]
        * df["DXY_ret_1"]
    )

    df["EURUSD_DXY_ret_difference"] = (
        df["EURUSD_ret_1"]
        - df["DXY_ret_1"]
    )

    # ---------------------------------------------------------------
    # EURUSD / volatility relationships
    # ---------------------------------------------------------------

    df["EURUSD_return_to_vol"] = (
        df["EURUSD_ret_1"]
        / df["EURUSD_vol_48"]
    )

    # ---------------------------------------------------------------
    # USD strength relative to EURUSD movement
    # ---------------------------------------------------------------

    df["EURUSD_DXY_momentum_product"] = (
        df["EURUSD_ret_12"]
        * df["DXY_ret_12"]
    )

    return df