from pathlib import Path

from .fred_provider import FREDProvider
from .yahoo_provider import YahooDownloader


def create_provider(
    provider_name: str,
    output_dir: Path,
):
    """
    Create the appropriate market-data provider.
    """

    provider_name = provider_name.lower()

    if provider_name == "yahoo":
        return YahooDownloader(output_dir)

    if provider_name == "fred":
        return FREDProvider(output_dir)

    raise ValueError(
        f"Unsupported provider: {provider_name}"
    )