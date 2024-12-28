@echo off
echo Building Markdown Editor...

REM Activate the markdown_editor conda environment
call conda activate markdown_editor

REM Build the executable
pyinstaller --noconfirm ^
    --clean ^
    --windowed ^
    --onefile ^
    --name "MarkdownEditor" ^
    --add-data "projects.json;." ^
    --hidden-import PyQt5.QtWebEngineWidgets ^
    --hidden-import PyQt5.QtWebEngine ^
    --hidden-import PyQt5.QtWebChannel ^
    markdown_editor.py

echo Build complete!
pause
