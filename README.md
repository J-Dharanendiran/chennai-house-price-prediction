# Chennai House Price Prediction

An end-to-end machine learning application for estimating residential property prices in Chennai, Tamil Nadu, India. This project combines data analysis, feature engineering, model development, model evaluation, and API development into a containerized application.

The application allows users to enter property details and obtain an estimated house price through an interactive interface powered by a machine learning model.

## Overview

Real estate prices depend on several factors, including property characteristics, location, and available amenities. This project explores historical housing data to develop a machine learning solution for predicting residential property prices in Chennai.

The project covers the complete machine learning workflow, from raw data exploration to serving predictions through an API and an interactive frontend.

## Key Features

- **Exploratory Data Analysis:** Investigate distributions, relationships, and patterns in the housing dataset.
- **Data Preprocessing:** Clean data, handle missing values, and prepare features for modeling.
- **Feature Engineering:** Transform property attributes into useful model inputs.
- **Feature Selection:** Identify relevant features to support model development.
- **Model Training and Evaluation:** Establish a baseline and evaluate machine learning models.
- **Hyperparameter Tuning:** Optimize the Random Forest model through systematic parameter search.
- **REST API:** Serve predictions using FastAPI.
- **Interactive Frontend:** Provide a user-facing interface for house price estimation.
- **PDF Reports:** Generate downloadable prediction reports.
- **Docker Support:** Package the application and its dependencies for a reproducible environment.
- **Automated Testing:** Test API endpoints, model behavior, and PDF report functionality.

## Technology Stack

| Category | Technologies |
|---|---|
| Programming Language | Python |
| Data Manipulation | Pandas, NumPy |
| Data Visualization | Matplotlib, Seaborn |
| Machine Learning | Scikit-learn |
| Model Persistence | Joblib |
| Backend | FastAPI |
| API Validation | Pydantic |
| Frontend | Python-based web application |
| Testing | Pytest |
| Containerization | Docker, Docker Compose |
| Development Environment | Jupyter Notebook, VS Code |

## Project Structure

```text
chennai-house-price-prediction/
│
├── app/
│   └── main.py
│
├── data/
│   ├── raw/
│   │   └── chennai_house_price_prediction.csv
│   ├── processed/
│   │   └── chennai_house_price_prediction_cleaned.csv
│   └── README.md
│
├── docs/
│   └── problem definition.md
│
├── frontend/
│   ├── assets/
│   ├── app.py
│   ├── pdf_report.py
│   ├── requirements.txt
│   └── README.md
│
├── models/
│   ├── baseline_model.joblib
│   ├── selected_features.joblib
│   ├── selected_model.joblib
│   └── tuned_random_forest.joblib
│
├── notebooks/
│   ├── 01_dataset_inspection.ipynb
│   ├── 02_initial_eda.ipynb
│   ├── 03_data_cleaning.ipynb
│   ├── 04_oulier_analysis.ipynb
│   ├── 05_handling_missing_values.ipynb
│   ├── 06_feature_engineering.ipynb
│   ├── 07_basemodel_prediction_evaluation.ipynb
│   ├── 08_feature_selection.ipynb
│   └── 09_model_training_tuning.ipynb
│
├── reports/
│   └── baseline_model_results.csv
│
├── tests/
│   ├── test_api.py
│   ├── test_model.py
│   └── test_pdf.py
│
├── .dockerignore
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

*Note: The structure above reflects the current repository layout. Additional files may exist in the repository.*

## Machine Learning Workflow

The project follows a structured workflow:

1. **Dataset Inspection:** Understand the dataset, its features, data types, and quality.
2. **Data Cleaning:** Address inconsistencies and prepare the data for analysis.
3. **Exploratory Data Analysis:** Examine distributions, outliers, and relationships between features and house prices.
4. **Feature Engineering:** Transform and prepare features for machine learning.
5. **Baseline Modeling:** Establish an initial performance benchmark.
6. **Feature Selection:** Evaluate the contribution of input features.
7. **Model Training and Tuning:** Train candidate models and tune hyperparameters.
8. **Model Evaluation:** Compare model performance using appropriate regression metrics.
9. **Application Development:** Integrate the selected model into a FastAPI backend and frontend.
10. **Containerization and Testing:** Package the application with Docker and validate its functionality.

## Model Evaluation

Regression models should be evaluated using multiple complementary metrics:

- **R² Score:** Measures the proportion of target variance explained by the model.
- **MAE:** Measures the average absolute prediction error.
- **MSE:** Measures the average squared prediction error.
- **RMSE:** Expresses prediction error on the target's original scale.

The project includes baseline and tuned model artifacts to support model development and comparison.

Actual evaluation results should be reported from the project's saved evaluation outputs. No performance figures are claimed here.

## Getting Started

### Prerequisites

Install the following tools before running the project:

- Python 3.12 or a compatible Python version
- Git
- Docker Desktop, if using containerized execution

### 1. Clone the Repository

```bash
git clone https://github.com/J-Dharanendiran/chennai-house-price-prediction.git
cd chennai-house-price-prediction
```

### 2. Create a Virtual Environment

**Windows PowerShell**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

If PowerShell blocks environment activation, consult the Python documentation for your execution-policy configuration rather than changing security settings unnecessarily.

### 3. Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If the frontend has additional dependencies, install them using:

```bash
pip install -r frontend/requirements.txt
```

### 4. Run the Backend API

From the project root, start the FastAPI application:

```bash
uvicorn app.main:app --reload
```

The default local development address is:

`http://127.0.0.1:8000`

Open the interactive API documentation at:

`http://127.0.0.1:8000/docs`

The API provides an endpoint for checking application status and the endpoints implemented in `app/main.py`.

### 5. Run the Frontend

The frontend entry point is `frontend/app.py`. If it uses Streamlit, launch it with:

```bash
streamlit run frontend/app.py
```

The local frontend address is typically:

`http://localhost:8501`

Install any frontend-specific dependencies before launching the interface. Run the backend as well if the frontend sends prediction requests to the API.

### 6. Run with Docker

Docker provides a reproducible way to package and run the application without manually recreating the Python environment on every machine.

Ensure Docker Desktop is running, then execute:

```bash
docker compose up --build
```

Docker Compose uses the services, ports, and configuration defined in `docker-compose.yml`.

To stop the application:

```bash
docker compose down
```

For individual container and port details, refer to the project's `Dockerfile` and `docker-compose.yml`.

## Running Tests

Run the test suite from the project root:

```bash
pytest
```

The tests cover API behavior, model functionality, and PDF report generation.

## Model Artifacts

The `models/` directory contains serialized model-related artifacts used during model development and application execution.

| Artifact | Purpose |
|---|---|
| `baseline_model.joblib` | Baseline model artifact |
| `selected_features.joblib` | Saved feature-selection information |
| `selected_model.joblib` | Selected model artifact |
| `tuned_random_forest.joblib` | Tuned Random Forest model artifact |

The application must load the correct model and supply features in the expected format. The saved artifacts should remain compatible with the corresponding preprocessing logic and library versions.

Only load Joblib files from trusted sources because serialized Python objects can execute code when deserialized.

## Dataset

The project uses a Chennai house price prediction dataset containing residential property information and associated prices.

The dataset is organized into raw and processed directories:

- `data/raw/`: Source dataset.
- `data/processed/`: Cleaned dataset prepared during the data processing workflow.

Refer to `data/README.md` for additional dataset information.

Before redistributing the dataset, verify its source, license, and applicable usage restrictions.

## Limitations

- Predictions are estimates based on patterns learned from historical data.
- Actual property prices may vary with market conditions, property condition, location, and other factors not represented in the dataset.
- Model performance depends on the quality, coverage, and representativeness of the available data.
- Predictions should not be treated as professional property valuations or guarantees of market price.
- The application is intended for learning, demonstration, and experimentation rather than as a substitute for professional real estate advice.

## Future Improvements

Potential extensions include:

- More extensive model comparison and validation.
- Improved handling of location-specific property characteristics.
- Model monitoring and prediction logging.
- Input validation and API security improvements.
- Automated testing in a continuous integration pipeline.
- Model versioning and reproducible training workflows.
- Deployment to a hosting platform when required.

## Learning Objectives

This project demonstrates practical experience with:

- End-to-end machine learning development.
- Data preprocessing and exploratory analysis.
- Regression modeling and evaluation.
- Feature selection and hyperparameter tuning.
- REST API development with FastAPI.
- Frontend and backend integration.
- Model serialization and loading.
- Automated testing.
- Docker-based application packaging.
- Git and GitHub version control.

## Author

**J. Dharanendiran**

B.Tech Artificial Intelligence and Data Science

GitHub: [J-Dharanendiran](https://github.com/J-Dharanendiran)

## License

No license has been specified for this repository. Unless a license is added, others generally do not receive permission to reuse, modify, or redistribute the project's copyrighted code beyond applicable legal exceptions.

If you intend to make the project open source, consider adding an appropriate license after confirming that you have the rights to license all included materials.
