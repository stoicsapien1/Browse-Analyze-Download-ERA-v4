from __future__ import annotations

import os
import uuid
from pathlib import Path
from typing import Tuple

from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
import pandas as pd
from ydata_profiling import ProfileReport


BASE_DIR = Path(__file__).resolve().parent
UPLOAD_FOLDER = BASE_DIR / "uploads"
REPORT_FOLDER = BASE_DIR / "reports"
ALLOWED_EXTENSIONS = {"csv", "xlsx", "xls"}


def ensure_directories_exist() -> None:
    UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
    REPORT_FOLDER.mkdir(parents=True, exist_ok=True)


def create_app() -> Flask:
    ensure_directories_exist()

    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")
    app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)
    app.config["REPORT_FOLDER"] = str(REPORT_FOLDER)
    app.config["MAX_CONTENT_LENGTH"] = 200 * 1024 * 1024  # 200 MB

    @app.route("/")
    def index():
        return render_template("index.html")

    def allowed_file(filename: str) -> bool:
        return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

    def read_dataframe(file_path: Path) -> pd.DataFrame:
        suffix = file_path.suffix.lower()
        if suffix == ".csv":
            return pd.read_csv(file_path)
        if suffix in {".xlsx", ".xls"}:
            return pd.read_excel(file_path, engine="openpyxl")
        raise ValueError("Unsupported file type")

    @app.route("/upload", methods=["POST"])
    def upload():
        if "dataset" not in request.files:
            flash("No file part in the request")
            return redirect(url_for("index"))

        uploaded_file = request.files["dataset"]
        if uploaded_file.filename == "":
            flash("No file selected")
            return redirect(url_for("index"))

        if not allowed_file(uploaded_file.filename):
            flash("Unsupported file type. Please upload CSV or Excel.")
            return redirect(url_for("index"))

        unique_id = uuid.uuid4().hex
        ext = uploaded_file.filename.rsplit(".", 1)[1].lower()
        safe_name = f"dataset_{unique_id}.{ext}"
        save_path = UPLOAD_FOLDER / safe_name
        uploaded_file.save(save_path)

        try:
            df = read_dataframe(save_path)
        except Exception as exc:
            flash(f"Failed to read file: {exc}")
            return redirect(url_for("index"))

        preview_html = df.head(10).to_html(classes="dataframe", index=False, border=0)

        return render_template(
            "index.html",
            preview_html=preview_html,
            file_token=unique_id,
            stored_filename=safe_name,
        )

    @app.route("/generate", methods=["POST"])
    def generate():
        stored_filename = request.form.get("stored_filename")
        if not stored_filename:
            flash("Missing file reference. Please upload again.")
            return redirect(url_for("index"))

        file_path = UPLOAD_FOLDER / stored_filename
        if not file_path.exists():
            flash("Uploaded file not found. Please upload again.")
            return redirect(url_for("index"))

        try:
            df = read_dataframe(file_path)
            profile = ProfileReport(df, title="Automated EDA Report", explorative=True)
            report_name = f"report_{Path(stored_filename).stem}.html"
            report_path = REPORT_FOLDER / report_name
            profile.to_file(report_path)
        except Exception as exc:
            flash(f"Failed to generate report: {exc}")
            return redirect(url_for("index"))

        report_url = url_for("serve_report", filename=report_name)
        return render_template("index.html", report_url=report_url)

    @app.route("/reports/<path:filename>")
    def serve_report(filename: str):
        return send_from_directory(app.config["REPORT_FOLDER"], filename, as_attachment=False)

    return app





app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
