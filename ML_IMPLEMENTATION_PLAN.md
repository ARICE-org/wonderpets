# Machine Learning Models Implementation Plan

## Overview

This document outlines the detailed plan for implementing three machine learning models in the ARICE project:

1. **Rice Variety Recommendation Model** - Recommends optimal rice varieties based on soil conditions, weather data, and historical farming data
2. **Weather Forecasting Model** - Predicts weather patterns for agricultural planning
3. **Soil Health Forecasting & Analysis Model** - Analyzes and predicts soil health conditions

---

## Proposed File Structure

```
wonderpets/
├── docker-compose.yml (updated)
├── machine_learning/                    # ML microservice
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                      # FastAPI entry point for ML service
│   │   ├── config/
│   │   │   ├── __init__.py
│   │   │   └── settings.py              # ML service configuration
│   │   │
│   │   ├── models/                      # ML model definitions & architectures
│   │   │   ├── __init__.py
│   │   │   ├── base_model.py            # Abstract base class for all models
│   │   │   ├── recommendation/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── rice_variety_model.py        # Model architecture
│   │   │   │   ├── feature_engineering.py       # Feature preprocessing
│   │   │   │   └── data_preprocessing.py        # Data cleaning & transformation
│   │   │   ├── weather/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── weather_forecast_model.py    # Weather prediction model
│   │   │   │   ├── feature_engineering.py
│   │   │   │   └── data_preprocessing.py
│   │   │   └── soil/
│   │   │       ├── __init__.py
│   │   │       ├── soil_health_model.py         # Soil health scoring model
│   │   │       ├── soil_forecast_model.py       # 3-month seasonal forecast model
│   │   │       ├── feature_engineering.py
│   │   │       └── data_preprocessing.py
│   │   │
│   │   ├── services/                    # Business logic layer
│   │   │   ├── __init__.py
│   │   │   ├── recommendation_service.py       # Recommendation logic
│   │   │   ├── weather_service.py              # Weather forecasting logic
│   │   │   └── soil_analysis_service.py        # Soil analysis logic
│   │   │
│   │   ├── routers/                     # API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── recommendation.py        # /api/recommend endpoints
│   │   │   ├── weather.py               # /api/weather/forecast endpoints
│   │   │   └── soil.py                  # /api/soil/analysis endpoints
│   │   │
│   │   ├── schemas/                     # Pydantic request/response schemas
│   │   │   ├── __init__.py
│   │   │   ├── recommendation.py
│   │   │   ├── weather.py
│   │   │   └── soil.py
│   │   │
│   │   ├── utils/                       # Utility functions
│   │   │   ├── __init__.py
│   │   │   ├── model_loader.py          # Load/save trained models
│   │   │   ├── validators.py            # Input validation helpers
│   │   │   └── metrics.py               # Model performance metrics
│   │   │
│   │   └── data/                        # Data handling
│   │       ├── __init__.py
│   │       ├── connectors/
│   │       │   ├── __init__.py
│   │       │   ├── database.py          # PostgreSQL connector
│   │       │   └── external_api.py      # External weather API connector
│   │       └── repositories/
│   │           ├── __init__.py
│   │           ├── training_data.py     # Training data repository
│   │           └── prediction_log.py    # Prediction logging repository
│   │
│   ├── trained_models/                  # Serialized trained models (.pkl, .h5, .pt)
│   │   ├── recommendation/
│   │   │   └── .gitkeep
│   │   ├── weather/
│   │   │   └── .gitkeep
│   │   └── soil/
│   │       └── .gitkeep
│   │
│   ├── notebooks/                       # Jupyter notebooks for experimentation
│   │   ├── 01_eda_recommendation.ipynb
│   │   ├── 02_eda_weather.ipynb
│   │   ├── 03_eda_soil.ipynb
│   │   ├── 04_model_training_recommendation.ipynb
│   │   ├── 05_model_training_weather.ipynb
│   │   └── 06_model_training_soil.ipynb
│   │
│   ├── scripts/                         # Training & utility scripts
│   │   ├── train_recommendation.py
│   │   ├── train_weather.py
│   │   ├── train_soil.py
│   │   ├── evaluate_models.py
│   │   └── export_models.py
│   │
│   └── tests/                           # Unit & integration tests
│       ├── __init__.py
│       ├── conftest.py
│       ├── test_recommendation/
│       │   ├── __init__.py
│       │   ├── test_model.py
│       │   └── test_service.py
│       ├── test_weather/
│       │   ├── __init__.py
│       │   ├── test_model.py
│       │   └── test_service.py
│       └── test_soil/
│           ├── __init__.py
│           ├── test_model.py
│           └── test_service.py
│
├── backend/                             # Existing backend (updated)
│   └── app/
│       ├── services/                    # New: Service layer for ML integration
│       │   ├── __init__.py
│       │   └── ml_client.py             # HTTP client to call ML service
│       └── routers/
│           ├── recommendation.py        # New: Proxy to ML recommendation
│           └── soil_analysis.py         # New: Proxy to ML soil analysis
│
└── data/                                # Shared data directory (optional)
    ├── raw/                             # Raw datasets
    ├── processed/                       # Cleaned/processed data
    └── external/                        # External data sources
```

---

## Detailed Component Descriptions

### 1. ML Service (`ml_service/`)

A dedicated microservice for all ML operations, allowing independent scaling and development.

#### 1.1 Core Application (`app/`)

| Directory/File | Purpose |
|----------------|---------|
| `main.py` | FastAPI application entry point, includes middleware, CORS, and router registration |
| `config/settings.py` | Environment variables, model paths, API keys, database URLs |

#### 1.2 Models (`app/models/`)

Each model domain (recommendation, weather, soil) follows the same structure:

```python
# base_model.py - Abstract base class
from abc import ABC, abstractmethod

class BaseMLModel(ABC):
    @abstractmethod
    def train(self, X, y):
        pass
    
    @abstractmethod
    def predict(self, X):
        pass
    
    @abstractmethod
    def save(self, path: str):
        pass
    
    @abstractmethod
    def load(self, path: str):
        pass
```

**Recommendation Model** (`models/recommendation/`)
- Input: Soil data, weather data, location, season
- Output: Ranked list of recommended rice varieties with confidence scores
- Potential Algorithms: Random Forest, XGBoost, Neural Network

**Weather Forecasting Model** (`models/weather/`)
- Input: Historical weather data, location, date range
- Output: Predicted weather parameters (temperature, rainfall, humidity)
- Potential Algorithms: LSTM, Prophet, ARIMA, Transformer-based models

**Soil Health Model** (`models/soil/`)
- Input: Soil sensor data (pH, moisture, nutrients, NPK levels)
- Output: 
  - **Health Scoring**: Overall soil health score (0-100), individual parameter scores, deficiency analysis
  - **3-Month Forecast**: Predicted soil conditions aligned with rice planting season (~90-120 days)
- Features:
  - Seasonal trend analysis (per rice planting cycle)
  - Nutrient depletion forecasting
  - pH level predictions
  - Moisture retention projections
- Potential Algorithms: Gradient Boosting, LSTM for time-series forecasting, Neural Networks
#### 1.3 Services (`app/services/`)

Business logic layer that orchestrates model predictions:

```python
# recommendation_service.py
class RecommendationService:
    def __init__(self, model, preprocessor):
        self.model = model
        self.preprocessor = preprocessor
    
    def get_recommendations(self, farm_data: FarmInput) -> List[Recommendation]:
        # 1. Validate input
        # 2. Preprocess data
        # 3. Get model prediction
        # 4. Post-process results
        # 5. Return formatted recommendations
        pass
```

#### 1.4 API Endpoints (`app/routers/`)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/recommend/variety` | POST | Get rice variety recommendations |
| `/api/recommend/schedule` | POST | Get optimal planting schedule |
| `/api/weather/forecast` | POST | Get weather forecast |
| `/api/weather/historical` | GET | Get historical weather analysis |
| `/api/soil/analyze` | POST | Analyze current soil health and generate health score (0-100) |
| `/api/soil/health-score` | POST | Get detailed health scoring with parameter breakdown |
| `/api/soil/forecast` | POST | Get 3-month soil condition forecast (per planting season) |
| `/api/soil/seasonal-forecast` | POST | Get soil forecast aligned with rice growth stages |
| `/api/soil/recommendations` | POST | Get soil improvement recommendations |
| `/health` | GET | Service health check |
| `/models/status` | GET | Check loaded models status |

---

## Implementation Phases

### Phase 1: Foundation Setup (Week 1-2)

- [ ] Create `machine_learning/` directory structure
- [ ] Set up FastAPI application with basic health endpoints
- [ ] Configure Docker for ML service
- [ ] Update `docker-compose.yml` to include ML service
- [ ] Set up database connections and external API connectors
- [ ] Implement base model abstract class
- [ ] Create Pydantic schemas for all endpoints

### Phase 2: Data Pipeline (Week 3-4)

- [ ] Implement data connectors (PostgreSQL, external weather APIs)
- [ ] Create data preprocessing pipelines for each model
- [ ] Set up feature engineering modules
- [ ] Create training data repositories
- [ ] Set up Jupyter notebooks for EDA

### Phase 3: Model Development (Week 5-8)

- [ ] **Recommendation Model**
  - [ ] Exploratory data analysis
  - [ ] Feature selection and engineering
  - [ ] Model training and hyperparameter tuning
  - [ ] Model evaluation and validation
  - [ ] Export trained model

- [ ] **Weather Forecasting Model**
  - [ ] Historical weather data analysis
  - [ ] Time series model development
  - [ ] Model training and validation
  - [ ] Export trained model

- [ ] **Soil Health Model**
  - [ ] Soil data analysis and feature extraction
  - [ ] Health scoring model development (0-100 scale with parameter breakdown)
  - [ ] 3-month seasonal forecasting model (aligned with ~90-120 day rice planting cycle)
  - [ ] Integration of temporal patterns for nutrient depletion
  - [ ] Model training and validation
  - [ ] Export trained models (scoring + forecasting)

### Phase 4: Service Integration (Week 9-10)

- [ ] Implement model loading utilities
- [ ] Create service layer for each model
- [ ] Implement API endpoints
- [ ] Add request/response logging
- [ ] Implement caching for predictions

### Phase 5: Backend Integration (Week 11-12)

- [ ] Create ML client in backend service
- [ ] Add proxy endpoints in backend
- [ ] Update existing endpoints to use ML predictions
- [ ] Add error handling and fallbacks
- [ ] Implement prediction logging

### Phase 6: Testing & Deployment (Week 13-14)

- [ ] Write unit tests for all components
- [ ] Integration testing
- [ ] Performance testing
- [ ] Model monitoring setup
- [ ] Documentation
- [ ] Deployment to production

---

## Docker Compose Update

Add the following service to `docker-compose.yml`:

```yaml
machine_learning:
  build:
    context: ./machine_learning
    dockerfile: Dockerfile
  restart: always
  depends_on:
    postgre:
      condition: service_started
  ports:
    - "8001:8001"
  volumes:
    - ./machine_learning/app:/code/app
    - ./machine_learning/trained_models:/code/trained_models
  environment:
    - DATABASE_URL=postgresql+psycopg2://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}
    - MODEL_PATH=/code/trained_models
  env_file:
    - ./.env
```

---

## Technology Stack

| Component | Technology |
|-----------|------------|
| ML Framework | scikit-learn, TensorFlow/PyTorch |
| Time Series | Prophet, statsmodels |
| API Framework | FastAPI |
| Data Processing | pandas, numpy |
| Model Serialization | joblib, pickle, ONNX |
| Containerization | Docker |
| Database | PostgreSQL |
| Testing | pytest |
| Notebooks | Jupyter |

---

## Dependencies (requirements.txt)

```txt
# API Framework
fastapi>=0.104.0
uvicorn>=0.24.0
pydantic>=2.5.0

# ML Libraries
scikit-learn>=1.3.0
xgboost>=2.0.0
lightgbm>=4.0.0

# Deep Learning (optional, based on model choice)
torch>=2.1.0
tensorflow>=2.15.0

# Time Series
prophet>=1.1.0
statsmodels>=0.14.0

# Data Processing
pandas>=2.1.0
numpy>=1.26.0
scipy>=1.11.0

# Database
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0

# Utilities
python-dotenv>=1.0.0
httpx>=0.25.0
joblib>=1.3.0

# Testing
pytest>=7.4.0
pytest-asyncio>=0.21.0

# Jupyter (for notebooks)
jupyter>=1.0.0
matplotlib>=3.8.0
seaborn>=0.13.0
```

---

## Inter-Service Communication

```
┌─────────────────┐     HTTP/REST      ┌─────────────────┐
│                 │ ─────────────────► │                 │
│    Frontend     │                    │     Backend     │
│   (React Native)│ ◄───────────────── │    (FastAPI)    │
│                 │                    │                 │
└─────────────────┘                    └────────┬────────┘
                                                │
                                                │ HTTP/REST
                                                ▼
                                       ┌─────────────────┐
                                       │                 │
                                       │   ML Service    │
                                       │    (FastAPI)    │
                                       │                 │
                                       └────────┬────────┘
                                                │
                                                │ SQL
                                                ▼
                                       ┌─────────────────┐
                                       │                 │
                                       │   PostgreSQL    │
                                       │                 │
                                       └─────────────────┘
```

---

## Model Versioning Strategy

1. **File Naming Convention**: `{model_name}_v{version}_{date}.pkl`
   - Example: `rice_variety_v1.0_20251228.pkl`

2. **Version Tracking**: Maintain a `model_registry.json` in each model folder:
   ```json
   {
     "current_version": "1.0",
     "models": [
       {
         "version": "1.0",
         "file": "rice_variety_v1.0_20251228.pkl",
         "trained_date": "2025-12-28",
         "metrics": {
           "accuracy": 0.92,
           "f1_score": 0.89
         }
       }
     ]
   }
   ```

3. **Model Loading**: Always load the model specified in `current_version`

---

## Notes & Considerations

1. **Scalability**: The ML service is designed as a separate microservice to allow independent scaling based on prediction load.

2. **Model Updates**: Trained models are stored in a mounted volume for easy updates without rebuilding containers.

3. **Fallback Strategy**: Implement graceful degradation in the backend if ML service is unavailable.

4. **Monitoring**: Consider adding Prometheus metrics for model inference times and prediction distributions.

5. **Data Privacy**: Ensure all training data handling complies with data protection requirements.

6. **GPU Support**: If using deep learning models, consider adding GPU support to the Docker configuration.

---

## Next Steps

1. Review and approve this implementation plan
2. Create initial directory structure
3. Set up ML service Docker configuration
4. Begin Phase 1 implementation
