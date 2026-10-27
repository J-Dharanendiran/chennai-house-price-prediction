from __future__ import annotations

import html
import io
import math
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image as ReportLabImage,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


# ============================================================
# 1. CONFIGURATION
# ============================================================

ASSET_DIR = Path(__file__).resolve().parent / "assets"


# User-facing labels for the model's input features.
FEATURE_LABELS = [
    ("AREA", "Property location"),
    ("INT_SQFT", "Built-up area"),
    ("N_BEDROOM", "Bedrooms"),
    ("N_BATHROOM", "Bathrooms"),
    ("N_ROOM", "Total rooms"),
    ("SALE_COND", "Sale condition"),
    ("PARK_FACIL", "Parking facility"),
    ("BUILDTYPE", "Building type"),
    ("UTILITY_AVAIL", "Utility availability"),
    ("STREET", "Street access"),
    ("MZZONE", "Zone code (MZ zone)"),
    ("QS_OVERALL", "Overall quality score"),
    ("COMMIS", "Commission"),
]


# ============================================================
# 2. NUMBER AND PRICE FORMATTING
# ============================================================

def indian_grouping(integer_text: str) -> str:
    """Apply Indian comma grouping to a non-negative integer string."""
    if len(integer_text) <= 3:
        return integer_text

    last_three = integer_text[-3:]
    remaining = integer_text[:-3]
    groups: list[str] = []

    while len(remaining) > 2:
        groups.insert(0, remaining[-2:])
        remaining = remaining[:-2]

    if remaining:
        groups.insert(0, remaining)

    return ",".join(groups + [last_three])


def format_indian_number(value: Any, decimals: int = 0) -> str:
    """Format a number using Indian digit grouping, e.g. 85,00,000."""
    number = float(value)

    if not math.isfinite(number):
        return str(value)

    sign = "-" if number < 0 else ""
    number = abs(number)

    formatted = f"{number:.{decimals}f}"
    integer_part, dot, decimal_part = formatted.partition(".")
    grouped = indian_grouping(integer_part)

    return f"{sign}{grouped}{dot + decimal_part if dot else ''}"


def format_inr(value: Any, decimals: int = 0) -> str:
    """Format a number as Indian rupees."""
    return f"₹{format_indian_number(value, decimals)}"


def parse_numeric_price(value: Any) -> float | None:
    """Parse numeric values and common formatted currency strings safely."""
    if isinstance(value, bool) or value is None:
        return None

    if isinstance(value, (int, float)):
        number = float(value)
        return number if math.isfinite(number) else None

    text = str(value).strip()

    if not text:
        return None

    # Handle values such as 8500000, 85,00,000.00, and ₹85,00,000.
    cleaned = text.replace(",", "")
    match = re.search(r"[-+]?\d+(?:\.\d+)?", cleaned)

    if not match:
        return None

    try:
        number = float(match.group(0))
    except ValueError:
        return None

    return number if math.isfinite(number) else None


def format_prediction_price(
    raw_price: Any,
    currency: str,
) -> tuple[str, float | None]:
    """Format API output without duplicating a currency symbol."""
    numeric_price = parse_numeric_price(raw_price)
    currency = currency.upper().strip()

    is_inr = currency in {"INR", "RS", "RUPEE", "RUPEES", "₹", ""}

    if numeric_price is not None:
        if is_inr:
            return format_inr(numeric_price), numeric_price

        return (
            f"{currency} {format_indian_number(numeric_price)}",
            numeric_price,
        )

    raw_text = html.escape(str(raw_price))

    if is_inr and "₹" not in str(raw_price):
        raw_text = f"₹{raw_text}"

    return raw_text, None


# ============================================================
# 3. PROPERTY FEATURE DISPLAY
# ============================================================

def feature_display_value(key: str, value: Any) -> str:
    """Convert model inputs into readable property details."""
    if key == "INT_SQFT":
        return f"{format_indian_number(value)} sq. ft."

    if key == "COMMIS":
        return format_inr(value)

    if key in {"N_BEDROOM", "N_BATHROOM", "N_ROOM"}:
        return format_indian_number(value)

    if key == "QS_OVERALL":
        return f"{float(value):g} / 5"

    return str(value)


# ============================================================
# 4. PDF VALUATION REPORT GENERATION
# ============================================================

def build_valuation_pdf(
    features: dict[str, Any],
    raw_price: Any,
    currency: str,
    numeric_price: float | None,
) -> bytes:
    """Build a PDF report for a successful property price estimate."""

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=19 * mm,
        leftMargin=19 * mm,
        topMargin=17 * mm,
        bottomMargin=17 * mm,
        title="ChennaiHomes Property Valuation Report",
        author="ChennaiHomes",
    )

    # --------------------------------------------------------
    # Colors
    # --------------------------------------------------------

    ink = colors.HexColor("#202D2B")
    green = colors.HexColor("#1F5B4D")
    muted = colors.HexColor("#687673")
    sand = colors.HexColor("#F5F1E8")
    border = colors.HexColor("#E1E6DE")
    white = colors.white

    # --------------------------------------------------------
    # Paragraph styles
    # --------------------------------------------------------

    styles = getSampleStyleSheet()

    styles.add(
        ParagraphStyle(
            name="CHBrand",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=13,
            textColor=green,
            spaceAfter=4,
        )
    )

    styles.add(
        ParagraphStyle(
            name="CHTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=23,
            leading=28,
            alignment=TA_LEFT,
            textColor=ink,
            spaceBefore=2,
            spaceAfter=5,
        )
    )

    styles.add(
        ParagraphStyle(
            name="CHSubtitle",
            parent=styles["Normal"],
            fontSize=9,
            leading=14,
            textColor=muted,
            spaceAfter=12,
        )
    )

    styles.add(
        ParagraphStyle(
            name="CHSection",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=16,
            textColor=green,
            spaceBefore=13,
            spaceAfter=7,
        )
    )

    styles.add(
        ParagraphStyle(
            name="CHBody",
            parent=styles["BodyText"],
            fontSize=8.5,
            leading=12,
            textColor=ink,
        )
    )

    styles.add(
        ParagraphStyle(
            name="CHSmall",
            parent=styles["BodyText"],
            fontSize=7.5,
            leading=10.5,
            textColor=muted,
        )
    )

    styles.add(
        ParagraphStyle(
            name="CHPrice",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=25,
            leading=30,
            textColor=white,
        )
    )

    styles.add(
        ParagraphStyle(
            name="CHPriceLabel",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#E7EDE7"),
        )
    )

    # --------------------------------------------------------
    # Report header
    # --------------------------------------------------------

    generated_at = datetime.now().astimezone().strftime(
        "%d %B %Y, %I:%M %p %Z"
    )

    price_display, parsed_price = format_prediction_price(
        raw_price,
        currency,
    )

    safe_price = html.escape(price_display)
    story: list[Any] = []

    # Include the map image when available.
    map_path = ASSET_DIR / "chennai_vintage_map.jpeg"

    if map_path.exists():
        try:
            map_image = ReportLabImage(
                str(map_path),
                width=25 * mm,
                height=34 * mm,
            )

            map_image.hAlign = "RIGHT"

            brand_table = Table(
                [
                    [
                        Paragraph(
                            "CHENNAIHOMES  ·  PROPERTY INTELLIGENCE",
                            styles["CHBrand"],
                        ),
                        map_image,
                    ]
                ],
                colWidths=[doc.width - 28 * mm, 28 * mm],
            )

            brand_table.setStyle(
                TableStyle(
                    [
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 0),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                        ("TOPPADDING", (0, 0), (-1, -1), 0),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                    ]
                )
            )

            story.extend([brand_table, Spacer(1, 5 * mm)])

        except Exception:
            story.append(
                Paragraph(
                    "CHENNAIHOMES  ·  PROPERTY INTELLIGENCE",
                    styles["CHBrand"],
                )
            )

    else:
        story.append(
            Paragraph(
                "CHENNAIHOMES  ·  PROPERTY INTELLIGENCE",
                styles["CHBrand"],
            )
        )

    story.append(
        Paragraph(
            "Property valuation report",
            styles["CHTitle"],
        )
    )

    story.append(
        Paragraph(
            f"Generated {html.escape(generated_at)} · Chennai, Tamil Nadu",
            styles["CHSubtitle"],
        )
    )

    # --------------------------------------------------------
    # Estimated price box
    # --------------------------------------------------------

    price_box = Table(
        [
            [
                Paragraph(
                    "MODEL-GENERATED ESTIMATED SALE PRICE",
                    styles["CHPriceLabel"],
                )
            ],
            [Paragraph(safe_price, styles["CHPrice"])],
        ],
        colWidths=[doc.width],
    )

    price_box.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), green),
                ("LEFTPADDING", (0, 0), (-1, -1), 15),
                ("RIGHTPADDING", (0, 0), (-1, -1), 15),
                ("TOPPADDING", (0, 0), (-1, 0), 12),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 3),
                ("TOPPADDING", (0, 1), (-1, 1), 2),
                ("BOTTOMPADDING", (0, 1), (-1, 1), 14),
                ("ROUNDEDCORNERS", [8, 8, 8, 8]),
            ]
        )
    )

    story.extend([price_box, Spacer(1, 5 * mm)])

    # --------------------------------------------------------
    # Property summary
    # --------------------------------------------------------

    area_value = float(features.get("INT_SQFT", 0) or 0)

    if numeric_price is not None and numeric_price >= 0 and area_value > 0:
        price_per_sqft = format_inr(numeric_price / area_value)
    else:
        price_per_sqft = "Not available"

    summary_data = [
        [
            Paragraph("PROPERTY LOCATION", styles["CHSmall"]),
            Paragraph("BUILT-UP AREA", styles["CHSmall"]),
            Paragraph("ESTIMATED PRICE / SQ. FT.", styles["CHSmall"]),
        ],
        [
            Paragraph(
                f"<b>{html.escape(str(features.get('AREA', '—')))}</b>",
                styles["CHBody"],
            ),
            Paragraph(
                f"<b>{format_indian_number(area_value)} sq. ft.</b>",
                styles["CHBody"],
            ),
            Paragraph(
                f"<b>{html.escape(price_per_sqft)}</b>",
                styles["CHBody"],
            ),
        ],
    ]

    summary = Table(
        summary_data,
        colWidths=[doc.width / 3] * 3,
    )

    summary.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), sand),
                ("BOX", (0, 0), (-1, -1), 0.6, border),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, border),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 9),
                ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                ("TOPPADDING", (0, 0), (-1, 0), 8),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 3),
                ("TOPPADDING", (0, 1), (-1, 1), 3),
                ("BOTTOMPADDING", (0, 1), (-1, 1), 9),
            ]
        )
    )

    story.extend(
        [
            summary,
            Paragraph("Property details", styles["CHSection"]),
        ]
    )

    # --------------------------------------------------------
    # All submitted property features
    # --------------------------------------------------------

    detail_rows = [
        [
            Paragraph("<b>Feature</b>", styles["CHBody"]),
            Paragraph("<b>Submitted value</b>", styles["CHBody"]),
        ]
    ]

    for key, label in FEATURE_LABELS:
        if key in features:
            detail_rows.append(
                [
                    Paragraph(
                        html.escape(label),
                        styles["CHBody"],
                    ),
                    Paragraph(
                        html.escape(
                            feature_display_value(key, features[key])
                        ),
                        styles["CHBody"],
                    ),
                ]
            )

    details = Table(
        detail_rows,
        colWidths=[doc.width * 0.56, doc.width * 0.44],
        repeatRows=1,
    )

    details.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), green),
                ("TEXTCOLOR", (0, 0), (-1, 0), white),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [white, colors.HexColor("#F8F9F6")],
                ),
                ("GRID", (0, 0), (-1, -1), 0.45, border),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    story.append(details)

    # --------------------------------------------------------
    # Valuation disclaimer
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "Important information",
            styles["CHSection"],
        )
    )

    story.append(
        Paragraph(
            "This report records an automated estimate produced by a "
            "machine-learning model from the details supplied. "
            "It is not a professional property valuation, an appraisal, "
            "a verified current market quote, or a guarantee of a property's "
            "selling price. Results depend on the model, its training data, "
            "and the accuracy and suitability of the submitted information. "
            "Independent verification is recommended before making financial "
            "or property decisions.",
            styles["CHBody"],
        )
    )

    story.append(Spacer(1, 4 * mm))

    story.append(
        Paragraph(
            "ChennaiHomes · Machine-learning property estimate "
            "· For informational use only",
            styles["CHSmall"],
        )
    )

    # --------------------------------------------------------
    # Page footer
    # --------------------------------------------------------

    def add_page_number(canvas: Any, document: Any) -> None:
        canvas.saveState()

        canvas.setStrokeColor(border)
        canvas.line(
            19 * mm,
            13 * mm,
            A4[0] - 19 * mm,
            13 * mm,
        )

        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(muted)

        canvas.drawString(
            19 * mm,
            8 * mm,
            "ChennaiHomes | Property Valuation Report",
        )

        canvas.drawRightString(
            A4[0] - 19 * mm,
            8 * mm,
            f"Page {document.page}",
        )

        canvas.restoreState()

    # Build the PDF and return its bytes.
    doc.build(
        story,
        onFirstPage=add_page_number,
        onLaterPages=add_page_number,
    )

    return buffer.getvalue()

