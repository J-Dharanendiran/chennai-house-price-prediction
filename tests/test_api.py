import math
import pytest
from fastapi.testclient import TestClient

from app.main import app, format_indian_price

client = TestClient(app)


# --------------------------------------------------
# 1. Test the home endpoint
# --------------------------------------------------

def test_home_endpoint():
    response = client.get("/")

    assert response.status_code == 200

    assert response.json() == {
        "message": "Chennai House Price Prediction API is running!"
    }


# --------------------------------------------------
# 2. Test Indian price formatting
# --------------------------------------------------

@pytest.mark.parametrize(
    "price, expected",
    [
        (8500000, "85,00,000.00"),
        (125000, "1,25,000.00"),
        (50000, "50,000.00"),
        (999, "999.00"),
        (0, "0.00"),
    ],
)
def test_format_indian_price(price, expected):
    assert format_indian_price(price) == expected


# --------------------------------------------------
# 3. Test prediction with valid input
# --------------------------------------------------

def test_prediction_endpoint():
    payload = {
        "features": {
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
    }

    response = client.post("/predict", json=payload)

    assert response.status_code == 200

    result = response.json()

    assert "predicted_price" in result
    assert "currency" in result

    assert result["currency"] == "INR"
    assert isinstance(result["predicted_price"], str)
    assert result["predicted_price"] != ""


# --------------------------------------------------
# 4. Test missing required input
# --------------------------------------------------

def test_prediction_missing_required_feature():
    payload = {
        "features": {
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
            # COMMIS intentionally omitted
        }
    }

    response = client.post("/predict", json=payload)

    assert response.status_code == 422


# --------------------------------------------------
# 5. Test invalid numeric input
# --------------------------------------------------

def test_prediction_invalid_numeric_input():
    payload = {
        "features": {
            "AREA": "CHROMPET",
            "INT_SQFT": "not_a_number",
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
    }

    response = client.post("/predict", json=payload)

    assert response.status_code == 422

# --------------------------------------------------
# 6. Test an unknown endpoint
# --------------------------------------------------

def test_unknown_endpoint():
    response = client.get("/unknown-endpoint")

    assert response.status_code == 404


# --------------------------------------------------
# 7. Test malformed prediction request
# --------------------------------------------------

def test_prediction_missing_features_object():
    payload = {}

    response = client.post("/predict", json=payload)

    assert response.status_code == 422


# --------------------------------------------------
# 8. Test prediction consistency
# --------------------------------------------------

def test_prediction_consistency():
    payload = {
        "features": {
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
    }

    first_response = client.post("/predict", json=payload)
    second_response = client.post("/predict", json=payload)

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    first_price = first_response.json()["predicted_price"]
    second_price = second_response.json()["predicted_price"]

    assert first_price == second_price


# --------------------------------------------------
# 9. Test predicted price validity
# --------------------------------------------------

def test_predicted_price_is_valid():
    payload = {
        "features": {
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
    }

    response = client.post("/predict", json=payload)

    assert response.status_code == 200

    result = response.json()

    price_string = result["predicted_price"]

    # Remove Indian-style grouping commas before conversion.
    price = float(price_string.replace(",", ""))

    assert math.isfinite(price)
    assert price >= 0