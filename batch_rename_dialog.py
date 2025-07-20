from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QLineEdit, QComboBox, QCheckBox, QSpinBox, QTableWidget,
    QTableWidgetItem, QGroupBox, QFormLayout, QMessageBox,
    QHeaderView, QSplitter, QTextEdit
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import re
import os
from pathlib import Path


class BatchRenameDialog(QDialog):
    """Dialog for batch renaming files"""
    
    def __init__(self, files, parent=None):
        super().__init__(parent)
        self.files = files
        self.preview_names = []
        self.setWindowTitle("Batch Rename Tool")
        self.setModal(True)
        self.resize(800, 600)
        self.setup_ui()
        self.update_preview()
    
    def setup_ui(self):
        """Set up the user interface"""
        layout = QVBoxLayout(self)
        
        # Create splitter for options and preview
        splitter = QSplitter(Qt.Vertical)
        
        # Rename options section
        options_widget = QGroupBox("Rename Options")
        options_layout = QVBoxLayout(options_widget)
        
        # Pattern-based renaming
        pattern_group = QGroupBox("Pattern Renaming")
        pattern_layout = QFormLayout(pattern_group)
        
        self.use_pattern = QCheckBox("Use naming pattern")
        self.use_pattern.toggled.connect(self.update_preview)
        pattern_layout.addRow(self.use_pattern)
        
        self.pattern_edit = QLineEdit("File_{counter:03d}")
        self.pattern_edit.setPlaceholderText("e.g., IMG_{counter:03d}, {name}_backup, Photo_{date}")
        self.pattern_edit.textChanged.connect(self.update_preview)
        pattern_layout.addRow("Pattern:", self.pattern_edit)
        
        # Counter settings
        counter_layout = QHBoxLayout()
        self.start_number = QSpinBox()
        self.start_number.setRange(0, 9999)
        self.start_number.setValue(1)
        self.start_number.valueChanged.connect(self.update_preview)
        counter_layout.addWidget(QLabel("Start:"))
        counter_layout.addWidget(self.start_number)
        
        self.step_number = QSpinBox()
        self.step_number.setRange(1, 100)
        self.step_number.setValue(1)
        self.step_number.valueChanged.connect(self.update_preview)
        counter_layout.addWidget(QLabel("Step:"))
        counter_layout.addWidget(self.step_number)
        counter_layout.addStretch()
        
        pattern_layout.addRow("Counter:", counter_layout)
        options_layout.addWidget(pattern_group)
        
        # Find and replace
        replace_group = QGroupBox("Find and Replace")
        replace_layout = QFormLayout(replace_group)
        
        self.use_replace = QCheckBox("Find and replace text")
        self.use_replace.toggled.connect(self.update_preview)
        replace_layout.addRow(self.use_replace)
        
        self.find_text = QLineEdit()
        self.find_text.textChanged.connect(self.update_preview)
        replace_layout.addRow("Find:", self.find_text)
        
        self.replace_text = QLineEdit()
        self.replace_text.textChanged.connect(self.update_preview)
        replace_layout.addRow("Replace with:", self.replace_text)
        
        self.use_regex = QCheckBox("Use regular expressions")
        self.use_regex.toggled.connect(self.update_preview)
        replace_layout.addRow(self.use_regex)
        
        options_layout.addWidget(replace_group)
        
        # Case conversion
        case_group = QGroupBox("Case Conversion")
        case_layout = QFormLayout(case_group)
        
        self.case_combo = QComboBox()
        self.case_combo.addItems([
            "No change",
            "UPPERCASE", 
            "lowercase",
            "Title Case",
            "Sentence case"
        ])
        self.case_combo.currentTextChanged.connect(self.update_preview)
        case_layout.addRow("Convert case:", self.case_combo)
        
        options_layout.addWidget(case_group)
        
        # Extension handling
        ext_group = QGroupBox("Extension")
        ext_layout = QFormLayout(ext_group)
        
        self.preserve_extension = QCheckBox("Preserve file extension")
        self.preserve_extension.setChecked(True)
        self.preserve_extension.toggled.connect(self.update_preview)
        ext_layout.addRow(self.preserve_extension)
        
        options_layout.addWidget(ext_group)
        
        splitter.addWidget(options_widget)
        
        # Preview section
        preview_widget = QGroupBox("Preview")
        preview_layout = QVBoxLayout(preview_widget)
        
        # Info label
        self.info_label = QLabel(f"Renaming {len(self.files)} files")
        self.info_label.setFont(QFont("Arial", 10, QFont.Bold))
        preview_layout.addWidget(self.info_label)
        
        # Preview table
        self.preview_table = QTableWidget()
        self.preview_table.setColumnCount(3)
        self.preview_table.setHorizontalHeaderLabels(["Current Name", "New Name", "Status"])
        self.preview_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.preview_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.preview_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        preview_layout.addWidget(self.preview_table)
        
        # Pattern help
        help_text = QTextEdit()
        help_text.setMaximumHeight(100)
        help_text.setReadOnly(True)
        help_text.setHtml("""
        <b>Pattern Variables:</b><br>
        • <code>{name}</code> - Original filename (without extension)<br>
        • <code>{counter}</code> - Sequential number<br>
        • <code>{counter:03d}</code> - Zero-padded number (001, 002, etc.)<br>
        • <code>{ext}</code> - File extension<br>
        • <code>{size}</code> - File size<br>
        • <code>{date}</code> - Current date (YYYY-MM-DD)
        """)
        preview_layout.addWidget(help_text)
        
        splitter.addWidget(preview_widget)
        splitter.setSizes([300, 400])
        layout.addWidget(splitter)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.rename_button = QPushButton("Rename Files")
        self.rename_button.clicked.connect(self.perform_rename)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.rename_button)
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
    
    def update_preview(self):
        """Update the preview table with new names"""
        self.preview_names = []
        conflicts = 0
        errors = 0
        
        self.preview_table.setRowCount(len(self.files))
        
        for i, file_info in enumerate(self.files):
            original_name = file_info.name
            try:
                new_name = self.generate_new_name(file_info, i)
                
                # Check for conflicts
                status = "OK"
                if new_name in self.preview_names:
                    status = "⚠️ Duplicate"
                    conflicts += 1
                elif new_name == original_name:
                    status = "No change"
                elif os.path.exists(os.path.join(os.path.dirname(file_info.path), new_name)):
                    status = "⚠️ File exists"
                    conflicts += 1
                
                self.preview_names.append(new_name)
                
            except Exception as e:
                new_name = f"ERROR: {str(e)}"
                status = "❌ Error"
                errors += 1
            
            # Update table
            self.preview_table.setItem(i, 0, QTableWidgetItem(original_name))
            self.preview_table.setItem(i, 1, QTableWidgetItem(new_name))
            self.preview_table.setItem(i, 2, QTableWidgetItem(status))
        
        # Update info label
        info_text = f"Renaming {len(self.files)} files"
        if conflicts > 0:
            info_text += f" - {conflicts} conflicts"
        if errors > 0:
            info_text += f" - {errors} errors"
        
        self.info_label.setText(info_text)
        self.rename_button.setEnabled(conflicts == 0 and errors == 0)
    
    def generate_new_name(self, file_info, index):
        """Generate new name for a file based on settings"""
        from datetime import datetime
        
        # Start with original name
        original_name = file_info.name
        name_without_ext = Path(original_name).stem
        extension = Path(original_name).suffix
        
        new_name = name_without_ext
        
        # Apply pattern renaming
        if self.use_pattern.isChecked():
            pattern = self.pattern_edit.text()
            if pattern.strip():
                counter = self.start_number.value() + (index * self.step_number.value())
                
                # Replace pattern variables
                new_name = pattern.format(
                    name=name_without_ext,
                    counter=counter,
                    ext=extension.lstrip('.'),
                    size=file_info.get_size_str(),
                    date=datetime.now().strftime('%Y-%m-%d')
                )
        
        # Apply find and replace
        if self.use_replace.isChecked():
            find_text = self.find_text.text()
            replace_text = self.replace_text.text()
            
            if find_text:
                if self.use_regex.isChecked():
                    try:
                        new_name = re.sub(find_text, replace_text, new_name)
                    except re.error:
                        raise ValueError("Invalid regular expression")
                else:
                    new_name = new_name.replace(find_text, replace_text)
        
        # Apply case conversion
        case_option = self.case_combo.currentText()
        if case_option == "UPPERCASE":
            new_name = new_name.upper()
        elif case_option == "lowercase":
            new_name = new_name.lower()
        elif case_option == "Title Case":
            new_name = new_name.title()
        elif case_option == "Sentence case":
            new_name = new_name.capitalize()
        
        # Add extension back
        if self.preserve_extension.isChecked():
            new_name += extension
        
        return new_name
    
    def perform_rename(self):
        """Perform the actual file renaming"""
        if not self.preview_names:
            return
        
        # Final confirmation
        confirm = QMessageBox.question(
            self, "Confirm Rename",
            f"Rename {len(self.files)} files?\n\nThis action cannot be undone!",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm != QMessageBox.Yes:
            return
        
        # Perform renames
        success_count = 0
        failed_renames = []
        
        for i, file_info in enumerate(self.files):
            try:
                old_path = file_info.path
                new_name = self.preview_names[i]
                new_path = os.path.join(os.path.dirname(old_path), new_name)
                
                # Rename the file
                os.rename(old_path, new_path)
                
                # Update file info
                file_info.path = new_path
                file_info.name = new_name
                
                success_count += 1
                
            except Exception as e:
                failed_renames.append((file_info.name, str(e)))
        
        # Show results
        if failed_renames:
            failed_list = "\n".join([f"• {name}: {error}" for name, error in failed_renames[:10]])
            if len(failed_renames) > 10:
                failed_list += f"\n... and {len(failed_renames) - 10} more"
            
            QMessageBox.warning(
                self, "Rename Results",
                f"Rename operation completed.\n\n"
                f"Successfully renamed: {success_count} files\n"
                f"Failed to rename: {len(failed_renames)} files\n\n"
                f"Failed files:\n{failed_list}"
            )
        else:
            QMessageBox.information(
                self, "Rename Complete",
                f"Successfully renamed {success_count} files!"
            )
        
        # Close dialog
        self.accept()
