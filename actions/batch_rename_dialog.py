from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QLineEdit, QComboBox, QSpinBox, QCheckBox, QGroupBox,
    QFormLayout, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QProgressDialog, QDialogButtonBox, QTabWidget,
    QWidget, QTextEdit
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import re
import os
import shutil
from pathlib import Path


class BatchRenameDialog(QDialog):
    """Dialog for batch renaming files"""
    
    def __init__(self, files, parent=None):
        super().__init__(parent)
        self.files = files
        self.setWindowTitle("Batch Rename Files")
        self.setModal(True)
        self.resize(800, 600)
        self.setup_ui()
        self.update_preview()
    
    def setup_ui(self):
        """Set up the user interface"""
        layout = QVBoxLayout(self)
        
        # Create tab widget for different rename methods
        tab_widget = QTabWidget()
        
        # Pattern Replace Tab
        pattern_tab = QWidget()
        pattern_layout = QVBoxLayout(pattern_tab)
        
        # Find and Replace
        find_replace_group = QGroupBox("Find and Replace")
        find_replace_layout = QFormLayout(find_replace_group)
        
        self.find_text = QLineEdit()
        self.find_text.setPlaceholderText("Text to find...")
        self.find_text.textChanged.connect(self.update_preview)
        find_replace_layout.addRow("Find:", self.find_text)
        
        self.replace_text = QLineEdit()
        self.replace_text.setPlaceholderText("Replace with...")
        self.replace_text.textChanged.connect(self.update_preview)
        find_replace_layout.addRow("Replace:", self.replace_text)
        
        self.case_sensitive = QCheckBox("Case sensitive")
        self.case_sensitive.toggled.connect(self.update_preview)
        find_replace_layout.addRow("", self.case_sensitive)
        
        pattern_layout.addWidget(find_replace_group)
        
        # Numbering
        numbering_group = QGroupBox("Add Numbering")
        numbering_layout = QFormLayout(numbering_group)
        
        self.add_numbering = QCheckBox("Add numbers to filenames")
        self.add_numbering.toggled.connect(self.update_preview)
        numbering_layout.addRow("", self.add_numbering)
        
        self.number_position = QComboBox()
        self.number_position.addItems(["Before filename", "After filename", "Before extension"])
        self.number_position.currentTextChanged.connect(self.update_preview)
        numbering_layout.addRow("Position:", self.number_position)
        
        self.start_number = QSpinBox()
        self.start_number.setRange(0, 9999)
        self.start_number.setValue(1)
        self.start_number.valueChanged.connect(self.update_preview)
        numbering_layout.addRow("Start from:", self.start_number)
        
        self.number_padding = QSpinBox()
        self.number_padding.setRange(1, 6)
        self.number_padding.setValue(2)
        self.number_padding.valueChanged.connect(self.update_preview)
        numbering_layout.addRow("Zero padding:", self.number_padding)
        
        pattern_layout.addWidget(numbering_group)
        
        tab_widget.addTab(pattern_tab, "Find & Replace")
        
        # Case Change Tab
        case_tab = QWidget()
        case_layout = QVBoxLayout(case_tab)
        
        case_group = QGroupBox("Change Case")
        case_group_layout = QVBoxLayout(case_group)
        
        self.case_option = QComboBox()
        self.case_option.addItems([
            "No change",
            "UPPERCASE",
            "lowercase", 
            "Title Case",
            "Sentence case"
        ])
        self.case_option.currentTextChanged.connect(self.update_preview)
        case_group_layout.addWidget(QLabel("Apply to:"))
        case_group_layout.addWidget(self.case_option)
        
        case_layout.addWidget(case_group)
        case_layout.addStretch()
        
        tab_widget.addTab(case_tab, "Case Change")
        
        layout.addWidget(tab_widget)
        
        # Preview section
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_table = QTableWidget()
        self.preview_table.setColumnCount(2)
        self.preview_table.setHorizontalHeaderLabels(["Original Name", "New Name"])
        self.preview_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.preview_table.setMaximumHeight(200)
        preview_layout.addWidget(self.preview_table)
        
        # Status label
        self.status_label = QLabel("")
        preview_layout.addWidget(self.status_label)
        
        layout.addWidget(preview_group)
        
        # Dialog buttons
        button_layout = QHBoxLayout()
        
        self.rename_button = QPushButton("Rename Files")
        self.rename_button.clicked.connect(self.perform_rename)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.rename_button)
        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
    
    def update_preview(self):
        """Update the preview table with renamed files"""
        new_names = []
        conflicts = []
        
        for i, file_info in enumerate(self.files):
            original_name = file_info.name
            new_name = self.generate_new_name(file_info, i)
            
            # Check for conflicts
            if new_name in new_names:
                conflicts.append(new_name)
            
            new_names.append(new_name)
        
        # Update preview table
        self.preview_table.setRowCount(min(len(self.files), 20))  # Show max 20 items
        
        for i in range(min(len(self.files), 20)):
            original_item = QTableWidgetItem(self.files[i].name)
            new_item = QTableWidgetItem(new_names[i])
            
            # Highlight conflicts
            if new_names[i] in conflicts:
                new_item.setBackground(Qt.red)
                new_item.setForeground(Qt.white)
            elif new_names[i] != self.files[i].name:
                new_item.setBackground(Qt.green)
                new_item.setForeground(Qt.white)
            
            self.preview_table.setItem(i, 0, original_item)
            self.preview_table.setItem(i, 1, new_item)
        
        # Update status
        changed_count = sum(1 for i, name in enumerate(new_names) if name != self.files[i].name)
        conflict_count = len(set(conflicts))
        
        if len(self.files) > 20:
            status_text = f"Showing 20 of {len(self.files)} files. "
        else:
            status_text = ""
        
        status_text += f"{changed_count} files will be renamed"
        
        if conflict_count > 0:
            status_text += f", {conflict_count} conflicts detected"
            self.rename_button.setEnabled(False)
        else:
            self.rename_button.setEnabled(changed_count > 0)
        
        self.status_label.setText(status_text)
    
    def generate_new_name(self, file_info, index):
        """Generate new name for a file based on current settings"""
        name_without_ext = Path(file_info.name).stem
        extension = Path(file_info.name).suffix
        
        new_name = name_without_ext
        
        # Apply find and replace
        if self.find_text.text():
            if self.case_sensitive.isChecked():
                new_name = new_name.replace(self.find_text.text(), self.replace_text.text())
            else:
                # Case insensitive replace
                find_text = self.find_text.text().lower()
                replace_text = self.replace_text.text()
                name_lower = new_name.lower()
                
                result = []
                start = 0
                while True:
                    pos = name_lower.find(find_text, start)
                    if pos == -1:
                        result.append(new_name[start:])
                        break
                    result.append(new_name[start:pos])
                    result.append(replace_text)
                    start = pos + len(find_text)
                new_name = ''.join(result)
        
        # Apply case change
        case_option = self.case_option.currentText()
        if case_option == "UPPERCASE":
            new_name = new_name.upper()
        elif case_option == "lowercase":
            new_name = new_name.lower()
        elif case_option == "Title Case":
            new_name = new_name.title()
        elif case_option == "Sentence case":
            new_name = new_name.capitalize()
        
        # Add numbering
        if self.add_numbering.isChecked():
            number = self.start_number.value() + index
            number_str = str(number).zfill(self.number_padding.value())
            
            position = self.number_position.currentText()
            if position == "Before filename":
                new_name = f"{number_str}_{new_name}"
            elif position == "After filename":
                new_name = f"{new_name}_{number_str}"
            elif position == "Before extension":
                new_name = f"{new_name}_{number_str}"
        
        return new_name + extension
    
    def perform_rename(self):
        """Perform the actual file renaming"""
        # Generate all new names
        new_names = []
        for i, file_info in enumerate(self.files):
            new_name = self.generate_new_name(file_info, i)
            new_names.append(new_name)
        
        # Check for conflicts one more time
        if len(set(new_names)) != len(new_names):
            QMessageBox.warning(self, "Naming Conflicts", 
                              "There are naming conflicts. Please adjust your settings.")
            return
        
        # Confirm operation
        changed_count = sum(1 for i, name in enumerate(new_names) if name != self.files[i].name)
        
        confirm = QMessageBox.question(
            self, "Confirm Batch Rename",
            f"Rename {changed_count} files?\n\nThis operation cannot be undone.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm != QMessageBox.Yes:
            return
        
        # Create progress dialog
        progress = QProgressDialog("Renaming files...", "Cancel", 0, changed_count, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.show()
        
        renamed_count = 0
        failed_renames = []
        
        for i, file_info in enumerate(self.files):
            new_name = new_names[i]
            
            if new_name == file_info.name:
                continue  # Skip files that don't need renaming
            
            if progress.wasCanceled():
                break
            
            progress.setValue(renamed_count)
            progress.setLabelText(f"Renaming: {file_info.name}")
            
            try:
                old_path = Path(file_info.path)
                new_path = old_path.parent / new_name
                
                # Rename the file
                old_path.rename(new_path)
                
                # Update file info
                file_info.name = new_name
                file_info.path = str(new_path)
                
                renamed_count += 1
                
            except Exception as e:
                failed_renames.append((file_info.name, str(e)))
        
        progress.close()
        
        # Show results
        if failed_renames:
            failed_list = "\n".join([f"• {name}: {error}" for name, error in failed_renames[:10]])
            if len(failed_renames) > 10:
                failed_list += f"\n... and {len(failed_renames) - 10} more"
            
            QMessageBox.warning(
                self, "Rename Results",
                f"Successfully renamed {renamed_count} files.\n"
                f"Failed to rename {len(failed_renames)} files:\n\n{failed_list}"
            )
        else:
            QMessageBox.information(
                self, "Rename Complete",
                f"Successfully renamed {renamed_count} files."
            )
        
        # Close dialog
        self.accept()
