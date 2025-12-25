# Installation Guide

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## Quick Installation

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd simple-web-browser-master
   ```

2. **Install required packages**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

## Manual Installation

If you prefer to install packages manually:

```bash
# Core GUI framework
pip install PyQt5

# PDF viewer support
pip install PyMuPDF
```

## Platform-Specific Notes

### Windows
- Use `py` instead of `python` if you have multiple Python versions:
  ```cmd
  py -m pip install -r requirements.txt
  py main.py
  ```

### macOS
- You might need to install additional dependencies for PyQt5:
  ```bash
  brew install python-tk
  pip install -r requirements.txt
  ```

### Linux (Ubuntu/Debian)
- Install system dependencies first:
  ```bash
  sudo apt-get update
  sudo apt-get install python3-pyqt5 python3-pyqt5.qtwebengine
  pip install -r requirements.txt
  ```

## Troubleshooting

### PyQt5 Installation Issues
If PyQt5 installation fails, try:
```bash
pip install --upgrade pip
pip install PyQt5 --no-cache-dir
```

### PyMuPDF Installation Issues
If PyMuPDF installation fails, try:
```bash
pip install --upgrade pip setuptools wheel
pip install PyMuPDF --no-cache-dir
```

### Missing WebEngine
If you get WebEngine errors, install the complete PyQt5 package:
```bash
pip install PyQt5[complete]
```

## Features Requiring Additional Setup

### PDF Reader Mode
- **Required**: PyMuPDF library
- **Installation**: `pip install PyMuPDF`
- **Note**: PDF reader will show installation instructions if PyMuPDF is missing

### Command Line Mode
- **Required**: System terminal/command prompt access
- **Note**: Uses system's built-in terminal capabilities

### API Tester Mode
- **Required**: No additional packages (uses system curl)
- **Note**: Requires curl to be installed on your system

## Verification

To verify your installation:

1. **Check Python version**:
   ```bash
   python --version
   ```

2. **Check PyQt5 installation**:
   ```python
   python -c "from PyQt5.QtWidgets import QApplication; print('PyQt5 OK')"
   ```

3. **Check PyMuPDF installation**:
   ```python
   python -c "import fitz; print('PyMuPDF OK')"
   ```

4. **Run the application**:
   ```bash
   python main.py
   ```

## Development Setup

For development, you might want additional tools:

```bash
# Code formatting
pip install black

# Code linting
pip install flake8

# Testing framework
pip install pytest
```

## Virtual Environment (Recommended)

To avoid conflicts with other Python projects:

```bash
# Create virtual environment
python -m venv browser_env

# Activate virtual environment
# Windows:
browser_env\Scripts\activate
# macOS/Linux:
source browser_env/bin/activate

# Install requirements
pip install -r requirements.txt

# Run application
python main.py
```