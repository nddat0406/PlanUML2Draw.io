"""Core functionality for PlantUML to Draw.io conversion."""

import argparse
import json
import os
import sys
from typing import Optional, Tuple

from plantuml2drawio.config import (DEFAULT_DRAWIO_EXT, DEFAULT_JSON_EXT,
                                    FILE_EXTENSION_PUML, OUTPUT_FORMAT_JSON,
                                    OUTPUT_FORMAT_XML)
from plantuml2drawio.drawio_embed_converter import (ConversionError,
                                                    convert_plantuml_to_drawio_xml)


def process_diagram(
    plantuml_content: str, output_json: bool = False
) -> Tuple[Optional[str], Optional[str]]:
    """Process PlantUML content and generate XML or JSON representation.

    Args:
        plantuml_content: Content of the PlantUML diagram
        output_json: If True, output JSON, otherwise XML

    Returns:
        On success: Tuple of (String with XML or JSON, output format description)
        On failure: (None, None)
    """
    if not plantuml_content:
        print("Error: Empty PlantUML content")
        return None, None

    try:
        drawio_xml = convert_plantuml_to_drawio_xml(plantuml_content)

        if output_json:
            output_content = json.dumps(
                {
                    "engine": "rglaue/plantuml_to_drawio-compatible",
                    "outputFormat": OUTPUT_FORMAT_XML,
                    "drawioXml": drawio_xml,
                },
                indent=2,
            )
            return output_content, OUTPUT_FORMAT_JSON

        return drawio_xml, OUTPUT_FORMAT_XML

    except ConversionError as e:
        print(f"Error: {e}")
        return None, None

    except Exception as e:
        print(f"Unexpected error during processing: {e}")
        return None, None


def read_plantuml_file(file_path: str) -> Optional[str]:
    """Read a PlantUML file and return its content.

    Args:
        file_path: Path to the file to read

    Returns:
        Content of the file as string or None on error
    """
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist")
        return None

    if not file_path.lower().endswith(FILE_EXTENSION_PUML):
        print(f"Warning: File '{file_path}' does not have the .puml extension")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            if not content.strip():
                print(f"Error: File '{file_path}' is empty")
                return None
            return content
    except IOError as e:
        print(f"Error reading input file '{file_path}': {e}")
        return None
    except UnicodeDecodeError as e:
        print(f"Error: File '{file_path}' is not a valid UTF-8 encoded text file: {e}")
        return None


def write_output_file(content: str, file_path: str) -> bool:
    """Write the given content to a file.

    Args:
        content: Content to write
        file_path: Path to the output file

    Returns:
        True on success, False on error
    """
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except IOError as e:
        print(f"Error writing output file '{file_path}': {e}")
        return False


def get_output_file_path(
    input_file: str, output_file: Optional[str], is_json: bool
) -> str:
    """Determine output file path based on input file and output format.

    Args:
        input_file: Path to the input file
        output_file: Optional path to the output file
        is_json: True if JSON format, False if Draw.io XML format

    Returns:
        Path to the output file
    """
    if output_file:
        return output_file

    base, _ = os.path.splitext(input_file)
    extension = DEFAULT_JSON_EXT if is_json else DEFAULT_DRAWIO_EXT
    return base + extension


def handle_info_request(content: str) -> None:
    """Display information about the current input and conversion engine."""
    is_plantuml = "@startuml" in content and "@enduml" in content
    print(f"PlantUML markers detected: {'yes' if is_plantuml else 'no'}")
    print("Converter engine: rglaue/plantuml_to_drawio-compatible SVG embed pipeline")


def main() -> None:
    """Main function of the program.

    Parses command line arguments, reads PlantUML file,
    determines diagram type, processes the diagram and
    writes output to a file.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description=(
            "Converts a PlantUML diagram to a draw.io XML file "
            "or a JSON representation of nodes and edges."
        )
    )
    parser.add_argument("--input", required=True, help="Input PlantUML file")
    parser.add_argument("--output", help="Output file (draw.io XML or JSON)")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output nodes and edges as JSON instead of XML.",
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Only display information about the diagram type.",
    )
    args = parser.parse_args()

    # Read input file
    plantuml_content = read_plantuml_file(args.input)
    if plantuml_content is None:
        sys.exit(1)

    # Only show information if requested
    if args.info:
        handle_info_request(plantuml_content)
        sys.exit(0)

    # Determine output file
    output_file = get_output_file_path(args.input, args.output, args.json)

    # Process diagram
    output_content, output_format = process_diagram(plantuml_content, args.json)
    if output_content is None:
        sys.exit(1)

    # Write content to file
    if write_output_file(output_content, output_file):
        print(f"{output_format} file successfully created: {output_file}")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
