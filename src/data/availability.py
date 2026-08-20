import pandas as pd


TIMEFRAME_MINUTES = {
    "5m": 5,
    "15m": 15,
    "1h": 60,
    "4h": 240,
    "1d": 1440,
}


def add_available_at(
    df: pd.DataFrame,
    timeframe: str,
) -> pd.DataFrame:
    """
    Add the timestamp at which a completed candle becomes known.
    """

    if timeframe not in TIMEFRAME_MINUTES:
        raise ValueError(
            f"Unknown timeframe: {timeframe}"
        )

    df = df.copy()

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        utc=True,
    )

    minutes = TIMEFRAME_MINUTES[timeframe]

    df["available_at"] = (
        df["timestamp"]
        + pd.Timedelta(
            minutes=minutes
        )
    )

    return df