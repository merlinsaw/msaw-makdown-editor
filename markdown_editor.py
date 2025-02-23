import sys
import os
import json
import pyperclip
from enum import Enum
from typing import List, Dict, Optional, Any, Union
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QFileSystemModel,
    QSplitter, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QTreeView, QStyle, QFileDialog, QMessageBox,
    QInputDialog, QMenu, QAction, QToolButton, QLineEdit, 
    QShortcut, QStatusBar
)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PyQt5.QtCore import (
    Qt, QDir, pyqtSlot, QTimer, QModelIndex,
    QAbstractItemModel, QVariant, QObject
)
from PyQt5.QtGui import QFont, QPalette, QColor, QKeySequence
from PyQt5.QtWebChannel import QWebChannel
import markdown2
import re

class ColorTheme(Enum):
    # Backgrounds
    WINDOW_BG = '#2B2B2B'          # Main window background
    EDITOR_BG = '#1E1E1E'          # Editor and panels background
    
    # Text Colors
    TEXT_PRIMARY = '#FFFFFF'        # Primary text color
    TEXT_SECONDARY = '##000000'      # Secondary text color
    
    # Button Colors
    BUTTON_BG = '#FFFFFF'          # Button background
    BUTTON_TEXT = '#663399'        # Button text color
    BUTTON_BORDER = '#FFD700'      # Button border
    BUTTON_HOVER_BG = '#faebd7'    # Button hover background
    BUTTON_HOVER_TEXT = '#B8860B'  # Button hover text
    
    # Accent Colors
    ACCENT_PRIMARY = '#663399'     # Primary accent (purple)
    ACCENT_SECONDARY = '#FFD700'   # Secondary accent (gold)
    ACCENT_TERTIARY = '#B8860B'    # Tertiary accent (dark gold)
    ACCENT_HIGHLIGHT = '#eb93eb'   # Highlight accent (light purple)
    
    # Interactive Elements
    HOVER_BG = '#3D3D3D'          # Generic hover background
    FOCUS_BORDER = '#eb93eb'      # Focus state border
    SELECTION_BG = '#663399'      # Selected item background
    
    # Scrollbar
    SCROLLBAR_BG = '#1E1E1E'      # Scrollbar background
    SCROLLBAR_HANDLE = '#FFFFFF'   # Scrollbar handle
    SCROLLBAR_BORDER = '#B8860B'   # Scrollbar border
    
    # Menu and Toolbar
    MENU_BG = '#1E1E1E'           # Menu background
    MENU_TEXT = '#FFFFFF'         # Menu text
    MENU_BORDER = '#B8860B'       # Menu border
    MENU_ITEM_SELECTED = '#663399' # Selected menu item

    def __str__(self):
        return self.value

    def __format__(self, format_spec):
        return self.value

class CopyHandler(QObject):
    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
    
    @pyqtSlot(str)
    def copy_to_clipboard(self, text: str) -> None:
        pyperclip.copy(text)

class KeyBindings(Enum):
    # Editor Mode Controls
    TOGGLE_EDIT_MODE = 'E'
    EXIT_EDIT_MODE = 'Esc'
    
    # File Operations
    SAVE_FILE = 'Ctrl+S'
    NEW_FILE = 'Ctrl+N'
    OPEN_FILE = 'Ctrl+O'
    
    # Edit Operations
    UNDO = 'Ctrl+Z'
    REDO = 'Ctrl+Y'
    CUT = 'Ctrl+X'
    COPY = 'Ctrl+C'
    PASTE = 'Ctrl+V'
    
    # Navigation
    FIND = 'Ctrl+F'
    REPLACE = 'Ctrl+H'
    
    # View Controls
    TOGGLE_PREVIEW = 'Q'
    TOGGLE_FILE_BROWSER = 'Ctrl+B'

class FontStyle(Enum):
    # Editor fonts
    EDITOR_MAIN = {
        'family': 'Consolas',
        'size': 12,
        'weight': 75,  # Bold
        'italic': False
    }
    
    EDITOR_HEADING1 = {
        'family': 'Consolas',
        'size': 20,
        'weight': 75,  # Bold
        'italic': False
    }
    
    EDITOR_HEADING2 = {
        'family': 'Consolas',
        'size': 16,
        'weight': 75,  # Bold
        'italic': False
    }
    
    # UI Element fonts
    BUTTON_TEXT = {
        'family': 'Segoe UI',
        'size': 10,
        'weight': 63,  # DemiBold
        'italic': False
    }
    
    MENU_TEXT = {
        'family': 'Segoe UI',
        'size': 10,
        'weight': 50,  # Normal
        'italic': False
    }
    
    STATUS_BAR = {
        'family': 'Segoe UI',
        'size': 9,
        'weight': 50,  # Normal
        'italic': False
    }
    
    FILE_BROWSER = {
        'family': 'Segoe UI',
        'size': 10,
        'weight': 50,  # Normal
        'italic': False
    }
    
    TITLE_BAR = {
        'family': 'Segoe UI',
        'size': 11,
        'weight': 63,  # DemiBold
        'italic': False
    }
    
    # Preview fonts
    PREVIEW_BODY = {
        'family': 'Segoe UI',
        'size': 12,
        'weight': 50,  # Normal
        'italic': False
    }
    
    PREVIEW_CODE = {
        'family': 'Consolas',
        'size': 12,
        'weight': 50,  # Normal
        'italic': False
    }
    
    PREVIEW_QUOTE = {
        'family': 'Segoe UI',
        'size': 12,
        'weight': 50,  # Normal
        'italic': True
    }

    def create_font(self):
        """Create a QFont object from the style configuration"""
        font = QFont(self.value['family'], self.value['size'])
        font.setWeight(self.value['weight'])
        font.setItalic(self.value['italic'])
        return font

class MultiProjectModel(QAbstractItemModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.root_paths: List[str] = []
        self.root_names: Dict[str, str] = {}
        self.file_model = QFileSystemModel()
        self.file_model.setFilter(QDir.AllEntries | QDir.NoDotAndDotDot)
        self.file_model.setNameFilters(['*.md', '*.markdown', '*.prompt'])
        self.file_model.setNameFilterDisables(False)
        
    def index(self, row: int, column: int, parent: QModelIndex = QModelIndex()) -> QModelIndex:
        """Improved index handling for better file display"""
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():  # Root level
            if 0 <= row < len(self.root_paths):
                return self.createIndex(row, column, self.root_paths[row])
            return QModelIndex()

        parent_path = str(parent.internalPointer() or '')
        if not parent_path:
            return QModelIndex()

        # Get the file system model's index for the parent path
        parent_model_index = self.file_model.index(parent_path)
        if not parent_model_index.isValid():
            return QModelIndex()

        # Get the child from the file system model
        child_index = self.file_model.index(row, 0, parent_model_index)
        if not child_index.isValid():
            return QModelIndex()

        # Get the full path of the child
        child_path = self.file_model.filePath(child_index)
        return self.createIndex(row, column, child_path)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Improved row count handling"""
        if not parent.isValid():
            return len(self.root_paths)

        path = str(parent.internalPointer() or '')
        if not path:
            return 0

        # Get count from file system model
        model_index = self.file_model.index(path)
        if model_index.isValid():
            return self.file_model.rowCount(model_index)
        return 0

    def parent(self, index: QModelIndex) -> QModelIndex:
        """Improved parent handling"""
        if not index.isValid():
            return QModelIndex()

        path = str(index.internalPointer() or '')
        if not path or path in self.root_paths:
            return QModelIndex()

        parent_path = os.path.dirname(path)
        if parent_path in self.root_paths:
            row = self.root_paths.index(parent_path)
            return self.createIndex(row, 0, parent_path)

        # Get parent from file system model
        parent_model_index = self.file_model.index(parent_path)
        if parent_model_index.isValid():
            return self.createIndex(parent_model_index.row(), 0, parent_path)

        return QModelIndex()

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> QVariant:
        if not index.isValid():
            return QVariant()
        
        path = str(index.internalPointer() or '')
        if not path:
            return QVariant()
        
        if role == Qt.DisplayRole:
            if path in self.root_paths:
                return self.root_names.get(path, os.path.basename(path))
            return os.path.basename(path)
        
        return QVariant()

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 1

    def normalize_path(self, path: str) -> str:
        """Normalize path to handle special characters and brackets"""
        if not path:
            return ""
        return os.path.normpath(os.path.abspath(path))

    def load_projects(self, projects: List[Dict[str, str]]) -> None:
        """Load projects with improved path handling"""
        self.beginResetModel()
        self.root_paths = []
        self.root_names = {}
        
        for project in projects:
            try:
                path = self.normalize_path(project['path'])
                if os.path.exists(path):
                    self.root_paths.append(path)
                    self.root_names[path] = project['name']
                    # Set root path in file model
                    self.file_model.setRootPath(path)
            except Exception as e:
                print(f"Error loading project {project['name']}: {str(e)}")
        
        self.endResetModel()

    def filePath(self, index: QModelIndex) -> str:
        """Get file path from index"""
        if not index.isValid():
            return ""
        return str(index.internalPointer() or "")

    def setRootPath(self, path: str) -> QModelIndex:
        """Set root path and return its index"""
        path = self.normalize_path(path)
        if path not in self.root_paths:
            self.beginResetModel()
            self.root_paths = [path]
            self.root_names = {path: os.path.basename(path)}
            self.file_model.setRootPath(path)
            self.endResetModel()
        return self.createIndex(0, 0, path)

class MarkdownEditor(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.current_file: Optional[str] = None
        self.copy_handler: CopyHandler = CopyHandler()
        self.is_split_view: bool = False
        self.is_file_browser_visible: bool = True
        self.projects: Dict[str, List[Dict[str, str]]] = self.load_projects()
        self.autosave_timer: QTimer = QTimer()
        self.autosave_timer.timeout.connect(self.autosave)
        self.autosave_timer.start(30000) # Autosave every 30 seconds
        self.initUI()
        self.setup_shortcuts()
        
        self.statusBar().showMessage('Ready')
        self.status_timer: QTimer = QTimer()
        self.status_timer.timeout.connect(lambda: self.statusBar().clearMessage())

    def show_status_message(self, message: str, timeout: int = 2000) -> None:
        self.statusBar().showMessage(message)
        self.status_timer.start(timeout)

    def setup_shortcuts(self):
        # Edit mode shortcuts
        self.edit_shortcut = QShortcut(QKeySequence(KeyBindings.TOGGLE_EDIT_MODE.value), self)
        self.edit_shortcut.activated.connect(lambda: (self.toggle_view(), 
            self.show_status_message(f'Toggle Edit Mode ({KeyBindings.TOGGLE_EDIT_MODE.value})')))

        # ESC shortcut
        self.esc_shortcut = QShortcut(QKeySequence(KeyBindings.EXIT_EDIT_MODE.value), self)
        self.esc_shortcut.activated.connect(lambda: self.return_to_preview())

        # Save shortcut
        self.save_shortcut = QShortcut(QKeySequence(KeyBindings.SAVE_FILE.value), self)
        self.save_shortcut.activated.connect(lambda: (self.save_file(), 
            self.show_status_message(f'File Saved ({KeyBindings.SAVE_FILE.value})')))

        # Undo shortcut
        self.undo_shortcut = QShortcut(QKeySequence(KeyBindings.UNDO.value), self)
        self.undo_shortcut.activated.connect(lambda: (self.input_text.undo(), 
            self.show_status_message(f'Undo ({KeyBindings.UNDO.value})')))

        # Redo shortcut
        self.redo_shortcut = QShortcut(QKeySequence(KeyBindings.REDO.value), self)
        self.redo_shortcut.activated.connect(lambda: (self.input_text.redo(), 
            self.show_status_message(f'Redo ({KeyBindings.REDO.value})')))

        # New file shortcut
        self.new_file_shortcut = QShortcut(QKeySequence(KeyBindings.NEW_FILE.value), self)
        self.new_file_shortcut.activated.connect(self.new_file)

        # Open file shortcut
        self.open_file_shortcut = QShortcut(QKeySequence(KeyBindings.OPEN_FILE.value), self)
        self.open_file_shortcut.activated.connect(self.open_file)

        # Find shortcut
        self.find_shortcut = QShortcut(QKeySequence(KeyBindings.FIND.value), self)
        self.find_shortcut.activated.connect(self.show_find_dialog)

        # Replace shortcut
        self.replace_shortcut = QShortcut(QKeySequence(KeyBindings.REPLACE.value), self)
        self.replace_shortcut.activated.connect(self.show_replace_dialog)

        # Toggle file browser shortcut
        self.toggle_browser_shortcut = QShortcut(QKeySequence(KeyBindings.TOGGLE_FILE_BROWSER.value), self)
        self.toggle_browser_shortcut.activated.connect(self.toggle_file_browser)

        # Cut, Copy, Paste shortcuts for the editor
        self.cut_shortcut = QShortcut(QKeySequence(KeyBindings.CUT.value), self)
        self.cut_shortcut.activated.connect(lambda: self.input_text.cut())
        
        self.copy_shortcut = QShortcut(QKeySequence(KeyBindings.COPY.value), self)
        self.copy_shortcut.activated.connect(lambda: self.input_text.copy())
        
        self.paste_shortcut = QShortcut(QKeySequence(KeyBindings.PASTE.value), self)
        self.paste_shortcut.activated.connect(lambda: self.input_text.paste())

    def create_button(self, text, shortcut, click_handler):
        """Helper function to create buttons with shortcut labels and proper font"""
        button = QPushButton(f"{text} ({shortcut})")
        button.setFont(FontStyle.BUTTON_TEXT.create_font())
        button.clicked.connect(click_handler)
        return button

    def initUI(self):
        # Set window properties
        self.setWindowTitle('Modern Markdown Editor')
        self.setGeometry(100, 100, 1200, 700)
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {ColorTheme.WINDOW_BG};
            }}
            QTextEdit {{
                background-color: {ColorTheme.EDITOR_BG};
                color: {ColorTheme.TEXT_PRIMARY};
                border: 1px solid {ColorTheme.ACCENT_SECONDARY};
                border-radius: 5px;
                padding: 8px;
                font-family: 'Consolas', monospace;
                font-size: 14px;
            }}
            QTreeView {{
                background-color: {ColorTheme.EDITOR_BG};
                color: {ColorTheme.TEXT_PRIMARY};
                border: 1px solid {ColorTheme.ACCENT_TERTIARY};
                border-radius: 5px;
                padding: 5px;
            }}
            QTreeView::item:hover {{
                background-color: {ColorTheme.HOVER_BG};
            }}
            QTreeView::item:selected {{
                background-color: {ColorTheme.ACCENT_PRIMARY};
                color: {ColorTheme.TEXT_PRIMARY};
            }}
            QPushButton {{
                background-color: {ColorTheme.BUTTON_BG};
                color: {ColorTheme.BUTTON_TEXT};
                border: 1px solid {ColorTheme.BUTTON_BORDER};
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {ColorTheme.BUTTON_HOVER_BG};
                color: {ColorTheme.BUTTON_HOVER_TEXT};
                border: 2px solid {ColorTheme.ACCENT_PRIMARY};
            }}
            QPushButton#burger-menu {{
                font-family: Arial;
                font-size: 16px;
                padding: 4px 8px;
                margin-right: 8px;
                min-width: 40px;
                color: {ColorTheme.ACCENT_PRIMARY};
            }}
            QPushButton#burger-menu:hover {{
                background-color: {ColorTheme.BUTTON_HOVER_BG};
                color: {ColorTheme.ACCENT_TERTIARY};
                border: 2px solid {ColorTheme.ACCENT_PRIMARY};
            }}
            QLineEdit {{
                background-color: {ColorTheme.EDITOR_BG};
                color: {ColorTheme.TEXT_PRIMARY};
                border: 1px solid {ColorTheme.ACCENT_TERTIARY};
                border-radius: 4px;
                padding: 5px;
                margin: 0 5px;
            }}
            QLineEdit:focus {{
                background-color: {ColorTheme.WINDOW_BG};
                color: {ColorTheme.TEXT_PRIMARY};
                border: 2px solid {ColorTheme.ACCENT_HIGHLIGHT};
            }}
            QTextEdit:focus {{
                background-color: {ColorTheme.EDITOR_BG};
                border: 2px solid {ColorTheme.ACCENT_PRIMARY};
            }}
            QStatusBar {{
                background-color: {ColorTheme.EDITOR_BG};
                color: {ColorTheme.ACCENT_SECONDARY};
                border-top: 1px solid {ColorTheme.ACCENT_TERTIARY};
            }}
            QToolButton {{
                background-color: {ColorTheme.BUTTON_BG};
                color: {ColorTheme.ACCENT_PRIMARY};
                border: 1px solid {ColorTheme.ACCENT_TERTIARY};
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
            }}
            QToolButton:hover {{
                background-color: {ColorTheme.BUTTON_HOVER_BG};
                color: {ColorTheme.ACCENT_TERTIARY};
                border: 2px solid {ColorTheme.ACCENT_PRIMARY};
            }}
            QToolButton::menu-indicator {{
                image: none;
            }}
            QMenu {{
                background-color: {ColorTheme.MENU_BG};
                color: {ColorTheme.MENU_TEXT};
                border: 1px solid {ColorTheme.MENU_BORDER};
            }}
            QMenu::item:selected {{
                background-color: {ColorTheme.MENU_ITEM_SELECTED};
                color: {ColorTheme.MENU_TEXT};
            }}
            QSplitter::handle {{
                background-color: {ColorTheme.ACCENT_TERTIARY};
            }}
            QScrollBar:vertical {{
                background-color: {ColorTheme.SCROLLBAR_BG};
                width: 12px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {ColorTheme.SCROLLBAR_HANDLE};
                border: 1px solid {ColorTheme.SCROLLBAR_BORDER};
                border-radius: 6px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {ColorTheme.BUTTON_HOVER_BG};
                border: 1px solid {ColorTheme.ACCENT_PRIMARY};
            }}
            QScrollBar:horizontal {{
                background-color: {ColorTheme.SCROLLBAR_BG};
                height: 12px;
                margin: 0px;
            }}
            QScrollBar::handle:horizontal {{
                background-color: {ColorTheme.SCROLLBAR_HANDLE};
                border: 1px solid {ColorTheme.SCROLLBAR_BORDER};
                border-radius: 6px;
                min-width: 20px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background-color: {ColorTheme.BUTTON_HOVER_BG};
                border: 1px solid {ColorTheme.ACCENT_PRIMARY};
            }}
        """)

        # Create central widget and main layout
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create top toolbar
        toolbar = QWidget()
        toolbar.setFixedHeight(50)
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setContentsMargins(10, 5, 10, 5)
        toolbar.setLayout(toolbar_layout)

        # Create burger menu button
        burger_menu_btn = QPushButton('☰')
        burger_menu_btn.setObjectName('burger-menu')
        burger_menu_btn.setFixedWidth(40)
        burger_menu_btn.setFixedHeight(36)
        burger_menu_btn.clicked.connect(self.toggle_file_browser)
        toolbar_layout.addWidget(burger_menu_btn)

        # Create address bar container
        address_container = QHBoxLayout()
        address_container.setSpacing(5)

        # Create address bar
        self.address_bar = QLineEdit()
        self.address_bar.setPlaceholderText("Enter folder path...")
        self.address_bar.returnPressed.connect(self.address_bar_navigate)
        address_container.addWidget(self.address_bar)

        # Create navigate button
        nav_btn = QPushButton('→')
        nav_btn.setFixedWidth(40)
        nav_btn.clicked.connect(self.address_bar_navigate)
        address_container.addWidget(nav_btn)

        # Add address container to toolbar with stretch factor
        toolbar_layout.addLayout(address_container, stretch=1)

        # Create toolbar buttons with shortcuts
        open_folder_btn = self.create_button('Browse', KeyBindings.OPEN_FILE.value, self.open_folder)
        toolbar_layout.addWidget(open_folder_btn)

        # Add project management button
        project_btn = QToolButton()
        project_btn.setText('Projects')
        project_menu = QMenu()
        project_btn.setMenu(project_menu)
        project_btn.setPopupMode(QToolButton.InstantPopup)
        self.update_project_menu(project_menu)
        toolbar_layout.addWidget(project_btn)

        # Add toggle view button with shortcut
        self.toggle_view_btn = self.create_button('Edit Mode', KeyBindings.TOGGLE_EDIT_MODE.value, self.toggle_view)
        self.toggle_view_btn.setCheckable(True)
        self.toggle_view_btn.setChecked(False)
        toolbar_layout.addWidget(self.toggle_view_btn)

        # Add new file button
        new_file_btn = self.create_button('New', KeyBindings.NEW_FILE.value, self.new_file)
        toolbar_layout.addWidget(new_file_btn)

        # Add save button
        save_btn = self.create_button('Save', KeyBindings.SAVE_FILE.value, self.save_file)
        toolbar_layout.addWidget(save_btn)

        # Add find button
        find_btn = self.create_button('Find', KeyBindings.FIND.value, self.show_find_dialog)
        toolbar_layout.addWidget(find_btn)

        # Add toolbar to main layout
        main_layout.addWidget(toolbar)

        # Create content area
        content = QWidget()
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        content.setLayout(content_layout)

        # Create file browser container
        self.browser_container = QWidget()
        self.browser_container.setFixedWidth(300)
        browser_layout = QVBoxLayout()
        browser_layout.setContentsMargins(0, 0, 0, 0)
        browser_layout.setSpacing(0)

        # Create file browser
        self.file_browser = QTreeView()
        self.file_system_model = QFileSystemModel()  # Create separate file system model
        self.file_system_model.setFilter(QDir.AllEntries | QDir.NoDotAndDotDot)
        self.file_system_model.setNameFilters(['*.md', '*.markdown', '*.prompt'])
        self.file_system_model.setNameFilterDisables(False)
        
        self.project_model = MultiProjectModel(self)  # Rename for clarity
        if self.projects.get("projects"):
            self.project_model.load_projects(self.projects["projects"])
        
        # Start with project model
        self.file_browser.setModel(self.project_model)
        self.current_model = self.project_model  # Track current model
        
        self.file_browser.clicked.connect(self.file_selected)
        self.file_browser.doubleClicked.connect(self.file_selected)
        self.file_browser.expanded.connect(self.on_tree_expanded)
        self.file_browser.collapsed.connect(self.on_tree_collapsed)
        self.file_browser.setColumnWidth(0, 200)
        self.file_browser.hideColumn(1)
        self.file_browser.hideColumn(2)
        self.file_browser.hideColumn(3)
        browser_layout.addWidget(self.file_browser)
        self.browser_container.setLayout(browser_layout)

        # Add browser to content layout
        content_layout.addWidget(self.browser_container)

        # Create editor container
        editor_container = QWidget()
        editor_layout = QVBoxLayout()
        editor_layout.setContentsMargins(0, 0, 0, 0)
        editor_layout.setSpacing(0)

        # Create splitter
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setHandleWidth(1)

        # Create input text area with editor font
        self.input_text = QTextEdit()
        self.input_text.setFont(FontStyle.EDITOR_MAIN.create_font())
        self.input_text.textChanged.connect(self.update_preview)
        self.input_text.setVisible(False)  # Start in preview mode

        # Create preview area
        self.preview_area = QWebEngineView()
        settings = self.preview_area.settings()
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.ErrorPageEnabled, True)
        settings.setAttribute(QWebEngineSettings.PluginsEnabled, True)

        # Add widgets to splitter
        self.splitter.addWidget(self.input_text)
        self.splitter.addWidget(self.preview_area)
        self.splitter.setSizes([0, self.width()])  # Start with preview only

        # Add splitter to editor layout
        editor_layout.addWidget(self.splitter)
        editor_container.setLayout(editor_layout)

        # Add editor container to content layout
        content_layout.addWidget(editor_container)

        # Add content to main layout
        main_layout.addWidget(content)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Set up web channel
        channel = QWebChannel()
        channel.registerObject('copyHandler', self.copy_handler)
        self.preview_area.page().setWebChannel(channel)

        # Initial preview
        self.update_preview()
        self.update_toggle_button_state()

        # Apply fonts to UI elements
        self.setFont(FontStyle.TITLE_BAR.create_font())
        self.statusBar().setFont(FontStyle.STATUS_BAR.create_font())
        self.file_browser.setFont(FontStyle.FILE_BROWSER.create_font())

    def update_toggle_button_state(self):
        if self.is_split_view:
            self.toggle_view_btn.setText('Preview Only')
            self.input_text.setVisible(True)
            self.splitter.setSizes([self.width() // 2, self.width() // 2])
        else:
            self.toggle_view_btn.setText('Edit Mode')
            self.input_text.setVisible(False)
            self.splitter.setSizes([0, self.width()])

    def load_projects(self) -> Dict[str, List[Dict[str, str]]]:
        try:
            with open('projects.json', 'r') as f:
                data = json.load(f)
                if not isinstance(data, dict) or "projects" not in data:
                    return {"projects": []}
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            # Create default projects.json
            default_projects = {
                "projects": [
                    {
                        "name": "Documents",
                        "path": os.path.expanduser("~/Documents")
                    }
                ]
            }
            with open('projects.json', 'w') as f:
                json.dump(default_projects, f, indent=4)
            return default_projects

    def save_projects(self) -> None:
        with open('projects.json', 'w') as f:
            json.dump(self.projects, f, indent=4)

    def update_project_menu(self, menu: QMenu) -> None:
        menu.clear()
        add_project_action = menu.addAction('Add Current Folder as Project')
        add_project_action.triggered.connect(self.add_project)
        if self.projects["projects"]:
            menu.addSeparator()
            for project in self.projects["projects"]:
                project_action = menu.addAction(project["name"])
                project_action.triggered.connect(
                    lambda checked, path=project["path"]: self.open_project(path)
                )
                remove_action = menu.addAction(f"Remove {project['name']}")
                remove_action.triggered.connect(
                    lambda checked, name=project["name"]: self.remove_project(name)
                )
                menu.addSeparator()

    def add_project(self):
        if not self.file_model.rootPath():
            QMessageBox.warning(self, "Warning", "Please open a folder first")
            return

        name, ok = QInputDialog.getText(
            self, 'Add Project', 'Enter project name:'
        )
        if ok and name:
            current_path = self.file_model.rootPath()
            self.projects["projects"].append({
                "name": name,
                "path": current_path
            })
            self.save_projects()
            self.update_project_menu(self.findChild(QToolButton).menu())

    def remove_project(self, project_name):
        self.projects["projects"] = [
            p for p in self.projects["projects"] if p["name"] != project_name
        ]
        self.save_projects()
        self.update_project_menu(self.findChild(QToolButton).menu())

    def open_project(self, path: str) -> None:
        """Open a project directory with improved path handling"""
        try:
            path = os.path.normpath(os.path.abspath(path))
            
            if not os.path.exists(path):
                QMessageBox.warning(self, "Warning", "Project folder no longer exists")
                return

            # Switch to file system model for project contents
            self.file_browser.setModel(self.file_system_model)
            self.current_model = self.file_system_model
            
            # Set root path
            root_index = self.file_system_model.setRootPath(path)
            if not root_index.isValid():
                raise Exception("Failed to set root path in model")

            # Set root index in view
            self.file_browser.setRootIndex(root_index)
            
            # Update address bar and status
            self.address_bar.setText(path)
            self.show_status_message(f'Opened project: {os.path.basename(path)}')
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open project: {str(e)}")

    def autosave(self):
        if self.current_file and os.path.exists(self.current_file):
            try:
                with open(self.current_file, 'w', encoding='utf-8') as file:
                    file.write(self.input_text.toPlainText())
            except Exception as e:
                print(f"Autosave failed: {str(e)}")

    def update_preview(self):
        """Improved markdown preview with better code block handling"""
        preview_style = FontStyle.PREVIEW_BODY.value  # Define this first for error handling
        code_style = FontStyle.PREVIEW_CODE.value  # Keep code font separate
        h1_style = FontStyle.EDITOR_HEADING1.value  # Restore heading styles
        h2_style = FontStyle.EDITOR_HEADING2.value
        try:
            markdown_text = self.input_text.toPlainText()
            
            # Pre-process code blocks to prevent markdown2 from failing
            code_block_pattern = r'```(.*?)\n(.*?)```'
            
            def code_block_replacer(match):
                header = match.group(1) or ''
                code = match.group(2) or ''
                
                # Handle empty code blocks
                if not code.strip():
                    return '```\n \n```'  # Add a space to prevent parser errors
                
                # Process code block content
                lines = code.split('\n')
                # Remove empty lines at start and end
                while lines and not lines[0].strip():
                    lines.pop(0)
                while lines and not lines[-1].strip():
                    lines.pop()
                
                if not lines:  # If all lines were empty
                    return '```\n \n```'
                
                # Ensure consistent indentation
                min_indent = float('inf')
                for line in lines:
                    if line.strip():  # Only check non-empty lines
                        indent = len(line) - len(line.lstrip())
                        min_indent = min(min_indent, indent)
                
                if min_indent == float('inf'):
                    min_indent = 0
                
                # Remove common indentation and ensure at least 4 spaces
                processed_lines = []
                for line in lines:
                    if line.strip():  # Keep empty lines as-is
                        line = line[min_indent:]
                    processed_lines.append('    ' + line)
                
                # Reconstruct the code block
                processed_code = '\n'.join(processed_lines)
                return f'```{header}\n{processed_code}\n```'
            
            # Pre-process code blocks
            processed_text = re.sub(code_block_pattern, code_block_replacer, markdown_text, flags=re.DOTALL)
            
            # Convert markdown to HTML with fallback
            try:
                html_content = markdown2.markdown(
                    processed_text,
                    extras=[
                        'fenced-code-blocks',
                        'tables',
                        'code-friendly',
                        'break-on-newline',
                        'cuddled-lists',
                        'markdown-in-html'
                    ]
                )
            except Exception as md_error:
                # Fallback to simpler conversion if full conversion fails
                try:
                    html_content = markdown2.markdown(
                        processed_text,
                        extras=['code-friendly']
                    )
                except:
                    raise Exception(f"Markdown conversion failed: {str(md_error)}")

            # Rest of your existing HTML template code...
            full_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <script type="text/javascript" src="qrc:///qtwebchannel/qwebchannel.js"></script>
                <style>
                    body {{
                        font-family: {preview_style['family']};
                        font-size: {preview_style['size']}pt;
                        font-weight: {preview_style['weight']};
                        line-height: 1.6;
                        padding: 20px;
                        color: #333;
                        max-width: 900px;
                        margin: 0 auto;
                    }}
                    pre, code {{
                        font-family: {code_style['family']};
                        font-size: {code_style['size']}pt;
                        font-weight: {code_style['weight']};
                        background-color: #f6f8fa;
                        border-radius: 3px;
                    }}
                    pre {{
                        padding: 16px;
                        overflow-x: auto;
                        white-space: pre-wrap;
                        word-wrap: break-word;
                        margin: 1em 0;
                    }}
                    code {{
                        padding: 2px 4px;
                    }}
                    h1 {{
                        font-family: {h1_style['family']};
                        font-size: {h1_style['size']}pt;
                        font-weight: {h1_style['weight']};
                        border-bottom: 2px solid #eaecef;
                        padding-bottom: 0.3em;
                        margin-top: 1.5em;
                        margin-bottom: 1em;
                        color: #24292e;
                    }}
                    h2 {{
                        font-family: {h2_style['family']};
                        font-size: {h2_style['size']}pt;
                        font-weight: {h2_style['weight']};
                        border-bottom: 1px solid #eaecef;
                        padding-bottom: 0.3em;
                        margin-top: 1.5em;
                        margin-bottom: 1em;
                        color: #24292e;
                    }}
                    h3 {{
                        font-family: {h2_style['family']};
                        font-size: {int(h2_style['size'] * 0.8)}pt;
                        font-weight: {h2_style['weight']};
                        margin-top: 1.2em;
                        margin-bottom: 0.8em;
                        color: #24292e;
                    }}
                    h4 {{
                        font-family: {h2_style['family']};
                        font-size: {int(h2_style['size'] * 0.7)}pt;
                        font-weight: {h2_style['weight']};
                        margin-top: 1.2em;
                        margin-bottom: 0.8em;
                        color: #24292e;
                    }}
                    blockquote {{
                        font-family: {preview_style['family']};
                        font-size: {preview_style['size']}pt;
                        font-style: italic;
                        padding: 0 1em;
                        border-left: 0.25em solid #dfe2e5;
                        margin: 1em 0;
                        color: #6a737d;
                    }}
                    table {{
                        border-collapse: collapse;
                        width: 100%;
                        margin: 1em 0;
                    }}
                    th, td {{
                        border: 1px solid #dfe2e5;
                        padding: 6px 13px;
                    }}
                    th {{
                        background-color: #f6f8fa;
                        font-weight: 600;
                    }}
                    tr:nth-child(even) {{
                        background-color: #f6f8fa;
                    }}
                    ul, ol {{
                        padding-left: 2em;
                        margin: 1em 0;
                    }}
                    li {{
                        margin: 0.5em 0;
                    }}
                    hr {{
                        height: 2px;
                        background-color: #e1e4e8;
                        border: none;
                        margin: 2em 0;
                    }}
                    a {{
                        color: #0366d6;
                        text-decoration: none;
                    }}
                    a:hover {{
                        text-decoration: underline;
                    }}
                    img {{
                        max-width: 100%;
                        height: auto;
                    }}
                    .language-diff {{
                        color: #24292e;
                    }}
                    .language-diff .deletion {{
                        background-color: #ffeef0;
                        color: #b31d28;
                    }}
                    .language-diff .addition {{
                        background-color: #e6ffed;
                        color: #22863a;
                    }}
                </style>
            </head>
            <body>
                {html_content}
            </body>
            </html>
            """
            self.preview_area.setHtml(full_html)
            
        except Exception as e:
            error_html = f"""
            <html>
            <body style="color: red; font-family: {preview_style['family']};">
                <h3>Error rendering markdown:</h3>
                <pre>{str(e)}</pre>
            </body>
            </html>
            """
            self.preview_area.setHtml(error_html)
            print(f"Preview error: {str(e)}")

    def open_folder(self):
        """Open a folder dialog to select and set the root directory"""
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.file_browser.setRootIndex(self.file_model.setRootPath(folder))
            self.address_bar.setText(folder)
            self.show_status_message(f'Opened folder: {folder}')

    def file_selected(self, index: QModelIndex) -> None:
        """Improved file selection handling"""
        try:
            # Get file path based on current model
            if self.current_model == self.project_model:
                file_path = self.project_model.filePath(index)
                if os.path.isdir(file_path):
                    self.open_project(file_path)
                    return
            else:
                file_path = self.file_system_model.filePath(index)

            if not file_path:
                return

            if os.path.isdir(file_path):
                if self.file_browser.isExpanded(index):
                    self.file_browser.collapse(index)
                else:
                    self.file_browser.expand(index)
                return

            if not file_path.lower().endswith(('.md', '.markdown', '.prompt')):
                return

            # Try to open the file with different encodings
            for encoding in ['utf-8', 'utf-8-sig', 'latin1', 'cp1252']:
                try:
                    with open(file_path, 'r', encoding=encoding) as file:
                        content = file.read()
                        self.input_text.setText(content)
                        self.current_file = file_path
                        self.setWindowTitle(f'Modern Markdown Editor - {os.path.basename(file_path)}')
                        self.show_status_message(f'Opened file: {os.path.basename(file_path)}')
                        break
                except UnicodeDecodeError:
                    continue
                except Exception as e:
                    raise Exception(f"Error opening file: {str(e)}")
            else:
                raise Exception("Could not decode file with any supported encoding")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def toggle_file_browser(self):
        self.is_file_browser_visible = not self.is_file_browser_visible
        width = 300 if self.is_file_browser_visible else 0
        self.browser_container.setFixedWidth(width)
        self.browser_container.setVisible(self.is_file_browser_visible)

    def update_projects_list(self):
        self.projects_list.clear()
        for project in self.projects["projects"]:
            item = QListWidgetItem(f"📁 {project['name']}")
            item.setData(Qt.UserRole, project["path"])
            self.projects_list.addItem(item)

    def project_selected(self, item):
        project_path = item.data(Qt.UserRole)
        if os.path.exists(project_path):
            self.file_browser.setRootIndex(self.file_model.setRootPath(project_path))
        else:
            QMessageBox.warning(self, "Warning", "Project folder no longer exists")

    def address_bar_navigate(self):
        """Improved address bar navigation with better path handling"""
        try:
            path = self.address_bar.text()
            path = self.file_model.normalize_path(path)
            
            if os.path.exists(path) and os.path.isdir(path):
                root_index = self.file_model.setRootPath(path)
                self.file_browser.setRootIndex(root_index)
                self.address_bar.setText(path)
                self.show_status_message(f'Navigated to: {path}')
            else:
                self.show_status_message('Invalid path', 2000)
        except Exception as e:
            self.show_status_message(f'Navigation error: {str(e)}', 2000)

    def save_file(self):
        if self.current_file and os.path.exists(self.current_file):
            try:
                with open(self.current_file, 'w', encoding='utf-8') as file:
                    file.write(self.input_text.toPlainText())
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save file: {str(e)}")
        else:
            self.save_file_as()

    def save_file_as(self):
        try:
            # Get current project directory from file browser
            current_dir = self.file_model.rootPath() or ""
            
            file_filters = (
                "Markdown Files (*.md *.markdown);;"
                "Prompt Files (*.prompt);;"
                "All Files (*.*)"
            )
            
            file_path, selected_filter = QFileDialog.getSaveFileName(
                self,
                "Save File As",
                current_dir,
                file_filters
            )
            
            if not file_path:
                return
            
            # Add appropriate extension if none provided
            if not any(file_path.lower().endswith(ext) for ext in ['.md', '.markdown', '.prompt']):
                if "Markdown" in selected_filter:
                    file_path += '.md'
                elif "Prompt" in selected_filter:
                    file_path += '.prompt'
            
            # Validate and enforce .prompt file naming conventions
            if file_path.lower().endswith('.prompt'):
                directory = os.path.dirname(file_path)
                filename = os.path.basename(file_path)
                if not filename.startswith('prompt.'):
                    filename = 'prompt.' + filename
                    file_path = os.path.join(directory, filename)
                
                # Additional validation for prompt files
                if not os.access(directory, os.W_OK):
                    raise PermissionError(f"No write permission for directory: {directory}")
            
            # Save the file
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(self.input_text.toPlainText())
            
            self.current_file = file_path
            self.setWindowTitle(f'Modern Markdown Editor - {os.path.basename(file_path)}')
            self.show_status_message(f'File saved successfully: {os.path.basename(file_path)}')
            
        except PermissionError as e:
            QMessageBox.critical(self, "Permission Error", str(e))
        except OSError as e:
            QMessageBox.critical(self, "File System Error", f"Could not save file: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Unexpected error while saving: {str(e)}")

    def return_to_preview(self):
        if self.is_split_view:
            self.is_split_view = False
            self.update_toggle_button_state()
            self.toggle_view()
            self.show_status_message('Returned to Preview Mode (ESC)')

    def new_file(self):
        """Create a new file"""
        if self.current_file and self.input_text.document().isModified():
            reply = QMessageBox.question(self, 'Save Changes?',
                'Do you want to save changes to the current file?',
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
            
            if reply == QMessageBox.Save:
                self.save_file()
            elif reply == QMessageBox.Cancel:
                return
        
        self.current_file = None
        self.input_text.clear()
        self.setWindowTitle('Modern Markdown Editor - New File')
        
        # Force switch to split view
        self.is_split_view = False  # Set to False first to ensure toggle works correctly
        self.toggle_view()  # This will switch to split view
        self.show_status_message('New File Created - Edit Mode')
        
        # Switch to split view
        if not self.is_split_view:
            self.is_split_view = True
            self.update_toggle_button_state()
            self.toggle_view()

    def show_find_dialog(self):
        """Show find dialog"""
        text, ok = QInputDialog.getText(self, 'Find', 'Enter text to find:')
        if ok and text:
            cursor = self.input_text.document().find(text)
            if not cursor.isNull():
                self.input_text.setTextCursor(cursor)
            else:
                self.show_status_message('Text not found')

    def show_replace_dialog(self):
        """Show replace dialog"""
        find_text, ok = QInputDialog.getText(self, 'Replace', 'Find text:')
        if ok and find_text:
            replace_text, ok = QInputDialog.getText(self, 'Replace', 'Replace with:')
            if ok:
                cursor = self.input_text.textCursor()
                text = self.input_text.toPlainText()
                new_text = text.replace(find_text, replace_text)
                self.input_text.setPlainText(new_text)
                self.show_status_message(f'Replaced {find_text} with {replace_text}')

    def toggle_view(self):
        """Toggle between edit and preview modes"""
        self.is_split_view = not self.is_split_view
        self.update_toggle_button_state()
        self.input_text.setVisible(self.is_split_view)
        
        if self.is_split_view:
            # Split view - show both editor and preview
            self.preview_area.setMaximumWidth(16777215)
            self.input_text.setMaximumWidth(16777215)
            self.input_text.setMinimumWidth(300)
            self.preview_area.setMinimumWidth(300)
            self.show_status_message('Edit Mode Enabled')
        else:
            # Preview only
            self.preview_area.setMaximumWidth(16777215)
            self.preview_area.setMinimumWidth(600)
            self.input_text.setMaximumWidth(0)
            self.input_text.setMinimumWidth(0)
            self.show_status_message('Preview Mode Enabled')

    def open_file(self):
        """Open a file dialog to select and open a markdown file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            "",
            "Markdown Files (*.md *.markdown *.prompt);;All Files (*.*)"
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                self.input_text.setText(content)
                self.current_file = file_path
                self.setWindowTitle(f'Modern Markdown Editor - {os.path.basename(file_path)}')
                self.show_status_message(f'Opened {os.path.basename(file_path)}')
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not open file: {str(e)}")

    def on_tree_expanded(self, index):
        """Handle tree expansion"""
        path = self.file_model.filePath(index)
        if path and os.path.isdir(path):
            self.file_browser.resizeColumnToContents(0)

    def on_tree_collapsed(self, index):
        """Handle tree collapse"""
        self.file_browser.resizeColumnToContents(0)

def main():
    # Enable High DPI display
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # Set cache directory to a user-writable location
    cache_dir = os.path.join(os.path.expanduser('~'), '.markdown_editor_cache')
    os.makedirs(cache_dir, exist_ok=True)
    os.environ['QTWEBENGINE_DISK_CACHE_DIR'] = cache_dir
        
    app = QApplication(sys.argv)
    editor = MarkdownEditor()
    editor.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
