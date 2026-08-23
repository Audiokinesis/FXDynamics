from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(r"C:\Users\mdesc\Documents\Projects\FXDynamics\src\features\diagnose_dxy.py").resolve().parents[2]

PROCESSED = (
    PROJECT_ROOT
    / "data"
    / "processed"
)


def load(instrument: str, timeframe: str) -> pd.DataFrame:

    path = (
        PROCESSED
        / instrument
        / f"{instrument}_{timeframe}.parquet"
    )

    df = pd.read_parquet(path)

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        utc=True,
    )

    df["available_at"] = pd.to_datetime(
        df["available_at"],
        utc=True,
    )

    return df.sort_values("timestamp").reset_index(drop=True)


def diagnose():

    eurusd = load("EURUSD", "5m")
    dxy = load("DXY", "5m")

    print("=" * 80)
    print("1. BASIC COVERAGE")
    print("=" * 80)

    for name, df in [
        ("EURUSD", eurusd),
        ("DXY", dxy),
    ]:

        print(f"\n{name}")

        print("Rows: ", len(df))
        print("Start:", df["timestamp"].min())
        print("End:  ", df["timestamp"].max())

    # ---------------------------------------------------------------
    # Coverage overlap
    # ---------------------------------------------------------------

    overlap_start = max(
        eurusd["timestamp"].min(),
        dxy["timestamp"].min(),
    )

    overlap_end = min(
        eurusd["timestamp"].max(),
        dxy["timestamp"].max(),
    )

    print("\n" + "=" * 80)
    print("2. OVERLAP")
    print("=" * 80)

    print("Overlap start:", overlap_start)
    print("Overlap end:  ", overlap_end)

    eur_overlap = eurusd[
        (eurusd["timestamp"] >= overlap_start)
        & (eurusd["timestamp"] <= overlap_end)
    ]

    dxy_overlap = dxy[
        (dxy["timestamp"] >= overlap_start)
        & (dxy["timestamp"] <= overlap_end)
    ]

    print("\nEURUSD overlap rows:", len(eur_overlap))
    print("DXY overlap rows:   ", len(dxy_overlap))

    # ---------------------------------------------------------------
    # Exact timestamp coverage
    # ---------------------------------------------------------------

    eur_times = set(
        eur_overlap["timestamp"]
    )

    dxy_times = set(
        dxy_overlap["timestamp"]
    )

    missing_dxy = sorted(
        eur_times - dxy_times
    )

    print("\n" + "=" * 80)
    print("3. EXACT TIMESTAMP COVERAGE")
    print("=" * 80)

    print(
        "EURUSD timestamps:",
        len(eur_times),
    )

    print(
        "DXY timestamps:",
        len(dxy_times),
    )

    print(
        "EURUSD timestamps without DXY:",
        len(missing_dxy),
    )

    if missing_dxy:

        print("\nFirst 30 missing DXY timestamps:")

        for ts in missing_dxy[:30]:
            print(ts)

    # ---------------------------------------------------------------
    # Group missing observations by date
    # ---------------------------------------------------------------

    missing_df = pd.DataFrame(
        {
            "timestamp": missing_dxy
        }
    )

    if not missing_df.empty:

        missing_df["date"] = (
            missing_df["timestamp"]
            .dt.date
        )

        daily_missing = (
            missing_df
            .groupby("date")
            .size()
            .sort_values(
                ascending=False
            )
        )

        print("\n" + "=" * 80)
        print("4. MISSING DXY BY DATE")
        print("=" * 80)

        print(
            daily_missing.to_string()
        )

    # ---------------------------------------------------------------
    # DXY hours
    # ---------------------------------------------------------------

    dxy["hour"] = (
        dxy["timestamp"].dt.hour
    )

    dxy["weekday"] = (
        dxy["timestamp"]
        .dt.day_name()
    )

    print("\n" + "=" * 80)
    print("5. DXY OBSERVATIONS BY HOUR")
    print("=" * 80)

    print(
        dxy.groupby("hour")
           .size()
           .to_string()
    )

    print("\n" + "=" * 80)
    print("6. DXY OBSERVATIONS BY WEEKDAY")
    print("=" * 80)

    print(
        dxy.groupby("weekday")
           .size()
           .to_string()
    )

    # ---------------------------------------------------------------
    # Sample EURUSD rows with missing DXY
    # ---------------------------------------------------------------

    if missing_dxy:

        sample_times = missing_dxy[:20]

        sample = eurusd[
            eurusd["timestamp"].isin(
                sample_times
            )
        ]

        print("\n" + "=" * 80)
        print("7. EURUSD ROWS WHERE DXY IS ABSENT")
        print("=" * 80)

        print(
            sample[
                [
                    "timestamp",
                    "available_at",
                    "close",
                ]
            ].to_string(index=False)
        )

    # ---------------------------------------------------------------
    # DXY gaps
    # ---------------------------------------------------------------

    dxy_gap = (
        dxy["timestamp"]
        .diff()
        .dt.total_seconds()
        / 60
    )

    print("\n" + "=" * 80)
    print("8. LARGEST DXY TIMESTAMP GAPS")
    print("=" * 80)

    gaps = (
        pd.DataFrame(
            {
                "timestamp": dxy["timestamp"],
                "gap_minutes": dxy_gap,
            }
        )
        .sort_values(
            "gap_minutes",
            ascending=False,
        )
        .head(20)
    )

    print(
        gaps.to_string(index=False)
    )


if __name__ == "__main__":
    diagnose()