# ARICE Machine Learning Service

Machine Learning microservice for the ARICE (Agricultural Rice Information and Consulting Expert) project.

## Overview

This service provides ML capabilities for rice farming:

1. **Soil Health Analysis** - Scores soil health (0-100) with detailed parameter breakdown
2. **Hybrid Soil Forecasting** - 3-month forecasts combining Rule-Based soil science with ML corrections
3. **Forecast Realignment** - Adjusts predictions when new sensor data arrives
4. **Rice Variety Recommendation** - Suggests optimal rice varieties based on conditions
5. **Weather Forecasting** - Predicts temperature, rainfall, and humidity

## Architecture

```
Frontend (Expo) ←→ Backend (FastAPI:8000) ←→ ML Service (FastAPI:8001)
                         ↓
                   PostgreSQL DB
```

The ML Service is called only by the Backend - never directly by Frontend.

## Project Structure

```
machine_learning/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── common/                 # Shared utilities (logger, exceptions)
│   ├── config/                 # Configuration settings
│   ├── models/                 # ML model implementations
│   │   ├── recommendation/     # Rice variety recommendation
│   │   ├── weather/            # Weather forecasting
│   │   └── soil/               # Hybrid soil forecasting model
│   ├── services/               # Business logic layer
│   ├── routers/                # API endpoints
│   ├── schemas/                # Pydantic models
│   └── utils/                  # Utility functions
├── data/                       # Training data
│   └── soil/                   # Soil datasets (synthetic, third district)
├── trained_models/             # Saved model artifacts
│   └── soil/                   # Trained hybrid model (.joblib)
├── notebooks/                  # Jupyter notebooks for exploration
├── scripts/                    # Training scripts
├── tests/                      # Unit tests
├── Dockerfile
└── requirements.txt
```

## Quick Start

### Local Development

```bash
# Navigate to machine_learning directory
cd machine_learning

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Train the hybrid soil model
python scripts/train_hybrid_soil.py

# Run the service
uvicorn app.main:app --reload --port 8001
```

### Using Docker

```bash
docker build -t arice-ml-service .
docker run -p 8001:8001 arice-ml-service
```

## API Endpoints

### Health Check
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Service health status |
| `/models/status` | GET | ML models loading status |

### Soil Analysis (`/api/soil`)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/analyze` | POST | Analyze soil health, returns score (0-100) |
| `/health-score-detailed` | POST | Detailed health scoring with parameter breakdown |
| `/hybrid-forecast` | POST | Generate 3-month hybrid forecast |
| `/realign-forecast` | POST | Realign forecast with new sensor data |
| `/status` | GET | Soil service status |

### Recommendation (`/api/recommend`)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/variety` | POST | Get rice variety recommendations |

### Weather (`/api/weather`)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/forecast` | POST | Get weather forecast |

## Training Models

### Train Hybrid Soil Model
```bash
python scripts/train_hybrid_soil.py
python scripts/train_hybrid_soil.py --data-path data/soil/synthetic_soil_timeseries.csv
```

Output:
```
2026-01-04 21:48:39 | INFO | Starting training | Data: synthetic_soil_timeseries.csv
2026-01-04 21:48:39 | INFO | Loaded 1460 records
...
=======================================================
  Parameter Performance (Test R²)
=======================================================
  nitrogen_ppm           0.7108 ██████████████
  phosphorus_ppm         0.6933 █████████████
  ...
=======================================================
2026-01-04 21:48:49 | INFO | Training complete in 9.63s
```

### Train Other Models
```bash
python scripts/train_recommendation.py
python scripts/train_weather.py
```

## Environment Variables

```env
ML_SERVICE_HOST=0.0.0.0
ML_SERVICE_PORT=8001
DEBUG=false
MODELS_PATH=./trained_models
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test
pytest tests/test_soil.py -v
```

## Dependencies

Key libraries:
- **FastAPI** - Web framework
- **scikit-learn** - Random Forest, metrics
- **pandas/numpy** - Data processing
- **joblib** - Model serialization
- **Pydantic** - Data validation
- **httpx** - HTTP client (for Backend→ML calls)

## License

ARICE Thesis Project - Wonderpets Team
