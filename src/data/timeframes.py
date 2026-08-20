from dataclasses import dataclass


@dataclass(frozen=True)
class Timeframe:
    name: str
    minutes: int
    provider_interval: str
    resample_rule: str | None = None


TIMEFRAME_DEFINITIONS = {

    "5m": Timeframe(
        name="5m",
        minutes=5,
        provider_interval="5m",
    ),

    "15m": Timeframe(
        name="15m",
        minutes=15,
        provider_interval="15m",
    ),

    "1h": Timeframe(
        name="1h",
        minutes=60,
        provider_interval="1h",
    ),

    "4h": Timeframe(
        name="4h",
        minutes=240,
        provider_interval="1h",
        resample_rule="4h",
    ),

    "1d": Timeframe(
        name="1d",
        minutes=1440,
        provider_interval="1d",
    ),
}