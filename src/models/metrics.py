from __future__ import annotations

import numpy as np
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)


def regression_metrics(
    y_true,
    y_pred,
) -> dict:

    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)

    mae = mean_absolute_error(
        y_true,
        y_pred,
    )

    rmse = np.sqrt(
        mean_squared_error(
            y_true,
            y_pred,
        )
    )

    r2 = r2_score(
        y_true,
        y_pred,
    )

    correlation = np.corrcoef(
        y_true,
        y_pred,
    )[0, 1]

    direction_accuracy = np.mean(
        np.sign(y_true)
        == np.sign(y_pred)
    )

    return {
        "mae": float(mae),
        "rmse": float(rmse),
        "r2": float(r2),
        "correlation": float(correlation),
        "direction_accuracy": float(
            direction_accuracy
        ),
        "actual_mean": float(
            np.mean(y_true)
        ),
        "prediction_mean": float(
            np.mean(y_pred)
        ),
    }