from pathlib import Path

import yfinance as yf


def download_market_data(
    instrument_name: str,
    provider_symbol: str,
    interval: str,
    period: str,
    output_path: Path,
) -> Path:

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    print(
        f"Downloading "
        f"{instrument_name} "
        f"[{interval}] "
        f"period={period}"
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
            f"No data returned for "
            f"{instrument_name} "
            f"[{interval}]"
        )

    data.to_parquet(
        output_path
    )

    print(
        f"Saved {len(data):,} rows → "
        f"{output_path}"
    )

    return output_path