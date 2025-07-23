from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QLineEdit, QTextEdit, QTabWidget, QWidget, QTableWidget,
    QTableWidgetItem, QHeaderView, QGroupBox, QFormLayout,
    QMessageBox, QDialogButtonBox, QComboBox, QSpinBox,
    QCheckBox, QDateEdit, QFileDialog
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont
from bookmark_manager import DirectoryBookmark, SearchPreset
import os
from pathlib import Path

class BookmarkDialog(QDialog):
    """Dialog for managing bookmarks and search presets"""
    
    def __init__(self, bookmark_manager, main_window, parent=None):
        super().__init__(parent)
        self.bookmark_manager = bookmark_manager
        self.main_window = main_window
        self.setWindowTitle("Manage Bookmarks")
        self.setModal(True)
        self.resize(800, 600)
        self.setup_ui()
        self.refresh_data()
    
    def setup_ui(self):
        """Set up the user interface"""
        layout = QVBoxLayout(self)
        
        # Create tab widget
        tab_widget = QTabWidget()
        
        # Directory Bookmarks Tab
        bookmarks_tab = QWidget()
        bookmarks_layout = QVBoxLayout(bookmarks_tab)
        
        # Add bookmark section
        add_bookmark_group = QGroupBox("Add New Bookmark")
        add_bookmark_layout = QFormLayout(add_bookmark_group)
        
        self.new_bookmark_name = QLineEdit()
        self.new_bookmark_name.setPlaceholderText("Enter bookmark name...")
        add_bookmark_layout.addRow("Name:", self.new_bookmark_name)
        
        bookmark_path_layout = QHBoxLayout()
        self.new_bookmark_path = QLineEdit()
        self.new_bookmark_path.setPlaceholderText("Enter directory path...")
        browse_bookmark_btn = QPushButton("Browse...")
        browse_bookmark_btn.clicked.connect(self.browse_bookmark_directory)
        bookmark_path_layout.addWidget(self.new_bookmark_path)
        bookmark_path_layout.addWidget(browse_bookmark_btn)
        add_bookmark_layout.addRow("Path:", bookmark_path_layout)
        
        self.new_bookmark_desc = QLineEdit()
        self.new_bookmark_desc.setPlaceholderText("Optional description...")
        add_bookmark_layout.addRow("Description:", self.new_bookmark_desc)
        
        add_bookmark_btn = QPushButton("Add Bookmark")
        add_bookmark_btn.clicked.connect(self.add_bookmark)
        add_bookmark_layout.addRow("", add_bookmark_btn)
        
        bookmarks_layout.addWidget(add_bookmark_group)
        
        # Existing bookmarks table
        bookmarks_group = QGroupBox("Existing Bookmarks")
        bookmarks_group_layout = QVBoxLayout(bookmarks_group)
        
        self.bookmarks_table = QTableWidget()
        self.bookmarks_table.setColumnCount(5)
        self.bookmarks_table.setHorizontalHeaderLabels(["Name", "Path", "Description", "Usage Count", "Last Used"])
        self.bookmarks_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.bookmarks_table.setSelectionBehavior(QTableWidget.SelectRows)
        bookmarks_group_layout.addWidget(self.bookmarks_table)
        
        # Bookmark action buttons
        bookmark_buttons = QHBoxLayout()
        edit_bookmark_btn = QPushButton("Edit Selected")
        edit_bookmark_btn.clicked.connect(self.edit_bookmark)
        remove_bookmark_btn = QPushButton("Remove Selected")
        remove_bookmark_btn.clicked.connect(self.remove_bookmark)
        use_bookmark_btn = QPushButton("Go to Selected")
        use_bookmark_btn.clicked.connect(self.use_bookmark)
        
        bookmark_buttons.addWidget(edit_bookmark_btn)
        bookmark_buttons.addWidget(remove_bookmark_btn)
        bookmark_buttons.addWidget(use_bookmark_btn)
        bookmark_buttons.addStretch()
        bookmarks_group_layout.addLayout(bookmark_buttons)
        
        bookmarks_layout.addWidget(bookmarks_group)
        tab_widget.addTab(bookmarks_tab, "Directory Bookmarks")
        
        # Search Presets Tab
        presets_tab = QWidget()
        presets_layout = QVBoxLayout(presets_tab)
        
        # Current search preset section
        current_preset_group = QGroupBox("Save Current Search")
        current_preset_layout = QFormLayout(current_preset_group)
        
        self.new_preset_name = QLineEdit()
        self.new_preset_name.setPlaceholderText("Enter preset name...")
        current_preset_layout.addRow("Name:", self.new_preset_name)
        
        self.new_preset_desc = QLineEdit()
        self.new_preset_desc.setPlaceholderText("Optional description...")
        current_preset_layout.addRow("Description:", self.new_preset_desc)
        
        save_preset_btn = QPushButton("Save Current Search as Preset")
        save_preset_btn.clicked.connect(self.save_current_search)
        current_preset_layout.addRow("", save_preset_btn)
        
        presets_layout.addWidget(current_preset_group)
        
        # Existing presets table
        presets_group = QGroupBox("Saved Search Presets")
        presets_group_layout = QVBoxLayout(presets_group)
        
        self.presets_table = QTableWidget()
        self.presets_table.setColumnCount(4)
        self.presets_table.setHorizontalHeaderLabels(["Name", "Description", "Configuration", "Last Used"])
        self.presets_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.presets_table.setSelectionBehavior(QTableWidget.SelectRows)
        presets_group_layout.addWidget(self.presets_table)
        
        # Preset action buttons
        preset_buttons = QHBoxLayout()
        load_preset_btn = QPushButton("Load Selected")
        load_preset_btn.clicked.connect(self.load_preset)
        edit_preset_btn = QPushButton("Edit Selected")
        edit_preset_btn.clicked.connect(self.edit_preset)
        remove_preset_btn = QPushButton("Remove Selected")
        remove_preset_btn.clicked.connect(self.remove_preset)
        
        preset_buttons.addWidget(load_preset_btn)
        preset_buttons.addWidget(edit_preset_btn)
        preset_buttons.addWidget(remove_preset_btn)
        preset_buttons.addStretch()
        presets_group_layout.addLayout(preset_buttons)
        
        presets_layout.addWidget(presets_group)
        tab_widget.addTab(presets_tab, "Search Presets")
        
        layout.addWidget(tab_widget)
        
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.accept)
        layout.addWidget(button_box)
    
    def browse_bookmark_directory(self):
        """Browse for directory to bookmark"""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Directory to Bookmark", 
            self.main_window.current_directory
        )
        if directory:
            self.new_bookmark_path.setText(directory)
            # Auto-generate name from directory
            if not self.new_bookmark_name.text():
                self.new_bookmark_name.setText(Path(directory).name)
    
    def add_bookmark(self):
        """Add a new directory bookmark"""
        name = self.new_bookmark_name.text().strip()
        path = self.new_bookmark_path.text().strip()
        description = self.new_bookmark_desc.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Missing Name", "Please enter a bookmark name.")
            return
        
        if not path or not os.path.exists(path):
            QMessageBox.warning(self, "Invalid Path", "Please enter a valid directory path.")
            return
        
        if self.bookmark_manager.add_bookmark(name, path, description):
            QMessageBox.information(self, "Bookmark Added", f"Successfully added bookmark '{name}'")
            self.new_bookmark_name.clear()
            self.new_bookmark_path.clear()
            self.new_bookmark_desc.clear()
            self.refresh_bookmarks()
        else:
            QMessageBox.warning(self, "Duplicate Bookmark", "A bookmark for this directory already exists.")
    
    def edit_bookmark(self):
        """Edit selected bookmark"""
        selected_row = self.bookmarks_table.currentRow()
        if selected_row < 0:
            QMessageBox.information(self, "No Selection", "Please select a bookmark to edit.")
            return
        
        bookmarks = self.bookmark_manager.get_bookmarks()
        if selected_row >= len(bookmarks):
            return
        
        bookmark = bookmarks[selected_row]
        
        # Create comprehensive edit dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Bookmark")
        dialog.setModal(True)
        dialog.resize(500, 200)
        layout = QFormLayout(dialog)
        
        # Name field
        name_edit = QLineEdit(bookmark.name)
        layout.addRow("Name:", name_edit)
        
        # Path field with browse button
        path_layout = QHBoxLayout()
        path_edit = QLineEdit(bookmark.path)
        browse_btn = QPushButton("Browse...")
        
        def browse_new_path():
            directory = QFileDialog.getExistingDirectory(
                dialog, "Select New Directory", bookmark.path
            )
            if directory:
                path_edit.setText(directory)
        
        browse_btn.clicked.connect(browse_new_path)
        path_layout.addWidget(path_edit)
        path_layout.addWidget(browse_btn)
        layout.addRow("Path:", path_layout)
        
        # Description field
        desc_edit = QLineEdit(bookmark.description)
        layout.addRow("Description:", desc_edit)
        
        # Dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec():
            new_name = name_edit.text().strip()
            new_path = path_edit.text().strip()
            new_description = desc_edit.text().strip()
            
            # Validate inputs
            if not new_name:
                QMessageBox.warning(self, "Invalid Name", "Please enter a bookmark name.")
                return
            
            if not new_path or not os.path.exists(new_path):
                QMessageBox.warning(self, "Invalid Path", "Please enter a valid directory path.")
                return
            
            # Check if new path conflicts with existing bookmarks (excluding current one)
            if new_path != bookmark.path and any(b.path == new_path for b in self.bookmark_manager.bookmarks):
                QMessageBox.warning(self, "Duplicate Path", "A bookmark for this directory already exists.")
                return
            
            # Update the bookmark
            # Remove old bookmark
            self.bookmark_manager.remove_bookmark(bookmark.path)
            # Add updated bookmark (preserving usage stats)
            updated_bookmark = DirectoryBookmark(
                name=new_name,
                path=new_path,
                description=new_description,
                created_at=bookmark.created_at,
                last_used=bookmark.last_used,
                usage_count=bookmark.usage_count
            )
            self.bookmark_manager.bookmarks.append(updated_bookmark)
            self.bookmark_manager.save_bookmarks()
            
            self.refresh_bookmarks()
            QMessageBox.information(self, "Bookmark Updated", f"Successfully updated bookmark '{new_name}'")
    
    def remove_bookmark(self):
        """Remove selected bookmark"""
        selected_row = self.bookmarks_table.currentRow()
        if selected_row < 0:
            QMessageBox.information(self, "No Selection", "Please select a bookmark to remove.")
            return
        
        bookmarks = self.bookmark_manager.get_bookmarks()
        if selected_row >= len(bookmarks):
            return
        
        bookmark = bookmarks[selected_row]
        
        confirm = QMessageBox.question(
            self, "Confirm Removal",
            f"Are you sure you want to remove the bookmark '{bookmark.name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            self.bookmark_manager.remove_bookmark(bookmark.path)
            self.refresh_bookmarks()
    
    def use_bookmark(self):
        """Navigate to selected bookmark"""
        selected_row = self.bookmarks_table.currentRow()
        if selected_row < 0:
            QMessageBox.information(self, "No Selection", "Please select a bookmark to use.")
            return
        
        bookmarks = self.bookmark_manager.get_bookmarks()
        if selected_row >= len(bookmarks):
            return
        
        bookmark = bookmarks[selected_row]
        
        # Set the directory in main window
        self.main_window.path_edit.setText(bookmark.path)
        self.main_window.current_directory = bookmark.path
        
        # Update usage stats
        self.bookmark_manager.use_bookmark(bookmark.path)
        
        QMessageBox.information(self, "Bookmark Applied", f"Directory set to: {bookmark.path}")
        self.accept()  # Close the dialog
    
    def save_current_search(self):
        """Save current search configuration as preset"""
        name = self.new_preset_name.text().strip()
        description = self.new_preset_desc.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Missing Name", "Please enter a preset name.")
            return
        
        # Get current search configuration from main window
        search_config = self.get_current_search_config()
        
        if self.bookmark_manager.add_preset(name, search_config, description):
            QMessageBox.information(self, "Preset Saved", f"Successfully saved preset '{name}'")
            self.new_preset_name.clear()
            self.new_preset_desc.clear()
            self.refresh_presets()
        else:
            QMessageBox.warning(self, "Duplicate Preset", "A preset with this name already exists.")
    
    def get_current_search_config(self):
        """Extract current search configuration from main window"""
        mw = self.main_window
        
        # Get advanced filter settings
        advanced_filters = mw.get_advanced_filters()
        
        return {
            "category": mw.category_combo.currentText(),
            "min_size": mw.min_size.value(),
            "max_size": mw.max_size.value(),
            "max_depth": mw.max_depth.value(),
            "date_filter_enabled": mw.date_filter_enabled.isChecked(),
            "date_from": mw.date_from.date().toString("yyyy-MM-dd") if mw.date_filter_enabled.isChecked() else None,
            "date_to": mw.date_to.date().toString("yyyy-MM-dd") if mw.date_filter_enabled.isChecked() else None,
            "pattern_filter_enabled": mw.pattern_filter_enabled.isChecked(),
            "filename_pattern": mw.pattern_edit.text(),
            "content_filter_enabled": mw.content_filter_enabled.isChecked(),
            "content_search": mw.content_edit.text()
        }
    
    def load_preset(self):
        """Load selected search preset"""
        selected_row = self.presets_table.currentRow()
        if selected_row < 0:
            QMessageBox.information(self, "No Selection", "Please select a preset to load.")
            return
        
        presets = self.bookmark_manager.get_presets()
        if selected_row >= len(presets):
            return
        
        preset = presets[selected_row]
        self.apply_preset_to_ui(preset)
        self.bookmark_manager.use_preset(preset.name)
        
        QMessageBox.information(self, "Preset Loaded", f"Applied search preset '{preset.name}'")
        self.accept()  # Close the dialog
    
    def apply_preset_to_ui(self, preset: SearchPreset):
        """Apply preset configuration to main window UI"""
        mw = self.main_window
        
        # Set basic filters
        category_index = mw.category_combo.findText(preset.category)
        if category_index >= 0:
            mw.category_combo.setCurrentIndex(category_index)
        
        mw.min_size.setValue(preset.min_size)
        mw.max_size.setValue(preset.max_size)
        mw.max_depth.setValue(preset.max_depth)
        
        # Set advanced filters
        mw.date_filter_enabled.setChecked(preset.date_filter_enabled)
        if preset.date_from:
            mw.date_from.setDate(QDate.fromString(preset.date_from, "yyyy-MM-dd"))
        if preset.date_to:
            mw.date_to.setDate(QDate.fromString(preset.date_to, "yyyy-MM-dd"))
        
        mw.pattern_filter_enabled.setChecked(preset.pattern_filter_enabled)
        mw.pattern_edit.setText(preset.filename_pattern or "")
        
        mw.content_filter_enabled.setChecked(preset.content_filter_enabled)
        mw.content_edit.setText(preset.content_search or "")
        
        # Update filter control states
        mw.toggle_date_filter(preset.date_filter_enabled)
        mw.toggle_pattern_filter(preset.pattern_filter_enabled)
        mw.toggle_content_filter(preset.content_filter_enabled)
    
    def edit_preset(self):
        """Edit selected preset with full configuration dialog"""
        selected_row = self.presets_table.currentRow()
        if selected_row < 0:
            QMessageBox.information(self, "No Selection", "Please select a preset to edit.")
            return
        
        presets = self.bookmark_manager.get_presets()
        if selected_row >= len(presets):
            return
        
        preset = presets[selected_row]
        
        # Create comprehensive edit dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Search Preset")
        dialog.setModal(True)
        dialog.resize(600, 500)
        layout = QVBoxLayout(dialog)
        
        # Basic preset info
        basic_group = QGroupBox("Preset Information")
        basic_layout = QFormLayout(basic_group)
        
        name_edit = QLineEdit(preset.name)
        basic_layout.addRow("Name:", name_edit)
        
        desc_edit = QLineEdit(preset.description)
        desc_edit.setPlaceholderText("Optional description...")
        basic_layout.addRow("Description:", desc_edit)
        
        layout.addWidget(basic_group)
        
        # Search configuration
        search_group = QGroupBox("Search Configuration")
        search_layout = QFormLayout(search_group)
        
        # Category selection
        category_combo = QComboBox()
        category_combo.addItem("All Files")
        for category in self.main_window.categories:
            category_combo.addItem(category.name)
        
        # Set current category
        category_index = category_combo.findText(preset.category)
        if category_index >= 0:
            category_combo.setCurrentIndex(category_index)
        
        search_layout.addRow("File Type:", category_combo)
        
        # Size filters
        size_layout = QHBoxLayout()
        min_size_spin = QSpinBox()
        min_size_spin.setRange(0, 10000)
        min_size_spin.setValue(preset.min_size)
        min_size_spin.setSuffix(" MB")
        
        max_size_spin = QSpinBox()
        max_size_spin.setRange(0, 100000)
        max_size_spin.setValue(preset.max_size)
        max_size_spin.setSuffix(" MB")
        max_size_spin.setSpecialValueText("No Limit")
        
        size_layout.addWidget(min_size_spin)
        size_layout.addWidget(QLabel("to"))
        size_layout.addWidget(max_size_spin)
        size_layout.addStretch()
        search_layout.addRow("Size Range:", size_layout)
        
        # Max depth
        max_depth_spin = QSpinBox()
        max_depth_spin.setRange(1, 100)
        max_depth_spin.setValue(preset.max_depth)
        search_layout.addRow("Max Depth:", max_depth_spin)
        
        layout.addWidget(search_group)
        
        # Advanced filters
        advanced_group = QGroupBox("Advanced Filters")
        advanced_layout = QVBoxLayout(advanced_group)
        
        # Date filter
        date_layout = QHBoxLayout()
        date_filter_check = QCheckBox("Filter by date range")
        date_filter_check.setChecked(preset.date_filter_enabled)
        date_layout.addWidget(date_filter_check)
        
        date_layout.addWidget(QLabel("From:"))
        date_from_edit = QDateEdit()
        if preset.date_from:
            date_from_edit.setDate(QDate.fromString(preset.date_from, "yyyy-MM-dd"))
        else:
            date_from_edit.setDate(QDate.currentDate().addDays(-30))
        date_from_edit.setCalendarPopup(True)
        date_from_edit.setEnabled(preset.date_filter_enabled)
        date_layout.addWidget(date_from_edit)
        
        date_layout.addWidget(QLabel("To:"))
        date_to_edit = QDateEdit()
        if preset.date_to:
            date_to_edit.setDate(QDate.fromString(preset.date_to, "yyyy-MM-dd"))
        else:
            date_to_edit.setDate(QDate.currentDate())
        date_to_edit.setCalendarPopup(True)
        date_to_edit.setEnabled(preset.date_filter_enabled)
        date_layout.addWidget(date_to_edit)
        date_layout.addStretch()
        advanced_layout.addLayout(date_layout)
        
        # Enable/disable date controls based on checkbox
        def toggle_date_controls(enabled):
            date_from_edit.setEnabled(enabled)
            date_to_edit.setEnabled(enabled)
        
        date_filter_check.toggled.connect(toggle_date_controls)
        
        # Pattern filter
        pattern_layout = QHBoxLayout()
        pattern_filter_check = QCheckBox("Filename pattern (regex)")
        pattern_filter_check.setChecked(preset.pattern_filter_enabled)
        pattern_layout.addWidget(pattern_filter_check)
        
        pattern_edit = QLineEdit(preset.filename_pattern)
        pattern_edit.setPlaceholderText("e.g., IMG_\\d{4}, .*\\.backup\\..*, ^test.*\\.py$")
        pattern_edit.setEnabled(preset.pattern_filter_enabled)
        pattern_layout.addWidget(pattern_edit)
        
        pattern_filter_check.toggled.connect(pattern_edit.setEnabled)
        advanced_layout.addLayout(pattern_layout)
        
        # Content filter
        content_layout = QHBoxLayout()
        content_filter_check = QCheckBox("Content search (text files only)")
        content_filter_check.setChecked(preset.content_filter_enabled)
        content_layout.addWidget(content_filter_check)
        
        content_edit = QLineEdit(preset.content_search)
        content_edit.setPlaceholderText("Search for text within files...")
        content_edit.setEnabled(preset.content_filter_enabled)
        content_layout.addWidget(content_edit)
        
        content_filter_check.toggled.connect(content_edit.setEnabled)
        advanced_layout.addLayout(content_layout)
        
        layout.addWidget(advanced_group)
        
        # Dialog buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save Changes")
        cancel_btn = QPushButton("Cancel")
        
        save_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        if dialog.exec():
            new_name = name_edit.text().strip()
            new_description = desc_edit.text().strip()
            
            if not new_name:
                QMessageBox.warning(self, "Invalid Name", "Please enter a preset name.")
                return
            
            # Check for name conflicts (excluding current preset)
            if new_name != preset.name and any(p.name == new_name for p in self.bookmark_manager.presets):
                QMessageBox.warning(self, "Duplicate Name", "A preset with this name already exists.")
                return
            
            # Create updated search configuration
            updated_config = {
                "category": category_combo.currentText(),
                "min_size": min_size_spin.value(),
                "max_size": max_size_spin.value(),
                "max_depth": max_depth_spin.value(),
                "date_filter_enabled": date_filter_check.isChecked(),
                "date_from": date_from_edit.date().toString("yyyy-MM-dd") if date_filter_check.isChecked() else None,
                "date_to": date_to_edit.date().toString("yyyy-MM-dd") if date_filter_check.isChecked() else None,
                "pattern_filter_enabled": pattern_filter_check.isChecked(),
                "filename_pattern": pattern_edit.text().strip(),
                "content_filter_enabled": content_filter_check.isChecked(),
                "content_search": content_edit.text().strip()
            }
            
            # Update the preset using the new method
            success = self.bookmark_manager.update_preset_full(
                preset.name, new_name, updated_config, new_description
            )
            
            if success:
                self.refresh_presets()
                QMessageBox.information(self, "Preset Updated", f"Successfully updated preset '{new_name}'")
            else:
                QMessageBox.warning(self, "Update Failed", "Failed to update preset. There may be a naming conflict.")
    
    def remove_preset(self):
        """Remove selected preset"""
        selected_row = self.presets_table.currentRow()
        if selected_row < 0:
            QMessageBox.information(self, "No Selection", "Please select a preset to remove.")
            return
        
        presets = self.bookmark_manager.get_presets()
        if selected_row >= len(presets):
            return
        
        preset = presets[selected_row]
        
        confirm = QMessageBox.question(
            self, "Confirm Removal",
            f"Are you sure you want to remove the preset '{preset.name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            self.bookmark_manager.remove_preset(preset.name)
            self.refresh_presets()

    def refresh_data(self):
        """Refresh both bookmarks and presets"""
        self.refresh_bookmarks()
        self.refresh_presets()
    
    def refresh_bookmarks(self):
        """Refresh the bookmarks table"""
        bookmarks = self.bookmark_manager.get_bookmarks()
        self.bookmarks_table.setRowCount(len(bookmarks))
        
        for row, bookmark in enumerate(bookmarks):
            self.bookmarks_table.setItem(row, 0, QTableWidgetItem(bookmark.name))
            self.bookmarks_table.setItem(row, 1, QTableWidgetItem(bookmark.path))
            self.bookmarks_table.setItem(row, 2, QTableWidgetItem(bookmark.description or ""))
            self.bookmarks_table.setItem(row, 3, QTableWidgetItem(str(bookmark.usage_count)))
            
            last_used = "Never"
            if bookmark.last_used:
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(bookmark.last_used)
                    last_used = dt.strftime("%Y-%m-%d %H:%M")
                except:
                    last_used = "Unknown"
            
            self.bookmarks_table.setItem(row, 4, QTableWidgetItem(last_used))
    
    def refresh_presets(self):
        """Refresh the presets table"""
        presets = self.bookmark_manager.get_presets()
        self.presets_table.setRowCount(len(presets))
        
        for row, preset in enumerate(presets):
            self.presets_table.setItem(row, 0, QTableWidgetItem(preset.name))
            self.presets_table.setItem(row, 1, QTableWidgetItem(preset.description or ""))
            
            # Create configuration summary
            config_parts = []
            if preset.category != "All Files":
                config_parts.append(f"Type: {preset.category}")
            if preset.min_size > 0:
                config_parts.append(f"Min: {preset.min_size}MB")
            if preset.max_size > 0:
                config_parts.append(f"Max: {preset.max_size}MB")
            if preset.date_filter_enabled:
                config_parts.append("Date filter")
            if preset.pattern_filter_enabled:
                config_parts.append("Pattern filter")
            if preset.content_filter_enabled:
                config_parts.append("Content search")
            
            config_summary = ", ".join(config_parts) if config_parts else "Default settings"
            self.presets_table.setItem(row, 2, QTableWidgetItem(config_summary))
            
            last_used = "Never"
            if preset.last_used:
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(preset.last_used)
                    last_used = dt.strftime("%Y-%m-%d %H:%M")
                except:
                    last_used = "Unknown"
            
            self.presets_table.setItem(row, 3, QTableWidgetItem(last_used))
