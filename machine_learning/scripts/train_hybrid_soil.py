"""
Train Hybrid Soil Forecast Model
================================

Trains the hybrid soil forecasting model that combines:
1. Rule-Based Expert System (soil science knowledge)
2. Pure ML (Random Forest)
3. Hybrid (ML learns residuals from rule-based predictions)

This script:
- Loads training data from Soil_Data/data/synthetic/
- Trains all three approaches
- Evaluates and compares performance
- Saves trained models for API use

Usage:
    python scripts/train_hybrid_soil.py
    python scripts/train_hybrid_soil.py --data-path /path/to/data.csv
"""

import argparse
import sys
import logging
from pathlib import Path
from datetime import datetime

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "app"))

import pandas as pd
import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_default_data_path() -> Path:
    """Get default path to synthetic soil data."""
    # Check multiple possible locations
    possible_paths = [
        Path(__file__).parent.parent.parent / "Soil_Data" / "data" / "synthetic" / "synthetic_soil_timeseries.csv",
        Path(__file__).parent.parent / "data" / "soil" / "synthetic_soil_timeseries.csv",
        Path("Soil_Data/data/synthetic/synthetic_soil_timeseries.csv"),
    ]
    
    for path in possible_paths:
        if path.exists():
            return path
    
    return possible_paths[0]  # Return first as default


def get_output_path() -> Path:
    """Get output path for trained models."""
    output_dir = Path(__file__).parent.parent / "trained_models" / "soil"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def load_training_data(data_path: Path) -> pd.DataFrame:
    """Load and validate training data."""
    logger.info(f"Loading data from: {data_path}")
    
    if not data_path.exists():
        raise FileNotFoundError(f"Data file not found: {data_path}")
    
    df = pd.read_csv(data_path)
    
    # Parse date if exists
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
    
    logger.info(f"Loaded {len(df)} records")
    logger.info(f"Columns: {list(df.columns)}")
    if 'date' in df.columns:
        logger.info(f"Date range: {df['date'].min()} to {df['date'].max()}")
    
    return df


def train_hybrid_model(df: pd.DataFrame, output_path: Path) -> dict:
    """Train the hybrid forecast model."""
    from models.soil.hybrid_forecast_model import HybridSoilForecastModel, HybridConfig, MLConfig
    
    logger.info("\n" + "="*80)
    logger.info("HYBRID SOIL FORECASTING MODEL TRAINING")
    logger.info("="*80)
    logger.info("\nThis script trains and compares THREE approaches:")
    logger.info("  1. Rule-Based Expert System")
    logger.info("  2. Pure Machine Learning (Random Forest)")
    logger.info("  3. HYBRID (Rule-Based + ML Residual Correction)")
    
    # Initialize model with configuration
    hybrid_config = HybridConfig(
        fusion_method="weighted_average",
        rule_weight=0.6,
        ml_weight=0.4,
        learn_weights=True,
        confidence_threshold=0.7
    )
    
    ml_config = MLConfig(
        model_type="RandomForest",
        n_estimators=100,
        max_depth=6,
        min_samples_split=15,
        min_samples_leaf=5,
        random_state=42,
        cv_folds=5
    )
    
    model = HybridSoilForecastModel(
        version="1.0",
        hybrid_config=hybrid_config,
        ml_config=ml_config
    )
    
    # Train the model
    logger.info("\n[1] Training models...")
    results = model.train(df)
    
    # Print comparison table
    print_comparison_table(results)
    
    # Save models
    model_path = output_path / "hybrid_soil_forecast.joblib"
    model.save(str(model_path))
    logger.info(f"\n✅ Models saved to: {model_path}")
    
    # Save evaluation results
    save_evaluation_results(results, output_path)
    
    # Print thesis summary
    print_thesis_summary(results)
    
    return results


def print_comparison_table(results: dict):
    """Print model comparison table."""
    print("\n" + "="*90)
    print("MODEL COMPARISON - Train R² and Test R²")
    print("="*90)
    print(f"{'Parameter':<22} | {'Rule-Based':^15} | {'Pure ML':^20} | {'Hybrid':^20}")
    print(f"{'':<22} | {'Test R²':^15} | {'Train':^9} {'Test':^10} | {'Train':^9} {'Test':^10}")
    print("-"*90)
    
    for param, approaches in results.items():
        rb_test = approaches['rule_based'].get('test_r2', 0)
        ml_train = approaches['pure_ml'].get('train_r2', 0)
        ml_test = approaches['pure_ml'].get('test_r2', 0)
        hy_train = approaches['hybrid'].get('train_r2', 0)
        hy_test = approaches['hybrid'].get('test_r2', 0)
        
        print(f"{param:<22} | {rb_test:^15.4f} | {ml_train:^9.4f} {ml_test:^10.4f} | {hy_train:^9.4f} {hy_test:^10.4f}")
    
    print("="*90)


def save_evaluation_results(results: dict, output_path: Path):
    """Save evaluation results to CSV."""
    rows = []
    for param, approaches in results.items():
        row = {
            'Parameter': param,
            'Rule_Based_Test_R2': approaches['rule_based'].get('test_r2', None),
            'Pure_ML_Train_R2': approaches['pure_ml'].get('train_r2', None),
            'Pure_ML_Test_R2': approaches['pure_ml'].get('test_r2', None),
            'Hybrid_Train_R2': approaches['hybrid'].get('train_r2', None),
            'Hybrid_Test_R2': approaches['hybrid'].get('test_r2', None),
            'Hybrid_RMSE': approaches['hybrid'].get('test_rmse', None),
            'Hybrid_MAE': approaches['hybrid'].get('test_mae', None),
        }
        rows.append(row)
    
    df = pd.DataFrame(rows)
    
    # Add average row
    avg_row = {
        'Parameter': 'AVERAGE',
        'Rule_Based_Test_R2': df['Rule_Based_Test_R2'].mean(),
        'Pure_ML_Train_R2': df['Pure_ML_Train_R2'].mean(),
        'Pure_ML_Test_R2': df['Pure_ML_Test_R2'].mean(),
        'Hybrid_Train_R2': df['Hybrid_Train_R2'].mean(),
        'Hybrid_Test_R2': df['Hybrid_Test_R2'].mean(),
        'Hybrid_RMSE': df['Hybrid_RMSE'].mean(),
        'Hybrid_MAE': df['Hybrid_MAE'].mean(),
    }
    df = pd.concat([df, pd.DataFrame([avg_row])], ignore_index=True)
    
    eval_path = output_path / "hybrid_model_evaluation.csv"
    df.to_csv(eval_path, index=False)
    logger.info(f"✅ Evaluation results saved to: {eval_path}")


def print_thesis_summary(results: dict):
    """Print thesis-worthy summary."""
    print("\n" + "="*80)
    print("THESIS SUMMARY: HYBRID APPROACH ANALYSIS")
    print("="*80)
    
    # Calculate averages
    approach_avgs = {'rule_based': [], 'pure_ml': [], 'hybrid': []}
    for param, approaches in results.items():
        approach_avgs['rule_based'].append(approaches['rule_based'].get('test_r2', 0))
        approach_avgs['pure_ml'].append(approaches['pure_ml'].get('test_r2', 0))
        approach_avgs['hybrid'].append(approaches['hybrid'].get('test_r2', 0))
    
    avg_r2 = {k: np.mean(v) for k, v in approach_avgs.items()}
    
    print("""
┌─────────────────────────────────────────────────────────────────────┐
│                    HYBRID MODEL ARCHITECTURE                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   1. RULE-BASED LAYER (Soil Science Knowledge)                      │
│      - Applies documented seasonal effects                          │
│      - Provides explainable baseline predictions                    │
│      - No training required, uses domain expertise                  │
│                                                                      │
│   2. ML RESIDUAL LAYER (Pattern Learning)                           │
│      - Learns errors/residuals from rule-based predictions          │
│      - Captures patterns rules don't account for                    │
│      - Random Forest with regularization                            │
│                                                                      │
│   3. FUSION LAYER (Combination)                                     │
│      - Final Prediction = Rule-Based + ML_Correction                │
│      - Inherits explainability from rules                           │
│      - Gains accuracy from ML pattern detection                     │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
""")
    
    print("AVERAGE TEST R² BY APPROACH:")
    print("-"*50)
    for approach, r2 in avg_r2.items():
        bar = "█" * int(max(0, r2) * 30)
        print(f"   {approach:<12}: {r2:>7.4f} {bar}")
    
    # Best approach
    best_approach = max(avg_r2, key=avg_r2.get)
    print(f"\n✨ KEY FINDING: {best_approach.upper()} performs best overall (R² = {avg_r2[best_approach]:.4f})")
    
    print("""
CONTRIBUTIONS TO KNOWLEDGE:
1. Demonstrated hybrid approach combining rule-based and ML
2. Quantified performance comparison across three approaches  
3. ML residual learning improves upon rule-based predictions
4. Maintains explainability while gaining accuracy
""")


def main():
    parser = argparse.ArgumentParser(description='Train Hybrid Soil Forecast Model')
    parser.add_argument(
        '--data-path',
        type=str,
        default=None,
        help='Path to training data CSV'
    )
    parser.add_argument(
        '--output-path',
        type=str,
        default=None,
        help='Path to save trained models'
    )
    
    args = parser.parse_args()
    
    # Determine paths
    data_path = Path(args.data_path) if args.data_path else get_default_data_path()
    output_path = Path(args.output_path) if args.output_path else get_output_path()
    
    try:
        # Load data
        df = load_training_data(data_path)
        
        # Train model
        results = train_hybrid_model(df, output_path)
        
        print("\n" + "="*80)
        print("✅ HYBRID MODEL TRAINING COMPLETE!")
        print("="*80)
        print(f"\nModels saved to: {output_path}")
        print("\nNext steps:")
        print("  1. Start the ML service: uvicorn app.main:app --reload")
        print("  2. Test the hybrid forecast: POST /api/soil/hybrid-forecast")
        print("  3. Compare approaches: GET /api/soil/model-comparison")
        
    except Exception as e:
        logger.error(f"Training failed: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
