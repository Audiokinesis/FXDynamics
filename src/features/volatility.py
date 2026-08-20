from __future__ import annotations

import pandas as pd


def add_rolling_volatility(
    df: pd.DataFrame,
) -> pd.DataFrame:

    df = df.copy()

    # ---------------------------------------------------------------
    # EURUSD volatility
    # ---------------------------------------------------------------

    df["EURUSD_vol_12"] = (
        df["EURUSD_ret_1"]
        .rolling(12)
        .std()
    )

    df["EURUSD_vol_48"] = (
        df["EURUSD_ret_1"]
        .rolling(48)
        .std()
    )

    df["EURUSD_vol_288"] = (
        df["EURUSD_ret_1"]
        .rolling(288)
        .std()
    )

    # 288 x 5 minutes = 24 hours

    # ---------------------------------------------------------------
    # DXY volatility
    # ---------------------------------------------------------------

    df["DXY_vol_12"] = (
        df["DXY_ret_1"]
        .rolling(12)
        .std()
    )

    df["DXY_vol_48"] = (
        df["DXY_ret_1"]
        .rolling(48)
        .std()
    )

    df["DXY_vol_288"] = (
        df["DXY_ret_1"]
        .rolling(288)
        .std()
    )

    return df