# Chennai Residential House Price Predictor API

## 1. Project Overview

The Chennai Residential House Price Predictor API is a machine learning application designed to estimate residential property sale prices in Chennai, Tamil Nadu, India.

The application will use historical housing data and property characteristics to generate price estimates through a REST API.

The project will combine supervised machine learning, data preprocessing, model evaluation, API development, automated testing, Docker, and cloud deployment.

## 2. Problem Statement

Estimating the sale price of a residential property can be challenging for buyers, sellers, and real estate professionals.

Property prices may vary according to location, interior area, building characteristics, amenities, and other relevant factors.

The objective of this project is to develop a regression model that estimates a residential property's sale price using relevant property characteristics from the selected Chennai House Price Prediction dataset.

The trained model will be exposed through a FastAPI service so that users can submit property information and receive a numerical price estimate.

## 3. Business Objective

Provide an initial property-price estimate that may help users conduct preliminary residential property research.

The intended users are:

* Residential property buyers.
* Residential property sellers.
* Real estate agents and property consultants.

The application will be positioned as a preliminary estimation tool rather than an official valuation service.

Its commercial usefulness will need to be evaluated through predictive performance, appropriate real-world comparisons, and user feedback.

## 4. Geographical and Property Scope

Geographical scope: Chennai, Tamil Nadu, India.

Initial property scope: Residential houses represented in the selected dataset.

The initial data-preparation stage will investigate restricting the dataset to records labelled `House` in the `BUILDTYPE` column.

Supported localities will be determined by inspecting the dataset's geographical coverage and evaluating whether the available observations support reliable predictions.

The first version will not claim to support every property category or locality in Chennai.

## 5. Dataset and Prediction Target

Selected dataset: Chennai House Price Prediction dataset hosted on GitHub.

Intended prediction target: `SALES_PRICE`.

The target column, currency, units, record provenance, geographical coverage, and date coverage must be verified during dataset inspection.

The repository's documented features include property size, number of bedrooms, number of bathrooms, locality, building type, parking availability, utilities, street characteristics, and zoning information.

The final feature list will be established after inspecting the actual CSV.

## 6. Candidate Input Features

Candidate features include:

* `AREA`: Property locality.
* `INT_SQFT`: Interior area in square feet.
* `N_BEDROOM`: Number of bedrooms.
* `N_BATHROOM`: Number of bathrooms.
* `N_ROOM`: Total number of rooms.
* `DIST_MAINROAD`: Distance from the main road.
* `PARK_FACIL`: Parking availability.
* `UTILITY_AVAIL`: Availability of utilities.
* `STREET`: Street category.
* `MZZONE`: Zoning category.

Only features that are appropriate for the intended prediction scenario will be retained.

Transaction identifiers and information unavailable at the time of prediction will be excluded.

Quality scores based on buyer reviews will be excluded from the initial input schema unless their availability and suitability can be established.

## 7. Machine Learning Approach

The project will compare the following regression approaches:

1. Dummy Regressor as a baseline.
2. Linear Regression as a simple predictive model.
3. Random Forest Regressor as a nonlinear ensemble model.

A consistent preprocessing and evaluation workflow will be used.

The final model will be chosen based on measured performance on held-out data, not on algorithm complexity alone.

## 8. Model Evaluation

Model performance will be evaluated using:

* Mean Absolute Error (MAE).
* Root Mean Squared Error (RMSE).
* R².

The project will investigate large prediction errors and differences in performance across supported localities or property categories.

The selected model should outperform the baseline under a suitable evaluation procedure.

No predictive accuracy or business-performance threshold will be claimed before the data and models have been evaluated.

## 9. Application Architecture

The application will contain:

* A reproducible model-training pipeline.
* Data preprocessing and feature transformation.
* Model evaluation and selection.
* Serialization and loading of the selected pipeline.
* A FastAPI prediction endpoint.
* Request validation using Pydantic.
* Automated API and preprocessing tests.
* Docker packaging.
* Public deployment.
* API documentation.

## 10. Expected Input and Output

The API will accept a structured request containing the supported property characteristics.

It will return a numerical estimated sale price.

The final request schema and output units will be defined after the dataset has been inspected and the target scale verified.

The API will reject invalid inputs and handle unsupported feature values appropriately.

## 11. Success Criteria

The project will be considered technically successful when:

1. The dataset can be processed using documented, reproducible steps.
2. The regression models can be trained and compared.
3. Evaluation metrics and important limitations are documented.
4. The selected pipeline can be saved and loaded successfully.
5. The API produces predictions for valid requests.
6. Automated tests cover important valid and invalid input cases.
7. The application runs successfully in Docker.
8. The public deployment and API documentation are accessible.
9. The README explains how to install, run, test, and evaluate the project.

Commercial usefulness will require additional evidence from appropriate real-world comparisons and intended-user feedback.

## 12. Assumptions and Limitations

The model's performance will depend on the quality, recency, and representativeness of the training data.

The dataset's provenance, license, date coverage, and target units must be verified before stronger claims are made about its real-world relevance.

Historical prediction performance will not automatically establish accuracy in the current housing market.

Predictions will be limited to the supported property categories and geographical areas represented adequately in the training data.

The application will provide model-generated estimates rather than guaranteed sale prices or official property valuations.

## 13. Definition of Completion

The project will be considered technically complete when the training pipeline is reproducible, the selected model has been evaluated, the API has been tested, the application has been packaged in Docker, and the service has been successfully deployed.

The repository will document its dataset source, model results, limitations, API usage, installation steps, and deployment details.
