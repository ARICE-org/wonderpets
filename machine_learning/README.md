# ARICE Machine Learning Service

Machine Learning microservice for the ARICE project.

## Overview

This service provides three core ML capabilities:

1. **Rice Variety Recommendation** - Suggests optimal rice varieties based on soil conditions and weather patterns
2. **Weather Forecasting** - Predicts temperature, rainfall, and humidity for farming planning
3. **Soil Health Analysis** - Scores soil health (0-100) and provides 3-month forecasts aligned with rice growth stages

## Project Structure

```
machine_learning/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── config/                 # Configuration settings
│   ├── models/                 # ML model implementations
│   │   ├── recommendation/     # Rice variety recommendation
│   │   ├── weather/            # Weather forecasting
│   │   └── soil/               # Soil health & forecasting
│   ├── services/               # Business logic layer
│   ├── routers/                # API endpoints
│   ├── schemas/                # Pydantic models
│   ├── utils/                  # Utility functions
│   └── data/                   # Data connectors & repositories
├── trained_models/             # Saved model artifacts
├── notebooks/                  # Jupyter notebooks for training
├── scripts/                    # Training scripts
├── tests/                      # Unit tests
├── Dockerfile
└── requirements.txt
```

## Quick Start

### Using Docker

```bash
# Build the image
docker build -t arice-ml-service .

# Run the container
docker run -p 8001:8001 arice-ml-service
```

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the service
uvicorn app.main:app --reload --port 8001
```

## API Endpoints

### Health Check
- `GET /health` - Service health status
- `GET /models/status` - ML models status

### Recommendation
- `POST /api/recommend/variety` - Get rice variety recommendations
- `POST /api/recommend/batch` - Batch recommendations

### Weather
- `POST /api/weather/forecast` - Get weather forecast
- `GET /api/weather/current/{location_id}` - Current weather

### Soil Analysis
- `POST /api/soil/health` - Analyze soil health
- `POST /api/soil/forecast` - Get 3-month soil forecast
- `POST /api/soil/recommendations` - Get improvement recommendations

## Training Models

### Train All Models
```bash
python scripts/train_all.py --data-source database
```

### Train Individual Models
```bash
python scripts/train_recommendation.py --data-source database
python scripts/train_weather.py --data-source database
python scripts/train_soil_health.py --data-source database
python scripts/train_soil_forecast.py --data-source database
```

## Rice Growth Stages

The soil forecast model aligns predictions with rice growth stages:

| Stage | Days | Critical Nutrients |
|-------|------|-------------------|
| Seedling | 0-15 | Nitrogen, Phosphorus |
| Tillering | 15-45 | Nitrogen, Potassium |
| Panicle Initiation | 45-70 | Phosphorus, Potassium |
| Flowering | 70-90 | Potassium, Nitrogen |
| Grain Filling | 90-120 | Potassium, Phosphorus |

## Soil Health Scoring

Health scores are calculated on a 0-100 scale:

- **90-100**: Excellent - Optimal conditions for rice cultivation
- **75-89**: Good - Minor adjustments may improve yield
- **60-74**: Fair - Some parameters need attention
- **40-59**: Poor - Significant improvements needed
- **0-39**: Critical - Major intervention required

## Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/arice_db

# Service
ML_SERVICE_HOST=0.0.0.0
ML_SERVICE_PORT=8001
DEBUG=false

# Models
MODELS_PATH=/app/trained_models
MODEL_CACHE_SIZE=3
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_recommendation.py -v
```

## Dependencies

Key libraries:
- **FastAPI** - Web framework
- **scikit-learn** - ML algorithms
- **Prophet** - Time series forecasting
- **pandas/numpy** - Data processing
- **SQLAlchemy** - Database ORM
- **Pydantic** - Data validation

## Contributing

1. Create a feature branch
2. Make changes
3. Run tests
4. Submit pull request

## License

This project is part of the ARICE thesis project.
