# PlantUML to Draw.io Converter

A tool for converting PlantUML diagrams to Draw.io format.

*[Deutsche Version weiter unten](#deutsche-version)*

<p align="center">
  <img src="https://via.placeholder.com/700x200?text=PlantUML+to+Draw.io+Converter" alt="PlantUML to Draw.io Converter Logo"/>
</p>

## 📋 Overview

This project enables the conversion of PlantUML diagrams to Draw.io format, allowing for seamless integration of UML diagrams into various documentation and presentation workflows. The web interface now uses a PlantUML-to-SVG-to-Draw.io pipeline compatible with the approach from `rglaue/plantuml_to_drawio`, which means it can handle any diagram type that PlantUML itself can render.

## ✨ Key Features

- 🔄 Conversion of PlantUML diagrams to Draw.io XML by embedding rendered SVG
- 🧬 Preserves the original PlantUML source inside the Draw.io document
- 📚 Supports class, sequence, activity, and other PlantUML-renderable diagrams
- 🖥️ User-friendly GUI and command-line interface
- 📦 Single-file and batch file conversion in the web interface

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/doubleSlashde/plantuml2drawio.git
cd plantuml2drawio

# Recommended: Use Python 3.11 for best compatibility
# Create and activate a virtual environment (optional but recommended)
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e .
```

### Usage

#### Command Line

```bash
# Using the entry point scripts
./p2d-cli --input examples/activity_examples/simple_activity.puml --output output.drawio

# Or using Python modules
python -m src.plantuml2drawio.core --input examples/activity_examples/simple_activity.puml --output output.drawio
```

#### Graphical User Interface

```bash
# Using the entry point scripts
./p2d-gui

# Or using Python modules
python -m src.plantuml2drawio.app
```

#### Giao Diện Web

Repository hiện có giao diện web để chuyển đổi sơ đồ PlantUML sang định dạng
XML có thể import vào Draw.io.

Chạy web app trên máy local:

```bash
# Windows (PowerShell)
py -3.9 -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-web.txt
pip install -e .
python web_app.py
```

Yêu cầu môi trường:

- Cần cài Java và có trong `PATH`
- Ở lần chạy đầu, app tự tải `plantuml-1.2024.4.jar` vào thư mục `tools/`
- Có thể override đường dẫn jar bằng biến môi trường `PLANTUML_JAR_PATH`

Sau đó mở:

```text
http://127.0.0.1:5000
```

Cách sử dụng:

- Dán nội dung PlantUML vào khung bên trái
- Chọn định dạng output (`Draw.io XML` hoặc `JSON`)
- Nhấn `Convert` (hoặc `Ctrl+Enter`)
- Sao chép kết quả hoặc tải file `.drawio.xml`
- Trong Draw.io: `File -> Import From -> Device` rồi chọn file vừa tải

Upload hàng loạt:

- Nhấn `Choose .puml files` và chọn nhiều file `.puml`, `.plantuml`, hoặc `.txt`
- Nhấn `Batch Convert`
- App sẽ tải về `converted-diagrams.zip`
- File ZIP chứa các file output tương ứng và `conversion-report.json`

Lưu ý:

- Output Draw.io được tạo bằng cách embed SVG render từ PlantUML (không dựng lại từng shape native)
- Output JSON là dạng wrapper chứa Draw.io XML để tiện inspect/debug
- Quá trình convert cần Java và PlantUML jar ở runtime

### Triển Khai Web Interface

Để chạy theo kiểu production, dùng Flask phía sau Waitress:

```bash
# Windows (PowerShell)
.\venv\Scripts\activate
pip install -r requirements-web.txt
waitress-serve --host 0.0.0.0 --port 8080 web_app:app
```

Sau đó truy cập app tại:

```text
http://localhost:8080
```

Khuyến nghị môi trường:

- Nên đặt service sau reverse proxy (Nginx/Caddy/IIS) để bật TLS/HTTPS
- Giới hạn kích thước request và rate limit ở lớp proxy
- Giữ `debug=False` cho môi trường không phải development
- Đảm bảo Java có sẵn trong môi trường deploy hoặc cấu hình `JAVA_BIN`
- Dùng `PLANTUML_JAR_PATH` nếu muốn tự cung cấp PlantUML jar thay vì auto-download

#### Triển Khai Lên Render

Repository đã có sẵn cấu hình Render chạy bằng Docker vì tính năng convert yêu cầu cả Python và Java ở runtime.

Các file sử dụng:

- `Dockerfile`
- `render.yaml`

Bước triển khai:

1. Push repository lên GitHub
2. Trên Render, tạo deployment mới kiểu `Blueprint` từ repository
3. Render sẽ tự nhận diện `render.yaml` và build service bằng Docker
4. Sau khi deploy xong, mở URL public do Render cung cấp

Bên trong container:

- Cài dependencies Python
- Cài Java runtime dạng headless
- Khởi chạy app bằng Waitress trên cổng do Render cấp

Lưu ý:

- PlantUML jar sẽ được tải tự động ở request convert đầu tiên nếu chưa cấu hình `PLANTUML_JAR_PATH`
- Nếu muốn đóng gói jar sẵn trong image, thêm file jar vào `tools/` và copy trong `Dockerfile`

## 📦 Project Structure

The project has been reorganized for better maintainability and extensibility:

```
plantuml2drawio/
├── README.md                    # This file
├── LICENSE                      # License information
├── requirements.txt             # Python dependencies
├── setup.py                     # Setup script for installation
├── p2d-cli                      # Command-line entry point
├── p2d-gui                      # GUI entry point
├── src/                         # Main source code
│   ├── plantuml2drawio/         # Core package
│   │   ├── core.py              # Core functionality
│   │   ├── app.py               # GUI application
│   │   ├── config.py            # Configuration settings
│   │   └── drawio_embed_converter.py # SVG embed converter for Draw.io XML
├── web_app.py                   # Flask web server
├── templates/                   # HTML templates for web UI
├── static/                      # CSS and JavaScript for web UI
├── tests/                       # Tests
├── docs/                        # Documentation
├── examples/                    # Example diagrams
└── resources/                   # Resources like icons
```

## 📚 Documentation

Detailed documentation is available in the `docs` directory:

- [Installation and Usage](docs/Installation_und_Benutzung.md)
- [Workflow](docs/Arbeitsablauf.md)
- [System Architecture](docs/Systemarchitektur.md)
- [Extension Possibilities](docs/Erweiterungen.md)

## 🧪 Examples

The project contains examples in the `examples` directory:

### Activity Diagram

**PlantUML Input**:
```plantuml
@startuml
start
:Step 1;
if (Condition?) then (yes)
  :Step 2a;
else (no)
  :Step 2b;
endif
:Step 3;
stop
@enduml
```

**Draw.io Output**:

<p align="center">
  <img src="https://via.placeholder.com/500x300?text=Draw.io+Activity+Diagram" alt="Draw.io Activity Diagram Example"/>
</p>

## 🛠️ Technology Stack

- Python 3.11 (recommended) or 3.6+
- Java runtime for PlantUML SVG rendering
- PlantUML jar for diagram rendering
- customtkinter for GUI
- XML libraries for Draw.io generation

## 📦 Executables

The project provides pre-built executables for both Windows and macOS through GitHub Actions. These executables are automatically built when:
- A new version tag is pushed (e.g., `v1.0.0`)
- The workflow is manually triggered via GitHub Actions UI

### Download Executables

1. Go to the [Releases](https://github.com/doubleSlashde/plantuml2drawio/releases) page to download the latest release
2. Or download the latest build artifacts from the [Actions](https://github.com/doubleSlashde/plantuml2drawio/actions) page:
   - `p2d-windows` - Windows executable with all dependencies
   - `p2d-macos` - macOS application bundle (.app)

### Building Executables Locally

You can build the executables locally using PyInstaller. You only need the runtime dependencies and PyInstaller:

```bash
# Install build requirements (includes runtime dependencies)
pip install -r requirements-build.txt

# Build executable (recommended with Python 3.11)
python -m PyInstaller --clean p2d.spec
```

The built executables will be available in the `dist` directory:
- Windows: `dist/p2d/p2d.exe` (with dependencies)
- macOS: `dist/p2d.app` (application bundle)

Note: The final executable will include all necessary runtime dependencies, so end users don't need to install Python or any requirements.

## 🗺️ Roadmap

- [x] Support for activity diagrams
- [ ] Support for usecase diagrams
- [ ] Support for sequence diagrams
- [ ] Support for class diagrams
- [ ] Support for component diagrams
- [ ] Advanced layout management
- [ ] Integration with PlantUML server
- [x] Web interface

## 🤝 Contributing

Contributions are welcome! Check out the [Extension Possibilities](docs/Erweiterungen.md) to learn more about possible contributions.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

- [PlantUML](https://plantuml.com/) for the excellent UML diagram syntax
- [Draw.io](https://www.draw.io/) for the open XML format and diagram editing functionality

---

<p align="center">
  Created with ❤️ for UML enthusiasts and software developers
</p>

---

<a name="deutsche-version"></a>
# Deutsche Version

## 📋 Übersicht

Dieses Projekt ermöglicht die Konvertierung von PlantUML-Diagrammen in das Draw.io-Format, wodurch eine nahtlose Integration von UML-Diagrammen in verschiedene Dokumentations- und Präsentationsworkflows ermöglicht wird. Der Konverter unterstützt derzeit Aktivitätsdiagramme und wird kontinuierlich um weitere Diagrammtypen erweitert.

## ✨ Hauptmerkmale

- 🔄 Konvertierung von PlantUML-Aktivitätsdiagrammen in das Draw.io-Format
- 🔍 Automatische Erkennung des PlantUML-Diagrammtyps
- 🖥️ Benutzerfreundliche GUI sowie Kommandozeilenschnittstelle
- 📐 Automatische Layout-Berechnung für optimale Diagrammdarstellung
- 🧩 Modularer Aufbau für einfache Erweiterbarkeit

## 🚀 Schnellstart

### Installation

```bash
# Repository klonen
git clone https://github.com/doubleSlashde/plantuml2drawio.git
cd plantuml2drawio

# Empfohlen: Python 3.11 für beste Kompatibilität verwenden
# Virtuelle Umgebung erstellen und aktivieren (optional, aber empfohlen)
python3.11 -m venv venv
source venv/bin/activate  # Unter Windows: venv\Scripts\activate

# Abhängigkeiten installieren
pip install -r requirements.txt

# Oder im Entwicklungsmodus installieren
pip install -e .
```

### Verwendung

#### Kommandozeile

```bash
# Über die Einstiegsskripte
./p2d-cli --input examples/activity_examples/simple_activity.puml --output output.drawio

# Oder über Python-Module
python -m src.plantuml2drawio.core --input examples/activity_examples/simple_activity.puml --output output.drawio
```

#### Grafische Benutzeroberfläche

```bash
# Über die Einstiegsskripte
./p2d-gui

# Oder über Python-Module
python -m src.plantuml2drawio.app
```
