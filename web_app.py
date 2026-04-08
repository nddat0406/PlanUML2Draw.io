"""Flask web interface for PlantUML to Draw.io conversion."""

import os
import sys

from flask import Flask, render_template, request, jsonify

# Ensure the src directory is in the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from plantuml2drawio.core import process_diagram

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024  # 1 MB max upload


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/convert", methods=["POST"])
def convert():
    data = request.get_json()
    if not data or "plantuml" not in data:
        return jsonify({"error": "No PlantUML content provided"}), 400

    plantuml_content = data["plantuml"].strip()
    if not plantuml_content:
        return jsonify({"error": "PlantUML content is empty"}), 400

    output_json = data.get("format") == "json"

    result, output_format = process_diagram(plantuml_content, output_json=output_json)

    if result is None:
        return jsonify({"error": "Failed to convert. Make sure the PlantUML content is a valid activity diagram."}), 422

    return jsonify({
        "result": result,
        "format": output_format,
    })


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
