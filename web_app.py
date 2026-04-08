"""Flask web interface for PlantUML to Draw.io conversion."""

import io
import json
import os
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_file

# Ensure the src directory is in the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from plantuml2drawio.drawio_embed_converter import (ConversionError,
                                                    convert_plantuml_to_drawio_xml)

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB max upload

TEXT_EXTENSIONS = {".puml", ".plantuml", ".txt"}


def convert_plantuml_content(plantuml_content: str, output_json: bool):
    """Convert PlantUML content and normalize error handling."""
    if not isinstance(plantuml_content, str):
        return None, None, "PlantUML content must be a string"

    cleaned_content = plantuml_content.strip()
    if not cleaned_content:
        return None, None, "PlantUML content is empty"

    try:
        drawio_xml = convert_plantuml_to_drawio_xml(cleaned_content)
    except ConversionError as exc:
        return None, None, str(exc)

    if output_json:
        result = json.dumps(
            {
                "engine": "rglaue/plantuml_to_drawio-compatible",
                "outputFormat": "Draw.io XML",
                "drawioXml": drawio_xml,
            },
            indent=2,
        )
        return result, "JSON", None

    return drawio_xml, "Draw.io XML", None


def normalize_output_name(filename: str, extension: str) -> str:
    """Generate a safe output filename for batch downloads."""
    stem = Path(filename or "diagram").stem.strip() or "diagram"
    safe_stem = "".join(char if char.isalnum() or char in {"-", "_"} else "_" for char in stem)
    return f"{safe_stem}{extension}"


def read_uploaded_text(uploaded_file):
    """Read an uploaded text file as UTF-8."""
    file_extension = Path(uploaded_file.filename or "").suffix.lower()
    if file_extension and file_extension not in TEXT_EXTENSIONS:
        return None, f"Unsupported file type: {uploaded_file.filename}"

    try:
        return uploaded_file.read().decode("utf-8"), None
    except UnicodeDecodeError:
        return None, f"File is not valid UTF-8 text: {uploaded_file.filename}"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/convert", methods=["POST"])
def convert():
    data = request.get_json()
    if not data or "plantuml" not in data:
        return jsonify({"error": "No PlantUML content provided"}), 400

    output_json = data.get("format") == "json"
    result, output_format, error = convert_plantuml_content(
        data["plantuml"],
        output_json=output_json,
    )

    if error:
        status_code = 400 if error in {"PlantUML content is empty", "PlantUML content must be a string"} else 422
        return jsonify({"error": error}), status_code

    return jsonify({"result": result, "format": output_format})


@app.route("/convert/batch", methods=["POST"])
def convert_batch():
    files = request.files.getlist("files")
    if not files:
        return jsonify({"error": "No files uploaded"}), 400

    output_json = request.form.get("format") == "json"
    output_extension = ".json" if output_json else ".drawio.xml"
    archive_buffer = io.BytesIO()
    converted_files = []
    failed_files = []
    used_names = set()

    with zipfile.ZipFile(archive_buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        for uploaded_file in files:
            if not uploaded_file.filename:
                continue

            content, read_error = read_uploaded_text(uploaded_file)
            if read_error:
                failed_files.append({"file": uploaded_file.filename, "error": read_error})
                continue

            result, _, convert_error = convert_plantuml_content(content, output_json=output_json)
            if convert_error:
                failed_files.append({"file": uploaded_file.filename, "error": convert_error})
                continue

            output_name = normalize_output_name(uploaded_file.filename, output_extension)
            suffix = 1
            unique_name = output_name
            while unique_name in used_names:
                unique_name = f"{Path(output_name).stem}_{suffix}{output_extension}"
                suffix += 1

            used_names.add(unique_name)
            archive.writestr(unique_name, result)
            converted_files.append(unique_name)

        report = {
            "converted": converted_files,
            "failed": failed_files,
            "format": "json" if output_json else "drawio",
        }
        archive.writestr("conversion-report.json", json.dumps(report, indent=2))

    if not converted_files:
        return jsonify(
            {
                "error": "No files could be converted",
                "failed": failed_files,
            }
        ), 422

    archive_buffer.seek(0)
    response = send_file(
        archive_buffer,
        mimetype="application/zip",
        as_attachment=True,
        download_name="converted-diagrams.zip",
    )
    response.headers["X-Converted-Count"] = str(len(converted_files))
    response.headers["X-Failed-Count"] = str(len(failed_files))
    return response


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
