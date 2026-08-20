from __future__ import annotations

import numpy as np
import pandas as pd


def add_price_returns(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Add log-return features for EURUSD and DXY.
    """

    df = df.copy()

    # ---------------------------------------------------------------
    # EURUSD
    # ---------------------------------------------------------------

    df["EURUSD_ret_1"] = np.log(
        df["EURUSD_close"]
        / df["EURUSD_close"].shift(1)
    )

    df["EURUSD_ret_3"] = np.log(
        df["EURUSD_close"]
        / df["EURUSD_close"].shift(3)
    )

    df["EURUSD_ret_12"] = np.log(
        df["EURUSD_close"]
        / df["EURUSD_close"].shift(12)
    )

    df["EURUSD_ret_48"] = np.log(
        df["EURUSD_close"]
        / df["EURUSD_close"].shift(48)
    )

    # ---------------------------------------------------------------
    # DXY
    # ---------------------------------------------------------------

    df["DXY_ret_1"] = np.log(
        df["DXY_close"]
        / df["DXY_close"].shift(1)
    )

    df["DXY_ret_3"] = np.log(
        df["DXY_close"]
        / df["DXY_close"].shift(3)
    )

    df["DXY_ret_12"] = np.log(
        df["DXY_close"]
        / df["DXY_close"].shift(12)
    )

    df["DXY_ret_48"] = np.log(
        df["DXY_close"]
        / df["DXY_close"].shift(48)
    )

    return df