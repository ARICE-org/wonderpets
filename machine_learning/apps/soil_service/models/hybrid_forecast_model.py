"""
Hybrid Soil Forecast Model

Combines rule-based soil science knowledge with ML pattern learning.
This is the core thesis contribution - a hybrid approach that:
1. Uses soil science rules for baseline predictions (explainability)
2. Applies ML to learn residuals/corrections (accuracy)
3. Combines both for robust and interpretable forecasts
"""

from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import numpy as np
import logging
from pathlib import Path
import joblib
from dataclasses import dataclass

from apps.common.base.base_model import BaseMLModel
from apps.common.utils.logging_utils import logger


@dataclass
class HybridConfig:
    """Configuration for hybrid model."""
    fusion_method: str = "weighted_average"
    rule_weight: float = 0.6
    ml_weight: float = 0.4
    learn_weights: bool = True
    confidence_threshold: float = 0.7


@dataclass
class MLConfig:
    """Configuration for ML models."""
    model_type: str = "RandomForest"
    n_estimators: int = 100
    max_depth: int = 6
    min_samples_split: int = 15
    min_samples_leaf: int = 5
    random_state: int = 42
    cv_folds: int = 5


class SoilScienceRules:
    """
    Soil science expert rules based on agricultural literature.
    
    Encapsulates domain knowledge for soil parameter predictions.
    """
    
    # Seasonal definitions (Philippines)
    SEASONS = {
        "dry": {"months": [12, 1, 2, 3, 4, 5]},
        "wet": {"months": [6, 7, 8, 9, 10, 11]}
    }
    
    # Soil parameter rules based on literature
    SOIL_RULES = {
        'nitrogen_ppm': {
            'optimal_range': (40, 80),
            'wet_change_pct': (-10, -15),
            'dry_change_pct': (-5, -8),
        },
        'phosphorus_ppm': {
            'optimal_range': (15, 30),
            'wet_change_pct': (-2, -5),
            'dry_change_pct': (0, -2),
        },
        'potassium_meq': {
            'optimal_range': (0.5, 1.5),
            'wet_change_pct': (-8, -12),
            'dry_change_pct': (-3, -5),
        },
        'pH': {
            'optimal_range': (5.5, 7.0),
            'wet_change_units': (-0.1, -0.3),
            'dry_change_units': (0, 0.1),
        },
        'soil_moisture_pct': {
            'optimal_range': (25, 40),
            'wet_typical': (30, 50),
            'dry_typical': (10, 25),
        },
        'organic_matter_pct': {
            'optimal_range': (3, 5),
            'wet_change_pct': (-3, -5),
            'dry_change_pct': (-1, -2),
        }
    }
    
    # Parameter weights for health scoring
    PARAMETER_WEIGHTS = {
        'nitrogen_ppm': 0.20,
        'phosphorus_ppm': 0.15,
        'potassium_meq': 0.15,
        'pH': 0.20,
        'soil_moisture_pct': 0.15,
        'organic_matter_pct': 0.15
    }
    
    @classmethod
    def get_season(cls, month: int) -> str:
        """Determine season from month."""
        if month in cls.SEASONS['dry']['months']:
            return 'dry'
        return 'wet'
    
    @classmethod
    def get_rule_based_prediction(
        cls,
        month: int,
        days_into_season: int,
        parameter: str,
        seasonal_baseline: Dict[str, Dict]
    ) -> float:
        """
        Generate rule-based prediction using soil science knowledge.
        
        Args:
            month: Current month (1-12)
            days_into_season: Days into current season
            parameter: Soil parameter name
            seasonal_baseline: Baseline statistics by season
            
        Returns:
            Rule-based predicted value
        """
        season = cls.get_season(month)
        base_mean = seasonal_baseline[season][parameter]['mean']
        
        rule = cls.SOIL_RULES.get(parameter, {})
        
        if parameter == 'pH':
            change_key = f'{season}_change_units'
            if change_key in rule:
                change_range = rule[change_key]
                progress = min(days_into_season / 180, 1.0)
                change = np.mean(change_range) * progress
                return base_mean + change
        elif parameter == 'soil_moisture_pct':
            typical_key = f'{season}_typical'
            if typical_key in rule:
                typical = rule[typical_key]
                target = np.mean(typical)
                progress = min(days_into_season / 90, 1.0)
                return base_mean * (1 - progress * 0.3) + target * (progress * 0.3)
        else:
            change_key = f'{season}_change_pct'
            if change_key in rule:
                change_range = rule[change_key]
                progress = min(days_into_season / 180, 1.0)
                change_pct = np.mean(change_range) / 100
                return base_mean * (1 + change_pct * progress)
        
        return base_mean
    
    @classmethod
    def calculate_days_into_season(cls, month: int, day: int, season: str) -> int:
        """Calculate days into current season."""
        if season == 'dry':
            if month == 12:
                return day
            else:
                return 31 + (month - 1) * 30 + day
        else:
            return (month - 6) * 30 + day


class HybridSoilForecastModel(BaseMLModel):
    """
    Hybrid soil forecast model combining rule-based and ML approaches.
    """
    
    TARGET_PARAMETERS = [
        'nitrogen_ppm', 'phosphorus_ppm', 'potassium_meq',
        'pH', 'soil_moisture_pct', 'organic_matter_pct'
    ]
    
    DEFAULT_SEASONAL_BASELINE = {
        'dry': {
            'nitrogen_ppm': {'mean': 35.0, 'std': 8.0},
            'phosphorus_ppm': {'mean': 20.0, 'std': 5.0},
            'potassium_meq': {'mean': 0.75, 'std': 0.2},
            'pH': {'mean': 6.2, 'std': 0.4},
            'soil_moisture_pct': {'mean': 35.0, 'std': 10.0},
            'organic_matter_pct': {'mean': 3.0, 'std': 0.8}
        },
        'wet': {
            'nitrogen_ppm': {'mean': 45.0, 'std': 10.0},
            'phosphorus_ppm': {'mean': 22.0, 'std': 6.0},
            'potassium_meq': {'mean': 0.85, 'std': 0.25},
            'pH': {'mean': 6.0, 'std': 0.5},
            'soil_moisture_pct': {'mean': 55.0, 'std': 12.0},
            'organic_matter_pct': {'mean': 3.5, 'std': 1.0}
        }
    }
    
    def __init__(
        self,
        version: str = "1.0",
        hybrid_config: Optional[HybridConfig] = None,
        ml_config: Optional[MLConfig] = None
    ):
        super().__init__(model_name="hybrid_soil_forecast", version=version)
        
        self.hybrid_config = hybrid_config or HybridConfig()
        self.ml_config = ml_config or MLConfig()
        self.rules = SoilScienceRules()
        
        self.pure_ml_models: Dict[str, Dict] = {}
        self.hybrid_residual_models: Dict[str, Dict] = {}
        self.seasonal_baseline: Dict[str, Dict] = self.DEFAULT_SEASONAL_BASELINE.copy()
        self.scalers: Dict[str, Any] = {}
        self.feature_columns: List[str] = []
        self.training_results: Dict[str, Any] = {}
    
    def load(self, model_path: str) -> None:
        """Load trained hybrid models from disk."""
        try:
            path = Path(model_path)
            if path.exists():
                models_data = joblib.load(path)
                self.pure_ml_models = models_data.get('pure_ml', {})
                self.hybrid_residual_models = models_data.get('hybrid_residual', {})
                loaded_baseline = models_data.get('seasonal_baseline', {})
                if loaded_baseline and 'dry' in loaded_baseline and 'wet' in loaded_baseline:
                    self.seasonal_baseline = loaded_baseline
                self.feature_columns = models_data.get('feature_columns', [])
                self.training_results = models_data.get('training_results', {})
                self.is_trained = True
                logger.info(f"Loaded hybrid models from {model_path}")
            else:
                logger.warning(f"Model file not found: {model_path}")
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            raise
    
    def save(self, model_path: str, filename: Optional[str] = None) -> str:
        """Save trained hybrid models to disk."""
        try:
            path = Path(model_path)
            if filename:
                path = path / filename
            path.parent.mkdir(parents=True, exist_ok=True)
            
            models_data = {
                'pure_ml': self.pure_ml_models,
                'hybrid_residual': self.hybrid_residual_models,
                'seasonal_baseline': self.seasonal_baseline,
                'feature_columns': self.feature_columns,
                'training_results': self.training_results,
                'metadata': self.metadata
            }
            
            joblib.dump(models_data, path)
            logger.info(f"Saved hybrid models to {path}")
            return str(path)
        except Exception as e:
            logger.error(f"Error saving models: {e}")
            raise
    
    def train(
        self,
        df,
        target_params: Optional[List[str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Train the hybrid model on provided data."""
        from sklearn.model_selection import TimeSeriesSplit, cross_val_score
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.preprocessing import StandardScaler
        from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
        
        target_params = target_params or self.TARGET_PARAMETERS
        
        df_prepared = self._prepare_training_data(df)
        self.seasonal_baseline = self._calculate_seasonal_baseline(df_prepared, target_params)
        self.feature_columns = self._get_feature_columns(df_prepared, target_params)
        
        results = {}
        
        for param in target_params:
            if param not in df_prepared.columns:
                logger.warning(f"Parameter {param} not found in data, skipping")
                continue
            
            logger.info(f"Training models for {param}...")
            
            X = df_prepared[self.feature_columns].values
            y = df_prepared[param].values
            
            split_idx = int(len(df_prepared) * 0.8)
            X_train, X_test = X[:split_idx], X[split_idx:]
            y_train, y_test = y[:split_idx], y[split_idx:]
            df_train = df_prepared.iloc[:split_idx]
            df_test = df_prepared.iloc[split_idx:]
            
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Rule-based predictions
            rule_train_pred = df_train.apply(
                lambda row: self.rules.get_rule_based_prediction(
                    row['month'], row['days_into_season'], param, self.seasonal_baseline
                ), axis=1
            ).values
            rule_test_pred = df_test.apply(
                lambda row: self.rules.get_rule_based_prediction(
                    row['month'], row['days_into_season'], param, self.seasonal_baseline
                ), axis=1
            ).values
            
            rule_metrics = {
                'test_r2': r2_score(y_test, rule_test_pred),
                'test_rmse': np.sqrt(mean_squared_error(y_test, rule_test_pred)),
                'test_mae': mean_absolute_error(y_test, rule_test_pred)
            }
            
            # Pure ML model
            ml_model = RandomForestRegressor(
                n_estimators=self.ml_config.n_estimators,
                max_depth=self.ml_config.max_depth,
                min_samples_split=self.ml_config.min_samples_split,
                min_samples_leaf=self.ml_config.min_samples_leaf,
                random_state=self.ml_config.random_state,
                n_jobs=-1
            )
            ml_model.fit(X_train_scaled, y_train)
            
            ml_train_pred = ml_model.predict(X_train_scaled)
            ml_test_pred = ml_model.predict(X_test_scaled)
            
            tscv = TimeSeriesSplit(n_splits=self.ml_config.cv_folds)
            cv_scores = cross_val_score(ml_model, X_train_scaled, y_train, cv=tscv, scoring='r2')
            
            ml_metrics = {
                'train_r2': r2_score(y_train, ml_train_pred),
                'test_r2': r2_score(y_test, ml_test_pred),
                'test_rmse': np.sqrt(mean_squared_error(y_test, ml_test_pred)),
                'test_mae': mean_absolute_error(y_test, ml_test_pred),
                'cv_r2_mean': cv_scores.mean(),
                'cv_r2_std': cv_scores.std()
            }
            
            self.pure_ml_models[param] = {
                'model': ml_model,
                'scaler': scaler
            }
            
            # Hybrid model (ML learns residuals)
            train_residuals = y_train - rule_train_pred
            
            hybrid_model = RandomForestRegressor(
                n_estimators=self.ml_config.n_estimators,
                max_depth=max(2, self.ml_config.max_depth - 2),
                min_samples_split=self.ml_config.min_samples_split,
                min_samples_leaf=self.ml_config.min_samples_leaf,
                random_state=self.ml_config.random_state,
                n_jobs=-1
            )
            hybrid_model.fit(X_train_scaled, train_residuals)
            
            train_residual_pred = hybrid_model.predict(X_train_scaled)
            test_residual_pred = hybrid_model.predict(X_test_scaled)
            
            hybrid_train_pred = rule_train_pred + train_residual_pred
            hybrid_test_pred = rule_test_pred + test_residual_pred
            
            hybrid_metrics = {
                'train_r2': r2_score(y_train, hybrid_train_pred),
                'test_r2': r2_score(y_test, hybrid_test_pred),
                'test_rmse': np.sqrt(mean_squared_error(y_test, hybrid_test_pred)),
                'test_mae': mean_absolute_error(y_test, hybrid_test_pred),
                'residual_r2': r2_score(y_test - rule_test_pred, test_residual_pred)
            }
            
            self.hybrid_residual_models[param] = {
                'model': hybrid_model,
                'scaler': scaler,
                'baseline': self.seasonal_baseline
            }
            
            results[param] = {
                'rule_based': rule_metrics,
                'pure_ml': ml_metrics,
                'hybrid': hybrid_metrics
            }
            
            logger.info(f"  Rule-Based R²: {rule_metrics['test_r2']:.4f}")
            logger.info(f"  Pure ML R²: {ml_metrics['test_r2']:.4f}")
            logger.info(f"  Hybrid R²: {hybrid_metrics['test_r2']:.4f}")
        
        self.training_results = results
        self.is_trained = True
        self.metadata['training_samples'] = len(df_prepared)
        self.metadata['trained_at'] = datetime.now().isoformat()
        
        return results
    
    def predict(
        self,
        features: Dict[str, Any],
        use_approach: str = "hybrid"
    ) -> Dict[str, Any]:
        """Generate predictions using the specified approach."""
        predictions = {}
        
        for param in self.TARGET_PARAMETERS:
            if use_approach == "rule_based":
                predictions[param] = self._predict_rule_based(param, features)
            elif use_approach == "pure_ml":
                predictions[param] = self._predict_pure_ml(param, features)
            else:
                predictions[param] = self._predict_hybrid(param, features)
        
        return predictions
    
    def preprocess(self, data: Any) -> np.ndarray:
        """Preprocess data for prediction."""
        return np.array(data)
    
    def _predict_rule_based(self, param: str, features: Dict) -> float:
        """Generate rule-based prediction."""
        return self.rules.get_rule_based_prediction(
            features['month'],
            features['days_into_season'],
            param,
            self.seasonal_baseline
        )
    
    def _predict_pure_ml(self, param: str, features: Dict) -> float:
        """Generate pure ML prediction."""
        if param not in self.pure_ml_models:
            return self._predict_rule_based(param, features)
        
        model_info = self.pure_ml_models[param]
        X = self._prepare_feature_vector(features)
        X_scaled = model_info['scaler'].transform([X])
        return model_info['model'].predict(X_scaled)[0]
    
    def _predict_hybrid(self, param: str, features: Dict) -> float:
        """Generate hybrid prediction (rule + ML residual)."""
        rule_pred = self._predict_rule_based(param, features)
        
        if param not in self.hybrid_residual_models:
            return rule_pred
        
        model_info = self.hybrid_residual_models[param]
        X = self._prepare_feature_vector(features)
        X_scaled = model_info['scaler'].transform([X])
        residual = model_info['model'].predict(X_scaled)[0]
        
        return rule_pred + residual
    
    def forecast_season(
        self,
        historical_data: Optional[Dict[str, Any]] = None,
        planting_date: Optional[datetime] = None,
        forecast_days: int = 90,
        interval_days: int = 3
    ) -> Dict[str, Any]:
        """Generate comprehensive seasonal forecast."""
        if planting_date is None:
            planting_date = datetime.now()
        
        forecasts = []
        
        for day_offset in range(0, forecast_days + 1, interval_days):
            forecast_date = planting_date + timedelta(days=day_offset)
            features = self._generate_forecast_features(forecast_date, historical_data)
            
            row = {
                'date': forecast_date.strftime('%Y-%m-%d'),
                'week_number': (day_offset // 7) + 1,
                'season': self.rules.get_season(forecast_date.month),
                'month': forecast_date.month,
                'days_into_season': features['days_into_season']
            }
            
            for param in self.TARGET_PARAMETERS:
                hybrid_pred = round(self._predict_hybrid(param, features), 2)
                row[param] = hybrid_pred
            
            row['soil_health_score'] = self._calculate_health_score(row)
            row['health_category'] = self._get_health_category(row['soil_health_score'])
            
            # Add individual status fields for frontend mapping
            row['nitrogenStatus'] = self._get_param_status('nitrogen_ppm', row['nitrogen_ppm'])
            row['phosphorusStatus'] = self._get_param_status('phosphorus_ppm', row['phosphorus_ppm'])
            row['potassiumStatus'] = self._get_param_status('potassium_meq', row['potassium_meq'])
            row['phStatus'] = self._get_param_status('pH', row['pH'])
            
            forecasts.append(row)
        
        weekly_summary = self._create_weekly_summary(forecasts)
        
        return {
            'planting_date': planting_date.strftime('%Y-%m-%d'),
            'forecast_end_date': (planting_date + timedelta(days=forecast_days)).strftime('%Y-%m-%d'),
            'forecast_interval_days': interval_days,
            'approach': 'hybrid',
            'detailed_forecast': forecasts,
            'weekly_summary': weekly_summary
        }
    
    def _prepare_training_data(self, df) -> Any:
        """Prepare data for training with feature engineering."""
        import pandas as pd
        
        df = df.copy()
        
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        else:
            df['date'] = pd.date_range(start='2024-01-01', periods=len(df), freq='D')
        
        df['month'] = df['date'].dt.month
        df['day_of_year'] = df['date'].dt.dayofyear
        df['season'] = df['month'].apply(self.rules.get_season)
        df['season_numeric'] = df['season'].map({'dry': 0, 'wet': 1})
        
        df['days_into_season'] = df.apply(
            lambda row: self.rules.calculate_days_into_season(
                row['month'], row['date'].day, row['season']
            ), axis=1
        )
        
        for param in self.TARGET_PARAMETERS:
            if param in df.columns:
                df[f'{param}_lag7'] = df[param].shift(7)
                df[f'{param}_lag30'] = df[param].shift(30)
                df[f'{param}_rolling_mean'] = df[param].rolling(window=14).mean()
        
        df = df.dropna().reset_index(drop=True)
        
        return df
    
    def _calculate_seasonal_baseline(
        self,
        df,
        target_params: List[str]
    ) -> Dict[str, Dict]:
        """Calculate baseline statistics by season."""
        baseline = {}
        for season in ['dry', 'wet']:
            season_data = df[df['season'] == season]
            baseline[season] = {}
            for param in target_params:
                if param in season_data.columns:
                    baseline[season][param] = {
                        'mean': float(season_data[param].mean()),
                        'std': float(season_data[param].std())
                    }
        return baseline
    
    def _get_feature_columns(
        self,
        df,
        target_params: List[str]
    ) -> List[str]:
        """Get feature columns for ML models."""
        feature_cols = ['month', 'day_of_year', 'season_numeric', 'days_into_season']
        
        for col in ['temperature', 'precipitation', 'evapotranspiration']:
            if col in df.columns:
                feature_cols.append(col)
        
        for param in target_params:
            for suffix in ['_lag7', '_lag30', '_rolling_mean']:
                col = f'{param}{suffix}'
                if col in df.columns:
                    feature_cols.append(col)
        
        return feature_cols
    
    def _prepare_feature_vector(self, features: Dict) -> List[float]:
        """Prepare feature vector from dict for prediction."""
        return [features.get(col, 0.0) for col in self.feature_columns]
    
    def _generate_forecast_features(
        self,
        forecast_date: datetime,
        historical_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Generate feature dict for a forecast date."""
        month = forecast_date.month
        season = self.rules.get_season(month)
        day_of_year = forecast_date.timetuple().tm_yday
        days_into_season = self.rules.calculate_days_into_season(
            month, forecast_date.day, season
        )
        
        features = {
            'month': month,
            'day_of_year': day_of_year,
            'season': season,
            'season_numeric': 0 if season == 'dry' else 1,
            'days_into_season': days_into_season
        }
        
        for param in self.TARGET_PARAMETERS:
            if historical_data and param in historical_data:
                values = historical_data[param]
                features[f'{param}_lag7'] = values[-7] if len(values) >= 7 else np.mean(values)
                features[f'{param}_lag30'] = values[-30] if len(values) >= 30 else np.mean(values)
                features[f'{param}_rolling_mean'] = np.mean(values[-14:]) if len(values) >= 14 else np.mean(values)
            else:
                baseline_val = self.seasonal_baseline.get(season, {}).get(param, {}).get('mean', 50)
                features[f'{param}_lag7'] = baseline_val
                features[f'{param}_lag30'] = baseline_val
                features[f'{param}_rolling_mean'] = baseline_val
        
        return features
    
    def _calculate_health_score(self, row: Dict) -> float:
        """Calculate soil health score (0-100)."""
        total_score = 0
        total_weight = 0
        
        optimal_ranges = {
            'nitrogen_ppm': (40, 80),
            'phosphorus_ppm': (15, 30),
            'potassium_meq': (0.5, 1.5),
            'pH': (5.5, 7.0),
            'soil_moisture_pct': (25, 40),
            'organic_matter_pct': (3, 5)
        }
        
        for param, (opt_low, opt_high) in optimal_ranges.items():
            if param in row:
                value = row[param]
                weight = self.rules.PARAMETER_WEIGHTS.get(param, 0.1)
                
                if opt_low <= value <= opt_high:
                    score = 100
                elif value < opt_low:
                    score = max(0, 100 - (opt_low - value) / opt_low * 100)
                else:
                    score = max(0, 100 - (value - opt_high) / opt_high * 50)
                
                total_score += score * weight
                total_weight += weight
        
        return round(total_score / total_weight if total_weight > 0 else 50, 1)

    def _get_param_status(self, param: str, value: float) -> str:
        """Calculate status for a specific parameter based on optimal ranges."""
        optimal_ranges = {
            'nitrogen_ppm': (40, 80),
            'phosphorus_ppm': (15, 30),
            'potassium_meq': (0.5, 1.5),
            'pH': (5.5, 7.0),
            'soil_moisture_pct': (25, 40),
            'organic_matter_pct': (3, 5)
        }
        
        if param not in optimal_ranges:
            return 'good'
            
        opt_low, opt_high = optimal_ranges[param]
        
        # pH handles acid/alkaline extremes
        if param == 'pH':
            if 5.5 <= value <= 7.0: return 'good'
            if 5.0 <= value < 5.5 or 7.0 < value <= 8.0: return 'warning'
            return 'bad'
            
        # General nutrients
        if opt_low <= value <= opt_high:
            return 'good'
        
        # Warning ranges (slightly outside optimal)
        if (opt_low * 0.7) <= value < opt_low or opt_high < value <= (opt_high * 1.3):
            return 'warning'
            
        return 'bad'
    
    def _get_health_category(self, score: float) -> str:
        """Get health category from score."""
        if score >= 90:
            return "Excellent"
        elif score >= 75:
            return "Good"
        elif score >= 60:
            return "Moderate"
        elif score >= 40:
            return "Poor"
        return "Critical"
    
    def _create_weekly_summary(self, forecasts: List[Dict]) -> List[Dict]:
        """Create weekly summary from detailed forecasts."""
        import pandas as pd
        
        if not forecasts:
            return []
        
        df = pd.DataFrame(forecasts)
        
        agg_dict = {
            'season': 'first',
            'soil_health_score': 'mean'
        }
        
        for param in self.TARGET_PARAMETERS:
            if param in df.columns:
                agg_dict[param] = 'mean'
        
        # Aggregate status fields using mode or representative value
        for status_col in ['nitrogenStatus', 'phosphorusStatus', 'potassiumStatus', 'phStatus']:
            if status_col in df.columns:
                agg_dict[status_col] = lambda x: x.iloc[0] # Take first day of week status
        
        weekly = df.groupby('week_number').agg(agg_dict).round(2)
        weekly['health_category'] = weekly['soil_health_score'].apply(self._get_health_category)
        
        return weekly.reset_index().to_dict('records')
