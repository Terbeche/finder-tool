from PySide6.QtWidgets import (QDialog, QVBoxLayout, QTabWidget, QWidget, QHBoxLayout,
                              QPushButton, QCheckBox, QGroupBox, QFormLayout, QSpinBox,
                              QTableWidget, QTableWidgetItem, QHeaderView, QDialogButtonBox,
                              QMessageBox, QComboBox, QLabel)
from PySide6.QtGui import QColor, QFont

from dialogs.category_dialog import CategoryDialog
from services.theme_manager import theme_manager

class SettingsDialog(QDialog):
    """Dialog for application settings"""
    def __init__(self, categories, parent=None):
        super().__init__(parent)
        self.categories = categories.copy()  # Work with a copy
        self.setWindowTitle("Settings")
        
        # Reference to main window
        self.main_window = parent
        self.app_settings = self.main_window.app_settings.copy() if hasattr(self.main_window, 'app_settings') else {}
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        tab_widget = QTabWidget()
        
        # General settings tab
        general_widget = QWidget()
        general_layout = QVBoxLayout(general_widget)
        
        # Theme selection
        theme_group = QGroupBox("Appearance")
        theme_layout = QFormLayout(theme_group)
        
        self.theme_combo = QComboBox()
        theme_names = theme_manager.get_theme_names()
        self.theme_combo.addItems(theme_names)
        
        # Set current theme
        current_theme = self.app_settings.get("theme", "Light")
        index = self.theme_combo.findText(current_theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
        
        # Connect theme change
        self.theme_combo.currentTextChanged.connect(self.preview_theme)
        
        theme_layout.addRow("Theme:", self.theme_combo)
        
        # Theme preview
        self.theme_preview = QLabel("Select a theme to see the changes applied immediately")
        self.theme_preview.setWordWrap(True)
        theme_layout.addRow("Preview:", self.theme_preview)
        
        general_layout.addWidget(theme_group)
        
        # Auto-discover extensions
        discovery_group = QGroupBox("File Discovery")
        discovery_layout = QVBoxLayout(discovery_group)
        
        self.auto_discover = QCheckBox("Auto-discover and suggest new file extensions")
        self.auto_discover.setChecked(self.app_settings.get("auto_discover", True))
        discovery_layout.addWidget(self.auto_discover)
        
        general_layout.addWidget(discovery_group)
        
        # Default scan settings
        scan_group = QGroupBox("Default Scan Settings")
        scan_layout = QFormLayout(scan_group)

        self.default_min_size = QSpinBox()
        self.default_min_size.setRange(0, 10000)
        self.default_min_size.setValue(self.app_settings.get("default_min_size", 0))
        self.default_min_size.setSuffix(" MB")
        scan_layout.addRow("Default Minimum Size:", self.default_min_size)
        
        self.default_max_depth = QSpinBox()
        self.default_max_depth.setRange(1, 100)
        self.default_max_depth.setValue(self.app_settings.get("default_max_depth", 15))
        scan_layout.addRow("Default Maximum Depth:", self.default_max_depth)
        
        general_layout.addWidget(scan_group)
        general_layout.addStretch()
        
        tab_widget.addTab(general_widget, "General")
        
        # Categories tab
        categories_widget = QWidget()
        categories_layout = QVBoxLayout(categories_widget)

        # List of categories
        self.categories_table = QTableWidget()
        self.categories_table.setColumnCount(3)
        self.categories_table.setHorizontalHeaderLabels(["Name", "Extensions", "Color"])
        self.categories_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.update_categories_table()
        
        categories_layout.addWidget(self.categories_table)
        
        # Buttons for category management
        buttons_layout = QHBoxLayout()
        add_button = QPushButton("Add Category")
        add_button.clicked.connect(self.add_category)
        edit_button = QPushButton("Edit Selected")
        edit_button.clicked.connect(self.edit_category)
        remove_button = QPushButton("Remove Selected")
        remove_button.clicked.connect(self.remove_category)
        
        buttons_layout.addWidget(add_button)
        buttons_layout.addWidget(edit_button)
        buttons_layout.addWidget(remove_button)
        categories_layout.addLayout(buttons_layout)
        
        tab_widget.addTab(categories_widget, "File Categories")
        
        layout.addWidget(tab_widget)
        
        # Dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setMinimumSize(600, 500)
    
    def preview_theme(self, theme_name):
        """Preview theme changes immediately"""
        # Map display names to internal names
        theme_map = {
            "Light": "light",
            "Dark": "dark", 
            "Nature": "nature",
            "Blue": "pro_blue",
            "Midnight": "midnight"
        }
        
        internal_name = theme_map.get(theme_name, "light")
        theme_manager.apply_theme(internal_name)
        
        # Update preview text
        theme_descriptions = {
            "Light": "Clean and bright interface with blue accents",
            "Dark": "Easy on the eyes with purple highlights",
            "Nature": "Relaxing green theme inspired by nature",
            "Blue": "Corporate blue theme for a professional look",
            "Midnight": "Deep indigo theme with cyan accents"
        }
        
        description = theme_descriptions.get(theme_name, "Theme preview")
        self.theme_preview.setText(f"✨ {description}")
    
    def update_categories_table(self):
        """Update the categories table with current data"""
        self.categories_table.setRowCount(len(self.categories))
        
        for row, category in enumerate(self.categories):
            # Name
            name_item = QTableWidgetItem(category.name)
            self.categories_table.setItem(row, 0, name_item)
            
            # Extensions
            extensions_item = QTableWidgetItem(", ".join(category.extensions))
            self.categories_table.setItem(row, 1, extensions_item)
            
            # Color (just text for now)
            color_item = QTableWidgetItem("█████")
            color_item.setForeground(QColor(category.color))
            color_item.setFont(QFont("Arial", 10, QFont.Bold))
            self.categories_table.setItem(row, 2, color_item)
    
    def add_category(self):
        """Add a new category - using the proper dialog pattern"""
        dialog = CategoryDialog(parent=self)
        if dialog.exec():
            new_category = dialog.get_category()  # Get data after dialog is closed
            self.categories.append(new_category)
            self.update_categories_table()
    
    def edit_category(self):
        """Edit selected category - using the proper dialog pattern"""
        selected_rows = self.categories_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.information(self, "No Selection", "Please select a category to edit.")
            return
            
        row = selected_rows[0].row()
        dialog = CategoryDialog(self.categories[row], parent=self)
        if dialog.exec():
            new_category = dialog.get_category()  # Get data after dialog is closed
            self.categories[row] = new_category
            self.update_categories_table()
    
    def remove_category(self):
        """Remove selected category"""
        selected_rows = self.categories_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.information(self, "No Selection", "Please select a category to remove.")
            return
            
        row = selected_rows[0].row()
        confirm = QMessageBox.question(
            self, "Confirm Deletion", 
            f"Are you sure you want to delete the category '{self.categories[row].name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            self.categories.pop(row)
            self.update_categories_table()
    
    def accept(self):
        """Handle dialog acceptance"""
        # Disable the OK button to prevent multiple clicks
        self.findChild(QDialogButtonBox).button(QDialogButtonBox.Ok).setEnabled(False)
        
        # Map display names to internal names for saving
        theme_map = {
            "Light": "light",
            "Dark": "dark", 
            "Nature": "nature",
            "Blue": "pro_blue",
            "Midnight": "midnight"
        }
        
        selected_theme = self.theme_combo.currentText()
        internal_theme = theme_map.get(selected_theme, "light")
        
        # First collect all the settings data
        self.app_settings = {
            "auto_discover": self.auto_discover.isChecked(),
            "default_min_size": self.default_min_size.value(),
            "default_max_depth": self.default_max_depth.value(),
            "theme": selected_theme,  # Store display name
            "theme_internal": internal_theme,  # Store internal name
        }
        
        # Close the dialog to prevent UI freezing
        super().accept()
    
    def reject(self):
        """Handle dialog rejection - restore original theme"""
        # Restore original theme
        original_theme = self.main_window.app_settings.get("theme_internal", "light")
        theme_manager.apply_theme(original_theme)
        super().reject()
        super().accept()
    
    def reject(self):
        """Handle dialog rejection - restore original theme"""
        # Restore original theme
        original_theme = self.main_window.app_settings.get("theme_internal", "light")
        theme_manager.apply_theme(original_theme)
        super().reject()

