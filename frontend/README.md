ChennaiHomes redesigned Streamlit frontend

Files

app.py: Streamlit frontend with a PDF property valuation report download.

assets/: supplied Chennai coastal image and vintage map.

requirements.txt: frontend dependencies, including ReportLab for PDF generation.

Add this to an existing project

Copy app.py to your project's frontend/app.py and copy the assets folder to frontend/assets/.

Install the added dependency in the project's active virtual environment:

python -m pip install -r frontend/requirements.txt

If your project uses only the root requirements.txt, install ReportLab directly:

python -m pip install reportlab

Start FastAPI from the project root in one terminal:

python -m uvicorn app.main:app --reload

Start Streamlit from the project root in a second terminal:

python -m streamlit run frontend/app.py

The frontend continues to send the existing {"features": {...}} request to the /predict endpoint. The PDF report is created only after a successful prediction and includes the generated estimate, all submitted features, price per square foot when available, generation timestamp, and an informational-use disclaimer.