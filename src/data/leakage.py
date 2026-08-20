from __future__ import annotations

import pandas as pd


def check_point_in_time_integrity(
    df: pd.DataFrame,
) -> dict:
    """
    Verify that no joined observation becomes available
    after the prediction timestamp.
    """

    violations = []

    availability_columns = [
        column
        for column in df.columns
        if column.endswith("_available_at")
    ]

    for column in availability_columns:

        invalid = (
            df[column].notna()
            &
            (df[column] > df["prediction_time"])
        )

        count = int(
            invalid.sum()
        )

        if count:
            violations.append(
                {
                    "column": column,
                    "violations": count,
                }
            )

    return {
        "valid": len(violations) == 0,
        "violations": violations,
    }