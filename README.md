# Lightweight Markdown Preview Editor

## Download
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/merlinsaw/msaw-makdown-editor)](https://github.com/merlinsaw/msaw-makdown-editor/releases/latest)

🔽 [Download Latest Release](https://github.com/merlinsaw/msaw-makdown-editor/releases/latest)

## Features
- Real-time Markdown preview with live updates
- Modern dark theme with customizable UI
- Split-view editing mode
- Code block support with syntax highlighting
- File browser with project management
- Auto-save functionality
- Find and replace functionality
- Keyboard shortcuts for all operations
- Copy paragraph functionality

## Setup Options

### Option 1: Download Pre-built Executable
1. Go to the [Releases page](https://github.com/merlinsaw/msaw-makdown-editor/releases)
2. Download the latest `MarkdownEditor.exe`
3. Run the executable - no installation required

### Option 2: Build from Source
1. Install Python 3.8 or higher
2. Clone this repository:
   ```bash
   git clone https://github.com/merlinsaw/msaw-makdown-editor.git
   cd msaw-makdown-editor
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Build the executable (Windows):
   ```bash
   build.bat
   ```
   The executable will be created in the `dist` directory.

### Option 3: Run from Source
1. Follow steps 1-3 from Option 2
2. Run the application:
   ```bash
   python markdown_editor.py
   ```

## Usage
- Type Markdown in the left panel
- See live preview in the right panel
- Use `E` key to toggle edit mode
- Use `Esc` to return to preview mode
- `Ctrl+S` to save, `Ctrl+O` to open files
- Click on any paragraph to copy its content

## System Requirements
- Windows 10 or later
- 100MB free disk space
- 4GB RAM recommended
