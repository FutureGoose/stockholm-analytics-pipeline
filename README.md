# Stockholm Analytics Pipeline

A comprehensive data pipeline system for Swedish market analytics, implementing containerized microservices for collecting, processing, and analyzing data from various external APIs with machine learning capabilities.

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/FutureGoose/ai23_data_engineering_project)

## 🏗️ Architecture Overview

The system consists of five main processing domains deployed on Google Cloud Platform:

- **Google Trends Pipeline** - Swedish keyword search trends analysis
- **Weather Prediction ML Pipeline** - XGBoost-powered weather forecasting for Stockholm  
- **Football Analytics Pipeline** - Match statistics and fixture data collection
- **Weather Data Ingestion** - Multi-source weather data collection (WeatherAPI, SMHI)
- **Radiation Data Collection** - Swedish meteorological radiation measurements

## 🚀 Key Features

### Google Trends Analytics [1](#0-0) 

- **Swedish Market Focus**: Localized data collection for Stockholm region (`geo='SE-AB'`)
- **Themed Keyword Categories**: Fashion, Food, Beverages, Weather gear
- **Robust Retry Logic**: 10 retry attempts with exponential backoff
- **Character Normalization**: Handles Swedish characters (å, ä, ö) for BigQuery compatibility

### Weather Prediction ML [2](#0-1) 

- **XGBoost Model**: Trained on 20 years of Stockholm weather data (2004-2024)
- **High Accuracy**: MAE: 1.43°C, RMSE: 1.89°C
- **Feature Engineering**: Temporal and lag features for improved predictions
- **Real-time Inference**: FastAPI endpoints for live weather forecasting

### Football Analytics [3](#0-2) 

- **API Sports Integration**: Fixture details and match statistics
- **Rate Limiting**: Intelligent throttling to respect API quotas
- **Flexible Storage**: JSON document storage for comprehensive match data

### SMHI Radiation Data [4](#0-3)

- **Multi-Parameter Collection**: Six radiation parameters (116, 117, 118, 120, 121, 122)
- **Stockholm-Focused**: Coordinates 59.33258°N, 18.0649°E for accurate local data
- **Historical Data**: 7-day rolling collection for trend analysis
- **Swedish Official Source**: Direct integration with SMHI's meteorological API

## 🛠️ Technology Stack

- **Runtime**: Python 3.x with FastAPI
- **ML Framework**: XGBoost for weather prediction
- **Data Storage**: Google BigQuery
- **Container Platform**: Google Cloud Run
- **Orchestration**: Google Workflows
- **CI/CD**: GitHub Actions
- **APIs**: Google Trends, WeatherAPI, SMHI, API Sports

## 📊 Data Flow

```mermaid
graph TB
    subgraph "External APIs"
        GAPI["Google Trends API"]
        WAPI["WeatherAPI"]
        FAPI["API Sports Football"]
        SMHI["SMHI Swedish Weather API"]
    end
    
    subgraph "Processing Services"
        PTS["pytrends-api-search-clean"]
        WAR["weatherapi-api-weather-raw"]
        FAR["api_sports-api-football-raw"]
        SAR["smhi-api-weather-raw"]
        CWP["clean-weatherprediction-consume<br/>(XGBoost ML)"]
    end
    
    subgraph "BigQuery Storage"
        GTBQ1["google_trends.searchwords_new_1"]
        GTBQ2["google_trends.searchwords_new_2"]
        GTBQ3["google_trends.searchwords_new_3"]
        GTBQ4["google_trends.searchwords_new_4"]
        WBQR["weather_data.raw_weatherapp"]
        WBQC["weather_data.clean_weatherapp<br/>(Manual SQL)"]
        WBQP["weather_data.raw_predictions_weatherapp"]
        FBQF["football_data.raw_fixture_details"]
        FBQS["football_data.raw_fixture_statistics"]
        RBQR["radiation_data.raw_radiationapp"]
    end
    
    %% Active automated flows
    GAPI --> PTS --> GTBQ1
    PTS --> GTBQ2
    PTS --> GTBQ3
    PTS --> GTBQ4
    FAPI --> FAR --> FBQF
    FAR --> FBQS
    SMHI --> SAR --> RBQR
    WAPI --> WAR --> WBQR
    
    %% Manual/Conditional flows
    WBQR -.->|Manual SQL Transform| WBQC
    WBQC --> CWP --> WBQP
    
    %% Styling
    classDef apiClass fill:#e1f5fe
    classDef serviceClass fill:#f3e5f5
    classDef storageClass fill:#e8f5e8
    classDef manualClass fill:#fff3e0,stroke-dasharray: 5 5
    
    class GAPI,WAPI,FAPI,SMHI apiClass
    class PTS,WAR,FAR,SAR,CWP serviceClass
    class GTBQ1,GTBQ2,GTBQ3,GTBQ4,WBQR,WBQP,FBQF,FBQS,RBQR storageClass
    class WBQC manualClass
```

**Note**: The weather data cleaning step (`raw_weatherapp` → `clean_weatherapp`) requires manual SQL execution and is not currently automated in the pipeline.

## 🚀 Deployment

### Prerequisites
- Google Cloud Platform account with BigQuery and Cloud Run enabled
- GitHub repository with Actions enabled
- Service account with appropriate permissions

### Automated Deployment [4](#0-3) 

Each service deploys automatically via GitHub Actions when changes are pushed to the `main` branch:

- **Path-based Triggers**: Only affected services redeploy
- **Regional Deployment**: `europe-north1` for European data residency
- **Container Registry**: `gcr.io/team-god/` namespace
- **Complete Coverage**: All 7 microservices have CI/CD pipelines

### Service Configuration
- **Concurrency**: 2 requests per instance
- **Authentication**: Unauthenticated access for workflow orchestration
- **Monitoring**: Comprehensive logging with error details

## 📈 Performance Metrics

### Weather ML Model
- **Training Data**: 183,817 records spanning 20 years
- **Features**: 7 engineered features including lag variables
- **Target**: Maximum temperature prediction for next 24 hours
- **Accuracy**: MAE 1.43°C, RMSE 1.89°C

### Data Processing
- **Google Trends**: 4 themed keyword categories with retry mechanisms
- **Football Data**: Rate-limited collection (60s pause every 10 requests)
- **Weather Prediction**: Real-time inference with feature validation

## 🔧 Development

### Local Setup
```bash
# Clone repository
git clone https://github.com/FutureGoose/ai23_data_engineering_project.git

# Install dependencies for specific service
cd pipes/[service-name]
pip install -r requirements.txt

# Run service locally
uvicorn src.main:app --host 0.0.0.0 --port 8080
```

### Service Structure
Each pipeline follows a consistent structure:
- `src/main.py` - FastAPI application with endpoints
- `Dockerfile` - Container build configuration  
- `requirements.txt` - Python dependencies
- Corresponding workflow YAML in `pipelines/`

## 📝 API Endpoints

### Weather Prediction Service
- `GET /` - Full prediction pipeline execution
- `GET /predict` - Generate weather predictions
- `GET /bigquery_test` - Fetch sample data

### Google Trends Service  
- `GET /` - Fetch and store trends data for all keyword categories

### Football Analytics Service
- `GET /` - Collect fixture details and statistics

### WeatherAPI Raw Data Service
- `GET /` - Collect historical weather data for specified location and date

### SMHI Radiation Service
- `GET /` - Collect radiation measurements for Stockholm region

### Date Utility Service
- `GET /` - Return yesterday's date in YYYY-MM-DD format

## 🏢 Project Context

This project was developed as part of the AI23 Data Engineering curriculum, demonstrating enterprise-grade data pipeline implementation with:

- **Microservices Architecture**: Independent, scalable services
- **Cloud-Native Design**: Leveraging Google Cloud Platform capabilities  
- **ML Integration**: Production machine learning workflows
- **Swedish Market Focus**: Localized data collection and analysis

---

**Contributors**: FutureGoose, speedan, danhag123, Gustaf Bodén  
**License**: MIT  
**Documentation**: See individual service directories for detailed implementation notes

## Notes

The system implements sophisticated error handling and retry mechanisms across all services, with particular attention to API rate limiting and Swedish character encoding issues. The weather prediction pipeline represents the most complex component, combining data engineering with machine learning for real-time inference capabilities.

Wiki pages you might want to explore:
- [Data Pipelines (FutureGoose/ai23_data_engineering_project)](/wiki/FutureGoose/ai23_data_engineering_project#2)
- [Weather Prediction ML Pipeline (FutureGoose/ai23_data_engineering_project)](/wiki/FutureGoose/ai23_data_engineering_project#2.2.3)