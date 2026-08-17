# FXDynamics

Regime-Conditioned FX Dynamics Engine.

## Objective

Analyze EUR/USD price dynamics using:

- Multi-timeframe market data
- Market structure / FVG regimes
- Scale-free log returns
- Cross-market features
- Regime-conditioned Koopman operators
- CV-LASSO sparse modeling
- Eigenvalue/eigenvector analysis
- Machine learning
- MLflow experiment tracking

## Instruments

- EURUSD
- DXY
- US2Y
- DE2Y
- US10Y

## Project Structure

- pp - Application / dashboard
- config - Configuration files
- data/raw - Raw market data
- data/interim - Intermediate processing results
- data/processed - ML-ready datasets
- 
otebooks - Research and experimentation notebooks
- src/data - Data ingestion and validation
- src/features - Feature engineering
- src/regimes - Market regime detection
- src/models - ML and Koopman models
- src/evaluation - Model evaluation
- src/visualization - Charts and visualizations
- 	ests - Unit and integration tests
- experiments - Experiment configurations
- mlruns - MLflow tracking data
- eports - Research reports and results
