# ⚔️ 7DS Grand Cross OCR Cataloging Tool

A Windows desktop automation and OCR utility for **The Seven Deadly Sins: Grand Cross (PC)** that captures character screenshots through the Windows Snipping Tool, extracts character metadata using a fully local OCR pipeline, and automatically stores the results in a searchable SQLite catalog.

The application is designed to make character data collection faster while keeping gameplay uninterrupted through a non-activating Win32 HUD overlay.

---

## 📌 Overview

Manually recording character information from a game can be repetitive and time-consuming, especially when maintaining a large character collection.

This tool automates the process:

```text
Game Character Screen
        ↓
Windows Snipping Tool (Win + Shift + S)
        ↓
Clipboard Capture
        ↓
Local OCR Processing (RapidOCR + ONNX Runtime)
        ↓
Character Data Extraction
        ↓
Duplicate Detection
        ↓
SQLite Database (characters.db)
        ↓
Search / Filter / Export
```

The entire OCR pipeline runs locally without requiring an external OCR API or cloud service.

---

## ✨ Key Features

### 📸 Automated Screenshot Capture
- Monitors the Windows clipboard in the background.
- Works with screenshots captured using `Win + Shift + S`.
- Automatically detects new screenshots.
- Extracts character information without requiring manual data entry.
- Designed to avoid interfering with gameplay.

### 🔍 Local OCR Processing
Character information is extracted using:
- **RapidOCR**
- **ONNX Runtime**
- **Pillow**

The OCR pipeline runs completely locally. This provides:
- ✅ No external OCR API
- ✅ No API costs
- ✅ No network dependency for OCR
- ✅ Low-latency local processing
- ✅ Local processing of captured screenshots

### 🎮 Game-Safe HUD Overlay
The application displays capture results using a custom borderless Windows overlay.

The overlay uses the Win32 `WS_EX_NOACTIVATE` window style to prevent the notification window from stealing keyboard/mouse focus from the game.

This allows capture confirmations to appear over the game while minimizing disruption to gameplay.

### 🛡️ Duplicate Protection
Character profiles are checked against existing records before being inserted into the database. If a character already exists, the application prevents unnecessary duplicate entries and informs the user.

### 📚 Character Manager
The application includes a searchable character catalog with:
- Character title & prefix
- Character name
- Attribute (with color identifiers)
- Race
- Combat class / stat information
- Real-time search functionality
- Attribute filtering (Darkness, Light, Strength, HP, Speed)
- Race filtering
- Manual entry & editing
- Multi-select row deletion

### 📤 Data Export
Character data can be exported in multiple formats:
- **CSV**
- **TXT**
- **JSON**
- **Excel / Google Sheets-compatible tabular format (TSV)**

The application also supports one-click copying of character data to the clipboard.

---

## 🛠️ Technology Stack

| Area | Technology |
|---|---|
| **Language** | Python 3.10+ |
| **GUI Framework** | PySide6 (Qt for Python) |
| **OCR Engine** | RapidOCR |
| **OCR Runtime** | ONNX Runtime |
| **Image Processing** | Pillow |
| **Windows Integration** | Win32 API via `ctypes` (`WS_EX_NOACTIVATE`) |
| **Background Processing** | PySide6 `QThread` |
| **Database** | SQLite3 |
| **Export Formats** | CSV / JSON / TXT / TSV |
| **Testing** | Automated benchmark & unit tests |

---

## 🧠 Engineering Highlights

### Local OCR Pipeline
Instead of sending screenshots to an external OCR service, the application performs OCR locally using RapidOCR with ONNX Runtime.

This removes the need for:
- API keys
- External network requests
- Cloud OCR services
- Per-request API costs

The OCR output is then processed to identify the relevant character fields.

### Background Processing
Screenshot monitoring and OCR processing are performed outside the main GUI thread.

PySide6 `QThread` is used for background processing so that OCR operations do not block the application's interface.

```text
Main GUI Thread
       │
       ├── User Interface (PySide6)
       │
       └── Background Worker (QThread)
                │
                ├── Clipboard Monitoring
                ├── Image Processing (Pillow)
                ├── OCR (RapidOCR)
                └── Database Operations (SQLite3)
```

This keeps the application responsive while screenshots are being processed.

### Win32 Non-Activating Overlay
One of the main technical challenges was displaying capture notifications over a game without causing the game to lose focus.

The application uses the Windows API through Python's `ctypes` interface and applies `WS_EX_NOACTIVATE` to the overlay window. This allows the overlay to remain visible without activating the window or unnecessarily interrupting the game.

---

## 🗄️ Data Storage

Character information is stored locally using SQLite3 (`characters.db`).

The database provides:
- Persistent character records
- Duplicate detection
- Searchable data
- Filtering
- Editing
- Deletion
- Export functionality

No external database server is required.

---

## 🧪 Testing & Benchmark

The OCR extraction pipeline was tested using an automated synthetic benchmark representing different character layouts and attribute configurations.

### Benchmark Result: **24 / 24 test cases passed (100% accuracy)**

The benchmark verifies extraction of character metadata across all attributes (Darkness, Light, Strength, HP, Speed), all races (Demon, Goddess, Human, Fairy, Giant, Unknown), collaboration units, and edge-case name structures.

> *Note: The reported accuracy applies specifically to the synthetic benchmark and should not be interpreted as a guarantee of 100% accuracy for all possible in-game screenshots.*

---

## 🚀 Quick Start

### Requirements
- Windows 10 or Windows 11
- Python 3.10 or newer
- The Seven Deadly Sins: Grand Cross PC version
- Windows Snipping Tool (`Win + Shift + S`)

### 1. Clone the Repository
```bash
git clone https://github.com/ninad1234567/7ds-grand-cross-ocr-tool.git
cd 7ds-grand-cross-ocr-tool
```

### 2. Create a Virtual Environment
```bash
python -m venv .venv
```

Activate it using:

- **Windows CMD**:
  ```cmd
  .venv\Scripts\activate
  ```
- **Windows PowerShell**:
  ```powershell
  .venv\Scripts\Activate.ps1
  ```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```
*Or directly:*
```bash
pip install PySide6 Pillow rapidocr-onnxruntime
```

---

## ▶️ Running the Application

Launch the application using:
```bash
python main.py
```

If using the provided launch scripts, you can also double-click:
- **`run.bat`** (Standard launcher)
- **`start_silent.vbs`** (Silent background launcher without terminal window)

---

## 🎮 Usage

1. **Start the application**: Launch the OCR cataloging tool.
2. **Start monitoring**: Click **"Start Monitoring"**.
3. **Open a character screen**: Launch the PC version of *The Seven Deadly Sins: Grand Cross* and navigate to the character profile you want to catalog.
4. **Capture the character**: Press **`Win + Shift + S`** and snip the character profile area.
5. **Automatic processing**: The application detects the new screenshot from the Windows clipboard and sends it through the local OCR pipeline.
6. **Character information extracted**: Character title, name, attribute, race, and stats are extracted and checked for duplicates.
7. **Capture confirmation**: A non-activating HUD notification displays the capture result without taking focus away from the game.
8. **Character catalog**: The extracted character is stored in the local SQLite database and becomes immediately available in the character manager.

---

## 📊 Example Workflow

```text
┌─────────────────────────┐
│  Character Profile      │
│  in 7DS Grand Cross     │
└────────────┬────────────┘
             │
             │ Win + Shift + S
             ▼
┌─────────────────────────┐
│ Windows Snipping Tool   │
└────────────┬────────────┘
             │
             │ Clipboard
             ▼
┌─────────────────────────┐
│ Background Monitor      │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ RapidOCR + ONNX Runtime │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ Data Extraction         │
│ Title / Name / Attribute│
│ Race / Combat Stats     │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ Duplicate Detection     │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ SQLite Character        │
│ Database (characters.db)│
└─────────────────────────┘
```

---

## 📁 Project Structure

```text
7ds-grand-cross-ocr-tool/
│
├── main.py                  # Application entry point
├── main_window.py           # PySide6 GUI interface & Character Manager
├── ocr_parser.py            # Local RapidOCR & 7DS Entity Extraction Engine
├── clipboard_monitor.py     # Background QThread clipboard watcher
├── toast_overlay.py         # Win32 non-activating HUD overlay popup
├── database.py              # SQLite3 storage & duplicate prevention
│
├── test_app.py              # Unit tests for OCR & CRUD operations
├── test_roster_benchmark.py # 24-character comprehensive benchmark suite
│
├── requirements.txt         # Python package dependencies
├── run.bat                  # 1-Click launcher script
├── start_silent.vbs         # Silent launcher (no console window)
├── .gitignore               # Git ignore rules
└── README.md                # Project documentation
```

---

## 🔐 Privacy

The application is designed around local processing. Character screenshots are processed locally using the installed OCR engine.

The application does not require:
- Cloud OCR APIs
- External databases
- User accounts
- API keys
- Remote character-data services

Character information is stored locally in SQLite.

---

## ⚡ Why I Built This

The goal of the project was to eliminate repetitive manual data entry when cataloging a large collection of game characters.

Instead of manually reading information from each character screen and typing it into a spreadsheet, the workflow becomes:

**Capture → OCR → Extract → Store**

The project also provided an opportunity to explore several areas of software engineering that are different from typical web applications:
- Desktop GUI development
- Computer vision and OCR
- Windows API integration
- Background threads
- Clipboard monitoring
- Local databases
- Data export
- Automated testing
- Non-intrusive UI overlays

---

## 🔮 Future Improvements

- Improved OCR handling for additional character card sub-menus
- More robust extraction validation
- Additional export formats
- Configurable capture regions
- Automatic character thumbnail image storage
- Improved benchmark coverage
- Additional Windows accessibility options
- Packaging the application as a standalone Windows executable (`.exe` via PyInstaller)

---

## ⚠️ Disclaimer

This project is an independent fan-made utility for personal productivity and data organization.

*The Seven Deadly Sins: Grand Cross* and its associated characters, artwork, trademarks, and other intellectual property belong to their respective owners.

This project is not affiliated with, endorsed by, or sponsored by the game's developers or publishers. No proprietary game files or game assets are included with this project.

---

## 📄 License

No open-source license is currently provided. Unless a license is added to this repository, the source code remains under the default copyright protections of its author.

---

## 👤 Author

**Ninad Kangandul**  
*Built as an independent Windows desktop automation and OCR project.*
