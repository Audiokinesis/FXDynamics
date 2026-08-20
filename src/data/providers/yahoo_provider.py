from __future__ import annotations

from pathlib import Path

import pandas as pd
import yfinance as yf


class YahooDownloader:
    """
    Yahoo Finance market-data provider.

    Responsible only for obtaining raw market data and converting
    it into the canonical FXDynamics schema.

    The provider does NOT:
        - perform feature engineering
        - calculate returns
        - detect regimes
        - remove bad historical observations
        - train models

    Those responsibilities belong to later pipeline stages.
    """

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)

    def download(
        self,
        symbol: str,
        instrument: str,
        interval: str,
        period: str,
        data_type: str = "price",
    ) -> pd.DataFrame:
        """
        Download data from Yahoo Finance.

        Parameters
        ----------
        symbol:
            Yahoo Finance ticker, e.g. EURUSD=X or DX-Y.NYB.

        instrument:
            Internal FXDynamics name, e.g. EURUSD or DXY.

        interval:
            Yahoo interval such as 5m, 15m, 1h, or 1d.

        period:
            Yahoo historical period.

        data_type:
            Semantic type of the series:
                price
                index
                yield

        Returns
        -------
        pd.DataFrame
            Canonical raw market-data dataframe.
        """

        print(
            f"Downloading Yahoo Finance: "
            f"{instrument} "
            f"({symbol}) "
            f"[{interval}, {period}]"
        )

        data = yf.download(
            tickers=symbol,
            period=period,
            interval=interval,
            auto_adjust=False,
            progress=False,
        )

        if data.empty:
            raise ValueError(
                f"No data returned by Yahoo Finance for "
                f"{instrument} ({symbol})"
            )

        # -----------------------------------------------------------
        # Flatten Yahoo's MultiIndex columns if present
        # -----------------------------------------------------------

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = [
                column[0]
                if isinstance(column, tuple)
                else column
                for column in data.columns
            ]

        # -----------------------------------------------------------
        # Reset DatetimeIndex into a normal column
        # -----------------------------------------------------------

        data = data.reset_index()

        # -----------------------------------------------------------
        # Normalize column names
        # -----------------------------------------------------------

        data.columns = [
            str(column)
            .strip()
            .lower()
            .replace(" ", "_")
            for column in data.columns
        ]

        # Yahoo normally returns Datetime.
        # Some datasets may return Date.
        timestamp_candidates = [
            "timestamp",
            "datetime",
            "date",
        ]

        timestamp_column = next(
            (
                column
                for column in timestamp_candidates
                if column in data.columns
            ),
            None,
        )

        if timestamp_column is None:
            raise ValueError(
                "Could not identify Yahoo timestamp column. "
                f"Available columns: {list(data.columns)}"
            )

        if timestamp_column != "timestamp":
            data = data.rename(
                columns={
                    timestamp_column: "timestamp"
                }
            )

        # -----------------------------------------------------------
        # Convert timestamp to UTC
        # -----------------------------------------------------------

        data["timestamp"] = pd.to_datetime(
            data["timestamp"],
            utc=True,
        )

        # -----------------------------------------------------------
        # Verify OHLC columns
        # -----------------------------------------------------------

        required_price_columns = [
            "open",
            "high",
            "low",
            "close",
        ]

        missing_columns = [
            column
            for column in required_price_columns
            if column not in data.columns
        ]

        if missing_columns:
            raise ValueError(
                f"Yahoo data is missing required columns: "
                f"{missing_columns}"
            )

        # -----------------------------------------------------------
        # Yahoo FX/index data may not have meaningful volume.
        # Preserve the field when present, otherwise set to zero.
        # -----------------------------------------------------------

        if "volume" not in data.columns:
            data["volume"] = 0

        # -----------------------------------------------------------
        # Add semantic metadata
        # -----------------------------------------------------------

        data["instrument"] = instrument
        data["data_type"] = data_type
        data["provider"] = "yahoo"

        # -----------------------------------------------------------
        # Initial availability timestamp
        #
        # For an individual candle:
        #
        #     timestamp = candle start
        #
        #     available_at = candle start + candle duration
        #
        # This is refined by the pipeline for resampled candles.
        # -----------------------------------------------------------

        interval_minutes = self._interval_to_minutes(
            interval
        )

        data["available_at"] = (
            data["timestamp"]
            + pd.Timedelta(
                minutes=interval_minutes
            )
        )

        # -----------------------------------------------------------
        # Canonical schema
        # -----------------------------------------------------------

        data = data[
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

        # -----------------------------------------------------------
        # Sort and deduplicate
        # -----------------------------------------------------------

        data = data.sort_values(
            "timestamp"
        )

        data = data.drop_duplicates(
            subset=["timestamp"],
            keep="last",
        )

        data = data.reset_index(
            drop=True
        )

        return data

    def save_raw(
        self,
        data: pd.DataFrame,
        instrument: str,
        timeframe: str,
    ) -> Path:
        """
        Save provider output as raw Parquet.

        The raw provider output should remain unchanged after this
        step so that it can be reproduced or investigated later.
        """

        output_path = (
            self.output_dir
            / instrument
            / f"{instrument}_{timeframe}_raw.parquet"
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        data.to_parquet(
            output_path,
            index=False,
        )

        print(
            f"Saved {len(data):,} rows → "
            f"{output_path}"
        )

        return output_path

    @staticmethod
    def _interval_to_minutes(
        interval: str,
    ) -> int:
        """
        Convert Yahoo interval notation to minutes.
        """

        mapping = {
            "1m": 1,
            "2m": 2,
            "5m": 5,
            "15m": 15,
            "30m": 30,
            "60m": 60,
            "90m": 90,
            "1h": 60,
            "1d": 1440,
        }

        if interval not in mapping:
            raise ValueError(
                f"Unsupported Yahoo interval: {interval}"
            )

        return mapping[interval]