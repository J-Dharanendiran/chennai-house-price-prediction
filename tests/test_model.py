from pathlib import Path
import joblib
import numpy as np
import pandas as pd

# --------------------------------------------------
# 1. Load the saved model pipeline
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "tuned_random_forest.joblib"
model = joblib.load(MODEL_PATH)

# --------------------------------------------------
# 2. Define a valid sample input
# --------------------------------------------------
SAMPLE_INPUT = pd.DataFrame(
    [
        {
            "AREA": "CHROMPET",
            "INT_SQFT": 1200,
            "N_BEDROOM": 3,
            "N_BATHROOM": 2,
            "N_ROOM": 4,
            "SALE_COND": "AbNormal",
            "PARK_FACIL": "Yes",
            "BUILDTYPE": "House",
            "UTILITY_AVAIL": "AllPub",
            "STREET": "Paved",
            "MZZONE": "RH",
            "QS_OVERALL": 4.0,
            "COMMIS": 50000,
        }
    ]
)


# --------------------------------------------------
# 3. Test that the model loads successfully
# --------------------------------------------------
def test_model_loaded():
    assert model is not None


# --------------------------------------------------
# 4. Test the number of expected features
# --------------------------------------------------
def test_model_feature_count():
    assert len(model.feature_names_in_) == 13


# --------------------------------------------------
# 5. Test the expected feature names
# --------------------------------------------------
def test_model_feature_names():
    expected_features = [
        "AREA",
        "INT_SQFT",
        "N_BEDROOM",
        "N_BATHROOM",
        "N_ROOM",
        "SALE_COND",
        "PARK_FACIL",
        "BUILDTYPE",
        "UTILITY_AVAIL",
        "STREET",
        "MZZONE",
        "QS_OVERALL",
        "COMMIS",
    ]
    assert list(model.feature_names_in_) == expected_features


# --------------------------------------------------
# 6. Test that the model produces a prediction
# --------------------------------------------------
def test_model_prediction():
    prediction = model.predict(SAMPLE_INPUT)
    assert len(prediction) == 1


# --------------------------------------------------
# 7. Test that the prediction is numeric and finite
# --------------------------------------------------
def test_model_prediction_is_finite():
    prediction = model.predict(SAMPLE_INPUT)
    assert np.issubdtype(prediction.dtype, np.number)
    assert np.isfinite(prediction).all()


# --------------------------------------------------
# 8. Test that the prediction is nonnegative
# --------------------------------------------------
def test_model_prediction_is_nonnegative():
    prediction = model.predict(SAMPLE_INPUT)
    assert prediction[0] >= 0


# --------------------------------------------------
# 9. Test prediction consistency
# --------------------------------------------------
def test_model_prediction_consistency():
    first_prediction = model.predict(SAMPLE_INPUT)
    second_prediction = model.predict(SAMPLE_INPUT)
    np.testing.assert_allclose(
        first_prediction,
        second_prediction,
    )