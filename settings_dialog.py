from PySide6.QtWidgets import (QDialog, QVBoxLayout, QTabWidget, QWidget, QHBoxLayout,
                              QPushButton, QCheckBox, QGroupBox, QFormLayout, QSpinBox,
                              QTableWidget, QTableWidgetItem, QHeaderView, QDialogButtonBox,
                              QMessageBox)
from PySide6.QtGui import QColor, QFont

from category_dialog import CategoryDialog

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
        
        # Categories tab
        tab_widget = QTabWidget()
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
        
        # General settings tab
        general_widget = QWidget()
        general_layout = QVBoxLayout(general_widget)
        
        # Auto-discover extensions
        self.auto_discover = QCheckBox("Auto-discover and suggest new file extensions")
        self.auto_discover.setChecked(self.app_settings.get("auto_discover", True))
        general_layout.addWidget(self.auto_discover)
        
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
        
        layout.addWidget(tab_widget)
        
        # Dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setMinimumSize(500, 400)
    
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
        
        # First collect all the settings data
        self.app_settings = {
            "auto_discover": self.auto_discover.isChecked(),
            "default_min_size": self.default_min_size.value(),
            "default_max_depth": self.default_max_depth.value(),
        }
        
        # Close the dialog to prevent UI freezing
        super().accept()

