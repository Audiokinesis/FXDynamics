from __future__ import annotations

import numpy as np
import pandas as pd


def add_next_return_target(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Create the next 5-minute EURUSD log-return target.

    The current EURUSD close is known at prediction_time.
    The next candle's close is the future outcome.
    """

    df = df.copy()

    df = df.sort_values(
        "prediction_time"
    ).reset_index(drop=True)

    df["target_next_5m_return"] = (
        np.log(
            df["EURUSD_close"].shift(-1)
            / df["EURUSD_close"]
        )
    )

    return df