"""Convert PlantUML text to Draw.io XML by embedding rendered SVG.

This module follows the same basic approach as rglaue/plantuml_to_drawio:
render PlantUML to SVG with the PlantUML jar, then embed both the PlantUML
source and rendered SVG into a Draw.io file.
"""

from __future__ import annotations

import base64
import json
import os
import re
import subprocess
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


DEFAULT_JAVA_BIN = os.environ.get("JAVA_BIN", "java")
DEFAULT_PLANTUML_JAR_URL = os.environ.get(
    "PLANTUML_JAR_URL",
    "https://github.com/plantuml/plantuml/releases/download/v1.2024.4/plantuml-1.2024.4.jar",
)
DEFAULT_PLANTUML_JAR_PATH = Path(
    os.environ.get(
        "PLANTUML_JAR_PATH",
        Path(__file__).resolve().parents[2] / "tools" / "plantuml-1.2024.4.jar",
    )
)

SVG_DIMENSION_RE = re.compile(r"([0-9]+(?:\.[0-9]+)?)")


class ConversionError(RuntimeError):
    """Raised when PlantUML cannot be converted to Draw.io XML."""


def ensure_plantuml_jar(jar_path: Path | None = None) -> Path:
    """Ensure the PlantUML jar exists locally, downloading it if necessary."""
    resolved_path = Path(jar_path or DEFAULT_PLANTUML_JAR_PATH)
    if resolved_path.exists():
        return resolved_path

    resolved_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with urllib.request.urlopen(DEFAULT_PLANTUML_JAR_URL, timeout=60) as response:
            resolved_path.write_bytes(response.read())
    except Exception as exc:  # pragma: no cover - network dependent
        raise ConversionError(
            "PlantUML jar is missing and automatic download failed. "
            "Set PLANTUML_JAR_PATH to a local jar or allow outbound downloads."
        ) from exc

    return resolved_path


def render_svg(plantuml_content: str, java_bin: str = DEFAULT_JAVA_BIN) -> str:
    """Render PlantUML text to SVG using the PlantUML jar."""
    jar_path = ensure_plantuml_jar()

    try:
        process = subprocess.run(
            [java_bin, "-Djava.awt.headless=true", "-jar", str(jar_path), "-tsvg", "-pipe"],
            input=plantuml_content,
            text=True,
            encoding="utf-8",
            capture_output=True,
            timeout=30,
            check=False,
        )
    except FileNotFoundError as exc:
        raise ConversionError(
            "Java runtime not found. Install Java or set JAVA_BIN to a valid executable."
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise ConversionError("PlantUML rendering timed out.") from exc

    if process.returncode != 0:
        message = process.stderr.strip() or "PlantUML rendering failed."
        raise ConversionError(message)

    svg = process.stdout.strip()
    if not svg.startswith("<svg") and "<svg" not in svg:
        raise ConversionError("PlantUML did not produce a valid SVG document.")

    return svg


def extract_svg_dimensions(svg: str) -> tuple[str, str]:
    """Extract width and height from the rendered SVG."""
    try:
        root = ET.fromstring(svg)
    except ET.ParseError as exc:
        raise ConversionError("Generated SVG could not be parsed.") from exc

    width = _extract_numeric(root.attrib.get("width"))
    height = _extract_numeric(root.attrib.get("height"))

    if width and height:
        return width, height

    style = root.attrib.get("style", "")
    style_width = _extract_style_value(style, "width")
    style_height = _extract_style_value(style, "height")
    if style_width and style_height:
        return style_width, style_height

    view_box = root.attrib.get("viewBox", "")
    view_box_parts = view_box.split()
    if len(view_box_parts) == 4:
        return view_box_parts[2], view_box_parts[3]

    raise ConversionError("Could not determine SVG dimensions.")


def _extract_numeric(value: str | None) -> str | None:
    if not value:
        return None
    match = SVG_DIMENSION_RE.search(value)
    return match.group(1) if match else None


def _extract_style_value(style: str, key: str) -> str | None:
    for part in style.split(";"):
        if ":" not in part:
            continue
        name, value = part.split(":", 1)
        if name.strip() == key:
            return _extract_numeric(value)
    return None


def build_drawio_xml(
    plantuml_content: str,
    svg: str,
    width: str,
    height: str,
    modified_at: datetime | None = None,
) -> str:
    """Build a Draw.io XML document containing the PlantUML source and SVG."""
    timestamp = (modified_at or datetime.now(timezone.utc)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    diagram_id = f"diagram-{uuid4().hex[:12]}"
    user_object_id = f"userobject-{uuid4().hex[:12]}"
    etag_id = f"etag-{uuid4().hex[:12]}"

    xml_root = ET.Element(
        "mxfile",
        {
            "host": "app.diagrams.net",
            "modified": timestamp,
            "agent": "Mozilla/5.0",
            "etag": etag_id,
            "version": "24.7.17",
            "type": "embed",
        },
    )
    diagram_elem = ET.SubElement(xml_root, "diagram", {"id": diagram_id, "name": "Page-1"})
    mx_graph_model = ET.SubElement(
        diagram_elem,
        "mxGraphModel",
        {
            "dx": "1219",
            "dy": "1005",
            "grid": "1",
            "gridSize": "10",
            "guides": "1",
            "tooltips": "1",
            "connect": "1",
            "arrows": "1",
            "fold": "1",
            "page": "1",
            "pageScale": "1",
            "pageWidth": "850",
            "pageHeight": "1100",
            "math": "0",
            "shadow": "0",
        },
    )
    root_elem = ET.SubElement(mx_graph_model, "root")
    ET.SubElement(root_elem, "mxCell", {"id": "0"})
    ET.SubElement(root_elem, "mxCell", {"id": "1", "parent": "0"})

    plantuml_payload = json.dumps({"data": plantuml_content, "format": "svg"})
    user_object = ET.SubElement(
        root_elem,
        "UserObject",
        {
            "label": "",
            "plantUmlData": plantuml_payload,
            "id": user_object_id,
        },
    )
    svg_base64 = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    mx_cell = ET.SubElement(
        user_object,
        "mxCell",
        {
            "style": "shape=image;noLabel=1;verticalAlign=top;aspect=fixed;imageAspect=0;"
            f"image=data:image/svg+xml;base64,{svg_base64}",
            "parent": "1",
            "vertex": "1",
        },
    )
    ET.SubElement(
        mx_cell,
        "mxGeometry",
        {
            "x": "0",
            "y": "0",
            "width": width,
            "height": height,
            "as": "geometry",
        },
    )

    return ET.tostring(xml_root, encoding="unicode")


def convert_plantuml_to_drawio_xml(
    plantuml_content: str,
    modified_at: datetime | None = None,
) -> str:
    """Convert PlantUML text into Draw.io XML."""
    cleaned_content = plantuml_content.strip()
    if not cleaned_content:
        raise ConversionError("PlantUML content is empty")

    svg = render_svg(cleaned_content)
    width, height = extract_svg_dimensions(svg)
    return build_drawio_xml(cleaned_content, svg, width, height, modified_at=modified_at)