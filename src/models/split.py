from __future__ import annotations

import pandas as pd


def temporal_split(
    df: pd.DataFrame,
    train_fraction: float = 0.70,
    validation_fraction: float = 0.15,
    purge_gap: int = 1,
):
    """
    Chronological train/validation/test split.

    The purge gap prevents samples immediately adjacent to a
    boundary from leaking target-period information across splits.
    """

    df = df.sort_values(
        "prediction_time"
    ).reset_index(drop=True)

    n = len(df)

    train_end = int(
        n * train_fraction
    )

    validation_end = int(
        n * (
            train_fraction
            + validation_fraction
        )
    )

    train_end_purged = train_end

    validation_start = (
        train_end
        + purge_gap
    )

    validation_end_purged = validation_end

    test_start = (
        validation_end
        + purge_gap
    )

    train = df.iloc[
        :train_end_purged
    ].copy()

    validation = df.iloc[
        validation_start:validation_end_purged
    ].copy()

    test = df.iloc[
        test_start:
    ].copy()

    return train, validation, test