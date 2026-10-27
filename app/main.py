from pathlib import Path

import joblib
import pandas as pd

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


# --------------------------------------------------
# 1. Create the FastAPI application
# --------------------------------------------------

app = FastAPI(
    title="Chennai House Price Prediction API",
    description="Predict house prices in Chennai using a trained ML model.",
    version="1.0.0"
)


# --------------------------------------------------
# 2. Load the saved model pipeline
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = BASE_DIR / "models" / "tuned_random_forest.joblib"

model = joblib.load(MODEL_PATH)


# --------------------------------------------------
# 3. Define the request format
# --------------------------------------------------

class HouseFeatures(BaseModel):
    AREA: str
    INT_SQFT: float
    N_BEDROOM: float
    N_BATHROOM: float
    N_ROOM: float
    SALE_COND: str
    PARK_FACIL: str
    BUILDTYPE: str
    UTILITY_AVAIL: str
    STREET: str
    MZZONE: str
    QS_OVERALL: float
    COMMIS: float


class HouseDetails(BaseModel):
    features: HouseFeatures

def format_indian_price(price):
    integer_part, decimal_part = f"{price:.2f}".split(".")

    last_three = integer_part[-3:]
    remaining = integer_part[:-3]

    if remaining:
        remaining = remaining[::-1]
        remaining = ",".join(
            remaining[i:i + 2]
            for i in range(0, len(remaining), 2)
        )[::-1]

        integer_part = remaining + "," + last_three
    else:
        integer_part = last_three

    return f"{integer_part}.{decimal_part}"

# --------------------------------------------------
# 4. Create a home endpoint
# --------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "Chennai House Price Prediction API is running!"
    }


# --------------------------------------------------
# 5. Create the prediction endpoint
# --------------------------------------------------

@app.post("/predict")
def predict_price(house: HouseDetails):

    try:
        # Convert the submitted details into a DataFrame
        input_data = pd.DataFrame([house.features.model_dump()])

        # Check the expected input columns
        expected_columns = list(model.feature_names_in_)

        missing_columns = [
            col for col in expected_columns
            if col not in input_data.columns
        ]

        extra_columns = [
            col for col in input_data.columns
            if col not in expected_columns
        ]

        if missing_columns:
            raise HTTPException(
                status_code=422,
                detail={
                    "error": "Missing required features",
                    "missing_columns": missing_columns
                }
            )

        if extra_columns:
            raise HTTPException(
                status_code=422,
                detail={
                    "error": "Unexpected features",
                    "extra_columns": extra_columns
                }
            )

        # Arrange columns in the expected order
        input_data = input_data[expected_columns]

        # Predict the house price
        prediction = model.predict(input_data)[0]

        return {
            "predicted_price": format_indian_price(float(prediction)),
            "currency": "INR"
        }

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(error)}"
        )

