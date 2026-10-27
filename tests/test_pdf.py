from io import BytesIO

import pytest
from pypdf import PdfReader

from frontend.pdf_report import (
    FEATURE_LABELS,
    build_valuation_pdf,
    format_inr,
    format_prediction_price,
)


@pytest.fixture
def sample_features():
    return {
        "AREA": "Anna Nagar",
        "INT_SQFT": 1500,
        "N_BEDROOM": 3,
        "N_BATHROOM": 2,
        "N_ROOM": 5,
        "SALE_COND": "AbNormal",
        "PARK_FACIL": "Yes",
        "BUILDTYPE": "House",
        "UTILITY_AVAIL": "AllPub",
        "STREET": "Paved",
        "MZZONE": "Residential",
        "QS_OVERALL": 4.0,
        "COMMIS": 0,
    }


@pytest.fixture
def sample_pdf(sample_features):
    return build_valuation_pdf(
        features=sample_features,
        raw_price=7500000,
        currency="INR",
        numeric_price=7500000.0,
    )


def test_pdf_generation_returns_bytes(sample_pdf):
    assert isinstance(sample_pdf, bytes)
    assert len(sample_pdf) > 0


def test_pdf_has_valid_signature(sample_pdf):
    assert sample_pdf.startswith(b"%PDF-")


def test_pdf_can_be_opened(sample_pdf):
    reader = PdfReader(BytesIO(sample_pdf))

    assert len(reader.pages) >= 1


def test_pdf_contains_property_details(sample_pdf):
    reader = PdfReader(BytesIO(sample_pdf))
    text = "\n".join(
        page.extract_text() or ""
        for page in reader.pages
    )

    assert "Anna Nagar" in text
    assert "1,500 sq. ft." in text
    assert "Bedrooms" in text
    assert "Bathrooms" in text


def test_pdf_contains_predicted_price(sample_pdf):
    reader = PdfReader(BytesIO(sample_pdf))
    text = "\n".join(
        page.extract_text() or ""
        for page in reader.pages
    )

    assert "75,00,000" in text


def test_feature_labels_are_defined():
    assert isinstance(FEATURE_LABELS, list)
    assert len(FEATURE_LABELS) == 13

    feature_names = [
        feature_name
        for feature_name, _ in FEATURE_LABELS
    ]

    assert len(feature_names) == len(set(feature_names))
    assert "AREA" in feature_names
    assert "INT_SQFT" in feature_names




@pytest.mark.parametrize(
    ("price", "expected"),
    [
        (1000, "₹1,000"),
        (100000, "₹1,00,000"),
        (7500000, "₹75,00,000"),
        (10000000, "₹1,00,00,000"),
    ],
)
def test_format_inr(price, expected):
    assert format_inr(price) == expected


def test_format_prediction_price_returns_expected_values():
    formatted_price, numeric_price = format_prediction_price(
        7500000,
        "INR",
    )

    assert "75,00,000" in formatted_price
    assert numeric_price == 7500000.0
