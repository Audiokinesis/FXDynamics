from __future__ import annotations

import pandas as pd


def feature_quality_report(
    df: pd.DataFrame,
    target: str,
) -> pd.DataFrame:

    rows = []

    for column in df.columns:

        rows.append(
            {
                "feature": column,
                "dtype": str(df[column].dtype),
                "rows": len(df),
                "missing": int(
                    df[column].isna().sum()
                ),
                "missing_pct": (
                    df[column].isna().mean() * 100
                ),
                "unique": (
                    df[column].nunique(
                        dropna=True
                    )
                ),
                "target": column == target,
            }
        )

    return pd.DataFrame(rows)