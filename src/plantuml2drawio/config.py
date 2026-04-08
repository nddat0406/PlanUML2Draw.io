#!/usr/bin/env python3
"""Configuration module for plantuml2drawio.

Contains configuration parameters and constants for the entire project.
"""

# Version information
VERSION = "1.2.0"
VERSION_DATE = "2025-03-16"

# File formats and extensions
DEFAULT_JSON_EXT = ".json"
DEFAULT_DRAWIO_EXT = ".drawio.xml"
FILE_EXTENSION_PUML = ".puml"
FILE_EXTENSION_DRAWIO = ".drawio.xml"

# Output formats
OUTPUT_FORMAT_JSON = "JSON"
OUTPUT_FORMAT_XML = "Draw.io XML"

# Application settings
DEFAULT_WINDOW_WIDTH = 800
DEFAULT_WINDOW_HEIGHT = 600
DEFAULT_WINDOW_TITLE = "PlantUML to Draw.io Converter"

# Resources
# Icon path without extension, will be added based on platform
ICON_PATH = "resources/icons/p2d_icon"

# Debug settings
DEBUG = False

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
