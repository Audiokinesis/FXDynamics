from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd
from pandas_datareader import data as web


class FREDProvider:
    """
    Provider for Federal Reserve Economic Data.

    Designed for point-observation macroeconomic series such as
    Treasury yields.
    """

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)

    def download(
        self,
        series_id: str,
        start: str | datetime,
        end: str | datetime | None,
        instrument: str,
    ) -> pd.DataFrame:

        print(
            f"Downloading FRED: "
            f"{instrument} "
            f"({series_id}) "
            f"[{start} -> {end}]"
        )

        if end is None:
            end = pd.Timestamp.now(
                tz="UTC"
            ).strftime("%Y-%m-%d")

        df = web.DataReader(
            series_id,
            "fred",
            start,
            end,
        )

        if df.empty:
            raise ValueError(
                f"No FRED data returned for {series_id}"
            )

        df = df.reset_index()

        # Normalize date column
        df = df.rename(
            columns={
                "DATE": "timestamp",
                series_id: "close",
            }
        )

        df["timestamp"] = pd.to_datetime(
            df["timestamp"],
            utc=True,
        )

        # FRED Treasury yields are point observations,
        # not OHLC market candles.
        df["open"] = df["close"]
        df["high"] = df["close"]
        df["low"] = df["close"]
        df["volume"] = 0

        df["instrument"] = instrument
        df["data_type"] = "yield"
        df["provider"] = "fred"

        # Conservative initial availability rule.
        #
        # We will refine release-time handling later.
        df["available_at"] = (
            df["timestamp"]
            + pd.Timedelta(days=1)
        )

        df = df[
            [
                "timestamp",
                "available_at",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "instrument",
                "data_type",
                "provider",
            ]
        ]

        df = df.sort_values(
            "timestamp"
        )

        df = df.drop_duplicates(
            subset=["timestamp"],
            keep="last",
        )

        df = df.reset_index(
            drop=True
        )

        return df

    def save_raw(
        self,
        df: pd.DataFrame,
        instrument: str,
    ) -> Path:

        path = (
            self.output_dir
            / instrument
            / f"{instrument}_1d_raw.parquet"
        )

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        df.to_parquet(
            path,
            index=False,
        )

        print(
            f"Saved {len(df):,} rows -> {path}"
        )

        return path