from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor

class ThemeManager(QObject):
    """Manages application themes and styling"""
    theme_changed = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.current_theme = "light"
        self.themes = {
            "light": self._get_light_theme(),
            "dark": self._get_dark_theme(),
            "nature": self._get_nature_theme()
        }
    
    def _get_light_theme(self):
        """Light theme configuration"""
        return {
            "name": "Light",
            "colors": {
                "background": "#FFFFFF",
                "surface": "#F8F9FA",
                "primary": "#2196F3",
                "primary_dark": "#1976D2",
                "secondary": "#03DAC6",
                "accent": "#FF5722",
                "text_primary": "#212121",
                "text_secondary": "#757575",
                "text_hint": "#BDBDBD",
                "border": "#E0E0E0",
                "border_focus": "#2196F3",
                "success": "#4CAF50",
                "warning": "#FF9800",
                "error": "#F44336",
                "info": "#2196F3"
            },
            "stylesheet": """
                /* Main Window */
                QMainWindow {
                    background-color: #FFFFFF;
                    color: #212121;
                }
                
                /* Group Boxes */
                QGroupBox {
                    font-weight: bold;
                    border: 2px solid #E0E0E0;
                    border-radius: 8px;
                    margin: 8px 0px;
                    padding-top: 10px;
                    background-color: #F8F9FA;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 8px 0 8px;
                    color: #2196F3;
                }
                
                /* Buttons */
                QPushButton {
                    background-color: #2196F3;
                    border: none;
                    color: white;
                    padding: 8px 16px;
                    border-radius: 6px;
                    font-weight: bold;
                    min-height: 20px;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
                QPushButton:pressed {
                    background-color: #1565C0;
                }
                QPushButton:disabled {
                    background-color: #BDBDBD;
                    color: #757575;
                }
                
                /* Secondary Buttons */
                QPushButton[class="secondary"] {
                    background-color: #F8F9FA;
                    color: #2196F3;
                    border: 2px solid #2196F3;
                }
                QPushButton[class="secondary"]:hover {
                    background-color: #E3F2FD;
                }
                
                /* Input Fields */
                QLineEdit, QSpinBox, QComboBox, QDateEdit {
                    padding: 8px 12px;
                    border: 2px solid #E0E0E0;
                    border-radius: 6px;
                    background-color: white;
                    color: #212121;
                    selection-background-color: #2196F3;
                }
                QLineEdit:focus, QSpinBox:focus, QComboBox:focus, QDateEdit:focus {
                    border-color: #2196F3;
                    outline: none;
                }
                
                /* SpinBox buttons */
                QSpinBox::up-button, QSpinBox::down-button {
                    background-color: #F5F5F5;
                    border: 1px solid #E0E0E0;
                    width: 16px;
                }
                QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                    background-color: #E3F2FD;
                    border-color: #2196F3;
                }
                QSpinBox::up-button:pressed, QSpinBox::down-button:pressed {
                    background-color: #BBDEFB;
                }
                
                /* ComboBox dropdown */
                QComboBox::drop-down {
                    background-color: #F5F5F5;
                    border: 1px solid #E0E0E0;
                    width: 20px;
                }
                QComboBox::drop-down:hover {
                    background-color: #E3F2FD;
                    border-color: #2196F3;
                }
                
                /* Disabled state styling */
                QLineEdit:disabled, QSpinBox:disabled, QComboBox:disabled, QDateEdit:disabled {
                    background-color: #F5F5F5;
                    color: #BDBDBD;
                    border-color: #E0E0E0;
                }
                QCheckBox:disabled {
                    color: #BDBDBD;
                }
                QCheckBox::indicator:disabled {
                    background-color: #F5F5F5;
                    border-color: #E0E0E0;
                }
                QGroupBox:disabled {
                    color: #BDBDBD;
                }
                QGroupBox::title:disabled {
                    color: #BDBDBD;
                }
                
                /* Table Widget */
                QTableWidget {
                    gridline-color: #E0E0E0;
                    background-color: white;
                    alternate-background-color: #F8F9FA;
                    selection-background-color: #E3F2FD;
                    border: 1px solid #E0E0E0;
                    border-radius: 8px;
                }
                QTableWidget::item {
                    padding: 8px;
                    border: none;
                }
                QTableWidget::item:selected {
                    background-color: #E3F2FD;
                    color: #1976D2;
                }
                QHeaderView::section {
                    background-color: #F5F5F5;
                    padding: 8px;
                    border: none;
                    border-bottom: 2px solid #2196F3;
                    font-weight: bold;
                    color: #212121;
                }
                
                /* Progress Bar */
                QProgressBar {
                    border: 2px solid #E0E0E0;
                    border-radius: 8px;
                    text-align: center;
                    background-color: #F5F5F5;
                }
                QProgressBar::chunk {
                    background-color: #2196F3;
                    border-radius: 6px;
                }
                
                /* Menu Bar */
                QMenuBar {
                    background-color: #F8F9FA;
                    border-bottom: 1px solid #E0E0E0;
                    padding: 4px;
                }
                QMenuBar::item {
                    padding: 8px 12px;
                    border-radius: 4px;
                }
                QMenuBar::item:selected {
                    background-color: #E3F2FD;
                    color: #1976D2;
                }
                QMenu {
                    background-color: white;
                    border: 1px solid #E0E0E0;
                    border-radius: 8px;
                    padding: 4px;
                }
                QMenu::item {
                    padding: 8px 16px;
                    border-radius: 4px;
                }
                QMenu::item:selected {
                    background-color: #E3F2FD;
                    color: #1976D2;
                }
                
                /* Status Bar */
                QStatusBar {
                    background-color: #F8F9FA;
                    border-top: 1px solid #E0E0E0;
                    color: #757575;
                }
                
                /* Checkboxes */
                QCheckBox {
                    spacing: 8px;
                    color: #212121;
                }
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                    border: 2px solid #E0E0E0;
                    border-radius: 4px;
                    background-color: white;
                }
                QCheckBox::indicator:checked {
                    background-color: #2196F3;
                    border-color: #2196F3;
                    image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1zbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEwIDNMNC41IDguNUwyIDYiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4KPC9zdmc+);
                }
                
                /* Labels */
                QLabel {
                    color: #212121;
                }
                
                /* Scrollbars */
                QScrollBar:vertical {
                    background-color: #F5F5F5;
                    width: 12px;
                    border-radius: 6px;
                }
                QScrollBar::handle:vertical {
                    background-color: #BDBDBD;
                    border-radius: 6px;
                    min-height: 20px;
                }
                QScrollBar::handle:vertical:hover {
                    background-color: #9E9E9E;
                }
            """
        }
    
    def _get_dark_theme(self):
        """Dark theme configuration"""
        return {
            "name": "Dark",
            "colors": {
                "background": "#121212",
                "surface": "#1E1E1E",
                "primary": "#BB86FC",
                "primary_dark": "#985EFF",
                "secondary": "#03DAC6",
                "accent": "#CF6679",
                "text_primary": "#FFFFFF",
                "text_secondary": "#B3B3B3",
                "text_hint": "#666666",
                "border": "#333333",
                "border_focus": "#BB86FC",
                "success": "#4CAF50",
                "warning": "#FF9800",
                "error": "#CF6679",
                "info": "#03DAC6"
            },
            "stylesheet": """
                /* Main Window */
                QMainWindow {
                    background-color: #121212;
                    color: #FFFFFF;
                }
                
                /* Group Boxes */
                QGroupBox {
                    font-weight: bold;
                    border: 2px solid #333333;
                    border-radius: 8px;
                    margin: 8px 0px;
                    padding-top: 10px;
                    background-color: #1E1E1E;
                    color: #FFFFFF;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 8px 0 8px;
                    color: #BB86FC;
                }
                
                /* Buttons */
                QPushButton {
                    background-color: #BB86FC;
                    border: none;
                    color: #121212;
                    padding: 8px 16px;
                    border-radius: 6px;
                    font-weight: bold;
                    min-height: 20px;
                }
                QPushButton:hover {
                    background-color: #985EFF;
                }
                QPushButton:pressed {
                    background-color: #7C4DFF;
                }
                QPushButton:disabled {
                    background-color: #333333;
                    color: #666666;
                }
                
                /* Secondary Buttons */
                QPushButton[class="secondary"] {
                    background-color: #1E1E1E;
                    color: #BB86FC;
                    border: 2px solid #BB86FC;
                }
                QPushButton[class="secondary"]:hover {
                    background-color: #2D2D2D;
                }
                
                /* Input Fields */
                QLineEdit, QSpinBox, QComboBox, QDateEdit {
                    padding: 8px 12px;
                    border: 2px solid #333333;
                    border-radius: 6px;
                    background-color: #2D2D2D;
                    color: #FFFFFF;
                    selection-background-color: #BB86FC;
                }
                QLineEdit:focus, QSpinBox:focus, QComboBox:focus, QDateEdit:focus {
                    border-color: #BB86FC;
                    outline: none;
                }
                
                /* SpinBox buttons */
                QSpinBox::up-button, QSpinBox::down-button {
                    background-color: #404040;
                    border: 1px solid #333333;
                    width: 16px;
                }
                QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                    background-color: #505050;
                    border-color: #BB86FC;
                }
                QSpinBox::up-button:pressed, QSpinBox::down-button:pressed {
                    background-color: #606060;
                }
                
                /* ComboBox dropdown */
                QComboBox::drop-down {
                    background-color: #404040;
                    border: 1px solid #333333;
                    width: 20px;
                }
                QComboBox::drop-down:hover {
                    background-color: #505050;
                    border-color: #BB86FC;
                }
                
                /* Disabled state styling */
                QLineEdit:disabled, QSpinBox:disabled, QComboBox:disabled, QDateEdit:disabled {
                    background-color: #1A1A1A;
                    color: #555555;
                    border-color: #2A2A2A;
                }
                QSpinBox::up-button:disabled, QSpinBox::down-button:disabled {
                    background-color: #1A1A1A;
                    border-color: #2A2A2A;
                }
                QComboBox::drop-down:disabled {
                    background-color: #1A1A1A;
                    border-color: #2A2A2A;
                }
                QCheckBox:disabled {
                    color: #555555;
                }
                QCheckBox::indicator:disabled {
                    background-color: #1A1A1A;
                    border-color: #2A2A2A;
                }
                QGroupBox:disabled {
                    color: #555555;
                    border-color: #2A2A2A;
                    background-color: #161616;
                }
                QGroupBox::title:disabled {
                    color: #555555;
                }
                
                /* Table Widget */
                QTableWidget {
                    gridline-color: #333333;
                    background-color: #1E1E1E;
                    alternate-background-color: #2D2D2D;
                    selection-background-color: #3D3D3D;
                    border: 1px solid #333333;
                    border-radius: 8px;
                    color: #FFFFFF;
                }
                QTableWidget::item {
                    padding: 8px;
                    border: none;
                }
                QTableWidget::item:selected {
                    background-color: #3D3D3D;
                    color: #BB86FC;
                }
                QHeaderView::section {
                    background-color: #2D2D2D;
                    padding: 8px;
                    border: none;
                    border-bottom: 2px solid #BB86FC;
                    font-weight: bold;
                    color: #FFFFFF;
                }
                
                /* Progress Bar */
                QProgressBar {
                    border: 2px solid #333333;
                    border-radius: 8px;
                    text-align: center;
                    background-color: #2D2D2D;
                    color: #FFFFFF;
                }
                QProgressBar::chunk {
                    background-color: #BB86FC;
                    border-radius: 6px;
                }
                
                /* Menu Bar */
                QMenuBar {
                    background-color: #1E1E1E;
                    border-bottom: 1px solid #333333;
                    padding: 4px;
                    color: #FFFFFF;
                }
                QMenuBar::item {
                    padding: 8px 12px;
                    border-radius: 4px;
                }
                QMenuBar::item:selected {
                    background-color: #3D3D3D;
                    color: #BB86FC;
                }
                QMenu {
                    background-color: #1E1E1E;
                    border: 1px solid #333333;
                    border-radius: 8px;
                    padding: 4px;
                    color: #FFFFFF;
                }
                QMenu::item {
                    padding: 8px 16px;
                    border-radius: 4px;
                }
                QMenu::item:selected {
                    background-color: #3D3D3D;
                    color: #BB86FC;
                }
                
                /* Status Bar */
                QStatusBar {
                    background-color: #1E1E1E;
                    border-top: 1px solid #333333;
                    color: #B3B3B3;
                }
                
                /* Checkboxes */
                QCheckBox {
                    spacing: 8px;
                    color: #FFFFFF;
                }
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                    border: 2px solid #333333;
                    border-radius: 4px;
                    background-color: #2D2D2D;
                }
                QCheckBox::indicator:checked {
                    background-color: #BB86FC;
                    border-color: #BB86FC;
                    image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1zbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEwIDNMNC41IDguNUwyIDYiIHN0cm9rZT0iIzEyMTIxMiIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4KPC9zdmc+);
                }
                
                /* Labels */
                QLabel {
                    color: #FFFFFF;
                }
                
                /* Scrollbars */
                QScrollBar:vertical {
                    background-color: #2D2D2D;
                    width: 12px;
                    border-radius: 6px;
                }
                QScrollBar::handle:vertical {
                    background-color: #666666;
                    border-radius: 6px;
                    min-height: 20px;
                }
                QScrollBar::handle:vertical:hover {
                    background-color: #888888;
                }
                
                /* Dialog and Tab styling for dark theme */
                QDialog {
                    background-color: #121212;
                    color: #FFFFFF;
                }
                QTabWidget::pane {
                    border: 1px solid #333333;
                    background-color: #1E1E1E;
                }
                QTabWidget::tab-bar {
                    alignment: left;
                }
                QTabBar::tab {
                    background-color: #2D2D2D;
                    color: #FFFFFF;
                    padding: 8px 16px;
                    border: 1px solid #333333;
                    border-bottom: none;
                    border-radius: 4px 4px 0px 0px;
                    margin-right: 2px;
                }
                QTabBar::tab:selected {
                    background-color: #1E1E1E;
                    color: #BB86FC;
                    border-color: #BB86FC;
                }
                QTabBar::tab:hover {
                    background-color: #3D3D3D;
                }
                
                /* Fix for settings dialog groupbox titles in dark theme */
                QDialog QGroupBox {
                    font-weight: bold;
                    border: 2px solid #333333;
                    border-radius: 8px;
                    margin: 8px 0px;
                    padding-top: 10px;
                    background-color: #1E1E1E;
                    color: #FFFFFF;
                }
                QDialog QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 8px 0 8px;
                    color: #BB86FC;
                    background-color: #1E1E1E;
                }
            """
        }
    
    def _get_nature_theme(self):
        """Nature theme configuration"""
        return {
            "name": "Nature",
            "colors": {
                "background": "#F1F8E9",
                "surface": "#E8F5E8",
                "primary": "#4CAF50",
                "primary_dark": "#388E3C",
                "secondary": "#8BC34A",
                "accent": "#FF7043",
                "text_primary": "#1B5E20",
                "text_secondary": "#2E7D32",
                "text_hint": "#66BB6A",
                "border": "#A5D6A7",
                "border_focus": "#4CAF50",
                "success": "#66BB6A",
                "warning": "#FF8F00",
                "error": "#D32F2F",
                "info": "#00ACC1"
            },
            "stylesheet": """
                /* Main Window */
                QMainWindow {
                    background-color: #F1F8E9;
                    color: #1B5E20;
                }
                
                /* Group Boxes */
                QGroupBox {
                    font-weight: bold;
                    border: 2px solid #A5D6A7;
                    border-radius: 12px;
                    margin: 8px 0px;
                    padding-top: 10px;
                    background-color: #E8F5E8;
                    color: #1B5E20;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 8px 0 8px;
                    color: #4CAF50;
                }
                
                /* Buttons */
                QPushButton {
                    background-color: #4CAF50;
                    border: none;
                    color: white;
                    padding: 8px 16px;
                    border-radius: 8px;
                    font-weight: bold;
                    min-height: 20px;
                }
                QPushButton:hover {
                    background-color: #388E3C;
                }
                QPushButton:pressed {
                    background-color: #2E7D32;
                }
                QPushButton:disabled {
                    background-color: #A5D6A7;
                    color: #66BB6A;
                }
                
                /* Secondary Buttons */
                QPushButton[class="secondary"] {
                    background-color: #E8F5E8;
                    color: #4CAF50;
                    border: 2px solid #4CAF50;
                }
                QPushButton[class="secondary"]:hover {
                    background-color: #C8E6C9;
                }
                
                /* Input Fields */
                QLineEdit, QSpinBox, QComboBox, QDateEdit {
                    padding: 8px 12px;
                    border: 2px solid #A5D6A7;
                    border-radius: 8px;
                    background-color: white;
                    color: #1B5E20;
                    selection-background-color: #4CAF50;
                }
                QLineEdit:focus, QSpinBox:focus, QComboBox:focus, QDateEdit:focus {
                    border-color: #4CAF50;
                    outline: none;
                    background-color: #F1F8E9;
                }
                
                /* SpinBox buttons */
                QSpinBox::up-button, QSpinBox::down-button {
                    background-color: #E8F5E8;
                    border: 1px solid #A5D6A7;
                    width: 16px;
                }
                QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                    background-color: #C8E6C9;
                    border-color: #4CAF50;
                }
                QSpinBox::up-button:pressed, QSpinBox::down-button:pressed {
                    background-color: #A5D6A7;
                }
                
                /* ComboBox dropdown */
                QComboBox::drop-down {
                    background-color: #E8F5E8;
                    border: 1px solid #A5D6A7;
                    width: 20px;
                }
                QComboBox::drop-down:hover {
                    background-color: #C8E6C9;
                    border-color: #4CAF50;
                }
                
                /* Disabled state styling */
                QLineEdit:disabled, QSpinBox:disabled, QComboBox:disabled, QDateEdit:disabled {
                    background-color: #F0F0F0;
                    color: #A5D6A7;
                    border-color: #C8E6C9;
                }
                QSpinBox::up-button:disabled, QSpinBox::down-button:disabled {
                    background-color: #F0F0F0;
                    border-color: #C8E6C9;
                }
                QComboBox::drop-down:disabled {
                    background-color: #F0F0F0;
                    border-color: #C8E6C9;
                }
                QCheckBox:disabled {
                    color: #A5D6A7;
                }
                QCheckBox::indicator:disabled {
                    background-color: #F0F0F0;
                    border-color: #C8E6C9;
                }
                QGroupBox:disabled {
                    color: #A5D6A7;
                    border-color: #C8E6C9;
                    background-color: #F0F8F0;
                }
                QGroupBox::title:disabled {
                    color: #A5D6A7;
                }
                
                /* Table Widget */
                QTableWidget {
                    gridline-color: #A5D6A7;
                    background-color: white;
                    alternate-background-color: #F1F8E9;
                    selection-background-color: #C8E6C9;
                    border: 1px solid #A5D6A7;
                    border-radius: 12px;
                    color: #1B5E20;
                }
                QTableWidget::item {
                    padding: 8px;
                    border: none;
                }
                QTableWidget::item:selected {
                    background-color: #C8E6C9;
                    color: #2E7D32;
                }
                QHeaderView::section {
                    background-color: #E8F5E8;
                    padding: 8px;
                    border: none;
                    border-bottom: 2px solid #4CAF50;
                    font-weight: bold;
                    color: #1B5E20;
                }
                
                /* Progress Bar */
                QProgressBar {
                    border: 2px solid #A5D6A7;
                    border-radius: 10px;
                    text-align: center;
                    background-color: #E8F5E8;
                    color: #1B5E20;
                }
                QProgressBar::chunk {
                    background-color: #4CAF50;
                    border-radius: 8px;
                }
                
                /* Menu Bar */
                QMenuBar {
                    background-color: #E8F5E8;
                    border-bottom: 1px solid #A5D6A7;
                    padding: 4px;
                    color: #1B5E20;
                }
                QMenuBar::item {
                    padding: 8px 12px;
                    border-radius: 6px;
                }
                QMenuBar::item:selected {
                    background-color: #C8E6C9;
                    color: #2E7D32;
                }
                QMenu {
                    background-color: white;
                    border: 1px solid #A5D6A7;
                    border-radius: 10px;
                    padding: 4px;
                    color: #1B5E20;
                }
                QMenu::item {
                    padding: 8px 16px;
                    border-radius: 6px;
                }
                QMenu::item:selected {
                    background-color: #C8E6C9;
                    color: #2E7D32;
                }
                
                /* Status Bar */
                QStatusBar {
                    background-color: #E8F5E8;
                    border-top: 1px solid #A5D6A7;
                    color: #2E7D32;
                }
                
                /* Checkboxes */
                QCheckBox {
                    spacing: 8px;
                    color: #1B5E20;
                }
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                    border: 2px solid #A5D6A7;
                    border-radius: 4px;
                    background-color: white;
                }
                QCheckBox::indicator:checked {
                    background-color: #4CAF50;
                    border-color: #4CAF50;
                    image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1zbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEwIDNMNC41IDguNUwyIDYiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4KPC9zdmc+);
                }
                
                /* Labels */
                QLabel {
                    color: #1B5E20;
                }
                
                /* Scrollbars */
                QScrollBar:vertical {
                    background-color: #E8F5E8;
                    width: 12px;
                    border-radius: 6px;
                }
                QScrollBar::handle:vertical {
                    background-color: #A5D6A7;
                    border-radius: 6px;
                    min-height: 20px;
                }
                QScrollBar::handle:vertical:hover {
                    background-color: #81C784;
                }
            """
        }
    
    def apply_theme(self, theme_name):
        """Apply a theme to the application"""
        if theme_name not in self.themes:
            return False
        
        self.current_theme = theme_name
        theme = self.themes[theme_name]
        
        # Apply stylesheet to application
        app = QApplication.instance()
        if app:
            app.setStyleSheet(theme["stylesheet"])
        
        self.theme_changed.emit(theme_name)
        return True
    
    def get_theme_names(self):
        """Get list of available theme names"""
        return [theme["name"] for theme in self.themes.values()]
    
    def get_current_theme(self):
        """Get current theme configuration"""
        return self.themes[self.current_theme]
    
    def get_color(self, color_name):
        """Get a specific color from current theme"""
        theme = self.get_current_theme()
        return theme["colors"].get(color_name, "#000000")

# Global theme manager instance
theme_manager = ThemeManager()
