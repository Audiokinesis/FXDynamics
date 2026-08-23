from __future__ import annotations

from pathlib import Path

import mlflow
import numpy as np
import pandas as pd

from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge, Lasso
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from xgboost import XGBRegressor

from .feature_sets import (
    EURUSD_FEATURES,
    CROSS_MARKET_FEATURES,
    validate_features,
)

from .split import temporal_split
from .metrics import regression_metrics


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "features"
    / "EURUSD_feature_matrix_5m.parquet"
)

TARGET = "target_next_5m_return"


def zero_predictor(
    y_train,
    y_test,
):
    """
    Zero-return baseline.

    Predicts that the next 5-minute return is exactly zero.
    """

    return np.zeros(
        len(y_test)
    )


def create_ridge():
    return Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(
                    strategy="median"
                ),
            ),
            (
                "scaler",
                StandardScaler(),
            ),
            (
                "model",
                Ridge(
                    alpha=1.0
                ),
            ),
        ]
    )


def create_lasso():
    return Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(
                    strategy="median"
                ),
            ),
            (
                "scaler",
                StandardScaler(),
            ),
            (
                "model",
                Lasso(
                    alpha=0.0001,
                    max_iter=10000,
                ),
            ),
        ]
    )


def create_xgboost():

    return Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(
                    strategy="median"
                ),
            ),
            (
                "model",
                XGBRegressor(
                    n_estimators=300,
                    max_depth=3,
                    learning_rate=0.03,
                    subsample=0.8,
                    colsample_bytree=0.8,
                    objective="reg:squarederror",
                    eval_metric="rmse",
                    random_state=42,
                ),
            ),
        ]
    )


def run_model(
    model_name,
    model,
    X_train,
    y_train,
    X_test,
    y_test,
):

    if model_name == "zero":

        prediction = zero_predictor(
            y_train,
            y_test,
        )

    else:

        model.fit(
            X_train,
            y_train,
        )

        prediction = model.predict(
            X_test
        )

    metrics = regression_metrics(
        y_test,
        prediction,
    )

    return metrics, prediction, model


def run_experiment(
    df: pd.DataFrame,
    feature_set_name: str,
    feature_columns: list[str],
):

    validate_features(
        df,
        feature_columns,
    )

    # ---------------------------------------------------------------
    # Remove rows where the target is unavailable.
    # ---------------------------------------------------------------

    dataset = df[
        df[TARGET].notna()
    ].copy()

    # ---------------------------------------------------------------
    # Remove rows before the feature warmup is available.
    #
    # We'll let the pipeline's imputers handle remaining DXY gaps,
    # but rows with no EURUSD feature history should be removed.
    # ---------------------------------------------------------------

    required_eurusd = [
        feature
        for feature in EURUSD_FEATURES
        if feature in feature_columns
    ]

    dataset = dataset.dropna(
        subset=required_eurusd
    )

    train, validation, test = temporal_split(
        dataset
    )

    X_train = train[
        feature_columns
    ]

    y_train = train[
        TARGET
    ]

    X_validation = validation[
        feature_columns
    ]

    y_validation = validation[
        TARGET
    ]

    X_test = test[
        feature_columns
    ]

    y_test = test[
        TARGET
    ]

    print()
    print("=" * 80)
    print(
        f"FEATURE SET: {feature_set_name}"
    )
    print("=" * 80)

    print(
        "Train:",
        len(train),
        train["prediction_time"].min(),
        "→",
        train["prediction_time"].max(),
    )

    print(
        "Validation:",
        len(validation),
        validation["prediction_time"].min(),
        "→",
        validation["prediction_time"].max(),
    )

    print(
        "Test:",
        len(test),
        test["prediction_time"].min(),
        "→",
        test["prediction_time"].max(),
    )

    models = {
        "zero": None,
        "ridge": create_ridge(),
        "lasso": create_lasso(),
        "xgboost": create_xgboost(),
    }

    results = []

    for model_name, model in models.items():

        with mlflow.start_run(
            run_name=f"{feature_set_name}_{model_name}"
        ):

            mlflow.log_param(
                "feature_set",
                feature_set_name,
            )

            mlflow.log_param(
                "feature_count",
                len(feature_columns),
            )

            mlflow.log_param(
                "model",
                model_name,
            )

            mlflow.log_param(
                "train_rows",
                len(train),
            )

            mlflow.log_param(
                "validation_rows",
                len(validation),
            )

            mlflow.log_param(
                "test_rows",
                len(test),
            )

            metrics, predictions, fitted_model = run_model(
                model_name,
                model,
                X_train,
                y_train,
                X_test,
                y_test,
            )

            for metric_name, value in metrics.items():

                mlflow.log_metric(
                    metric_name,
                    value,
                )

            results.append(
                {
                    "feature_set": feature_set_name,
                    "model": model_name,
                    **metrics,
                }
            )

            print(
                f"\n{model_name}"
            )

            for key, value in metrics.items():

                print(
                    f"  {key}: {value:.8f}"
                )

    return pd.DataFrame(results)


def main():

    df = pd.read_parquet(
        DATA_PATH
    )

    mlflow.set_experiment(
        "FXDynamics_Baseline"
    )

    eurusd_results = run_experiment(
        df,
        "EURUSD_only",
        EURUSD_FEATURES,
    )

    cross_market_results = run_experiment(
        df,
        "Cross_Market",
        CROSS_MARKET_FEATURES,
    )

    results = pd.concat(
        [
            eurusd_results,
            cross_market_results,
        ],
        ignore_index=True,
    )

    print()
    print("=" * 80)
    print("FINAL COMPARISON")
    print("=" * 80)

    print(
        results.to_string(
            index=False
        )
    )

    output_dir = (
        PROJECT_ROOT
        / "reports"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    results.to_csv(
        output_dir
        / "baseline_results.csv",
        index=False,
    )


if __name__ == "__main__":
    main()