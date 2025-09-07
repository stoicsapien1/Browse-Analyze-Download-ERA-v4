# Browse Analyze Download (Flask + ydata-profiling)

Beginner-friendly Flask app to upload CSV/Excel datasets, preview first rows, and generate an automated EDA report using ydata-profiling (formerly pandas-profiling).

## Features
- Upload CSV or Excel files
- Preview first 5–10 rows
- Generate and view/download EDA HTML report

## Project Structure
```
Browse Analyze Download/
├─ app.py
├─ templates/
│  ├─ base.html
│  └─ index.html
├─ static/
│  └─ styles.css
├─ uploads/            # temporary uploaded files
├─ reports/            # generated HTML reports
├─ README.md
└─ pyproject.toml      # uv dependency management
```

## Prerequisites
- Python 3.10+
- uv package manager

Install uv (if needed):
```bash
pip install uv
```

## Setup
Install dependencies with uv:
```bash
uv sync
```

## Run the app
```bash
uv run flask --app app run --debug
```

Then open your browser at http://127.0.0.1:5000/

## Usage
1. Choose a CSV or Excel file and upload.
2. Preview appears (first 10 rows).
3. Click "Generate EDA" to produce the HTML report.
4. Open the report link or download it.

## Notes
- Supported Excel engine: openpyxl
- Uploaded files and reports are stored in the local `uploads/` and `reports/` folders. They are not persisted or versioned.

