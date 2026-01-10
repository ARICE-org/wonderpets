"""
Train Hybrid Soil Forecast Model

Usage:
    python scripts/train_hybrid_soil.py
    python scripts/train_hybrid_soil.py --data-path data/soil/synthetic_soil_timeseries.csv
"""

import argparse
import sys
import logging
from pathlib import Path
from datetime import datetime

# Add app directory to path
# Add machine_learning directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def get_default_data_path() -> Path:
    """Get default path to synthetic soil data."""
    # Check multiple possible locations (prioritize local data folder)
    possible_paths = [
        Path(__file__).parent.parent / "data" / "soil" / "synthetic_soil_timeseries.csv",
        Path(__file__).parent.parent / "data" / "synthetic_soil_timeseries.csv",
        Path(__file__).parent.parent.parent / "Soil_Data" / "data" / "synthetic" / "synthetic_soil_timeseries.csv",
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
    if not data_path.exists():
        raise FileNotFoundError(f"Data file not found: {data_path}")
    
    df = pd.read_csv(data_path)
    
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
    
    return df


def train_hybrid_model(df: pd.DataFrame, output_path: Path) -> dict:
    """Train the hybrid forecast model."""
    from apps.soil_service.models.hybrid_forecast_model import HybridSoilForecastModel, HybridConfig, MLConfig
    
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
    results = model.train(df)
    
    # Save models
    model_path = output_path / "hybrid_soil_forecast.joblib"
    model.save(str(model_path))
    
    # Save evaluation results
    save_evaluation_results(results, output_path)
    
    return results, model_path


def print_comparison_table(results: dict):
    """Print concise training summary."""
    avg_r2 = np.mean([r['hybrid'].get('test_r2', 0) for r in results.values()])
    avg_rmse = np.mean([r['hybrid'].get('test_rmse', 0) for r in results.values()])
    
    print("\n" + "="*55)
    print("  Parameter Performance (Test R²)")
    print("="*55)
    for param, approaches in results.items():
        r2 = approaches['hybrid'].get('test_r2', 0)
        bar = "█" * int(max(0, r2) * 20)
        print(f"  {param:<22} {r2:.4f} {bar}")
    print("-"*55)
    print(f"  {'AVERAGE':<22} {avg_r2:.4f}")
    print(f"  {'AVG RMSE':<22} {avg_rmse:.4f}")
    print("="*55)


def save_evaluation_results(results: dict, output_path: Path):
    """Save evaluation results to CSV."""
    rows = []
    for param, approaches in results.items():
        row = {
            'parameter': param,
            'test_r2': approaches['hybrid'].get('test_r2', None),
            'rmse': approaches['hybrid'].get('test_rmse', None),
            'mae': approaches['hybrid'].get('test_mae', None),
        }
        rows.append(row)
    
    df = pd.DataFrame(rows)
    avg_row = {
        'parameter': 'AVERAGE',
        'test_r2': df['test_r2'].mean(),
        'rmse': df['rmse'].mean(),
        'mae': df['mae'].mean(),
    }
    df = pd.concat([df, pd.DataFrame([avg_row])], ignore_index=True)
    
    eval_path = output_path / "hybrid_model_evaluation.csv"
    df.to_csv(eval_path, index=False)


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
        start_time = datetime.now()
        
        logger.info(f"Starting training | Data: {data_path.name}")
        
        # Load data
        df = load_training_data(data_path)
        logger.info(f"Loaded {len(df)} records")
        
        # Train model
        results, model_path = train_hybrid_model(df, output_path)
        
        duration = (datetime.now() - start_time).total_seconds()
        
        # Print summary
        print_comparison_table(results)
        
        logger.info(f"Training complete in {duration:.2f}s | Model: {model_path}")
        
    except Exception as e:
        logger.error(f"Training failed: {e}")
        raise


if __name__ == "__main__":
    main()
