from pathlib import Path

import yfinance as yf

from .config import RAW_DATA_DIR


def download_market_data(
    instrument_name: str,
    provider_symbol: str,
    interval: str,
    period: str = "max",
) -> Path:
    """
    Download market data from Yahoo Finance and save it as Parquet.

    Parameters
    ----------
    instrument_name:
        Our internal instrument name, e.g. EURUSD.

    provider_symbol:
        Symbol used by the external data provider.

    interval:
        Yahoo Finance interval, e.g. 1h, 1d.

    period:
        Historical period requested from the provider.

    Returns
    -------
    Path
        Path to the saved raw Parquet file.
    """

    output_directory = RAW_DATA_DIR / instrument_name
    output_directory.mkdir(parents=True, exist_ok=True)

    print(
        f"Downloading {instrument_name} "
        f"({provider_symbol}) [{interval}]..."
    )

    data = yf.download(
        tickers=provider_symbol,
        period=period,
        interval=interval,
        auto_adjust=False,
        progress=False,
    )

    if data.empty:
        raise RuntimeError(
            f"No data returned for {instrument_name} "
            f"({provider_symbol}) [{interval}]"
        )

    output_path = (
        output_directory
        / f"{instrument_name}_{interval}.parquet"
    )

    data.to_parquet(output_path)

    print(f"Saved: {output_path}")

    return output_path