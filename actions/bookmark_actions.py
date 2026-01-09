import os
from pathlib import Path
from PySide6.QtWidgets import QDialog, QFormLayout, QLineEdit, QMessageBox, QVBoxLayout, QLabel, QDialogButtonBox
from PySide6.QtCore import Qt

class BookmarkActions:
    def __init__(self, main_window):
        self.main_window = main_window


    def update_bookmark_buttons(self):
        """Update the quick access bookmark buttons"""
        bookmarks = self.main_window.bookmark_manager.get_bookmarks()[:5]  # Top 5 most used
        
        for i, btn in enumerate(self.main_window.bookmark_buttons):
            if i < len(bookmarks):
                bookmark = bookmarks[i]
                btn.setText(bookmark.name)
                btn.setToolTip(f"{bookmark.path}\n{bookmark.description}" if bookmark.description else bookmark.path)
                btn.setVisible(True)
            else:
                btn.setVisible(False)
    
    def use_quick_bookmark(self, index):
        """Use a quick access bookmark"""
        bookmarks = self.main_window.bookmark_manager.get_bookmarks()
        if index < len(bookmarks):
            bookmark = bookmarks[index]
            self.main_window.path_edit.setText(bookmark.path)
            self.main_window.current_directory = bookmark.path
            self.main_window.bookmark_manager.use_bookmark(bookmark.path)
            self.update_bookmark_buttons()  # Refresh order based on usage
    
    def quick_save_location(self):
        """Quick save current directory as bookmark"""
        directory = self.main_window.path_edit.text()
        if not directory or not os.path.exists(directory):
            QMessageBox.warning(self.main_window, "Invalid Directory", "Please select a valid directory first.")
            return
        
        # Generate a default name
        default_name = Path(directory).name or "Root"
        
        name, _ = QLineEdit().text(), True
        # Simple input dialog
        dialog = QDialog(self.main_window)
        dialog.setWindowTitle("Save Location Bookmark")
        layout = QFormLayout(dialog)
        
        name_edit = QLineEdit(default_name)
        desc_edit = QLineEdit()
        desc_edit.setPlaceholderText("Optional description...")
        
        layout.addRow("Bookmark Name:", name_edit)
        layout.addRow("Description:", desc_edit)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec():
            name = name_edit.text().strip()
            description = desc_edit.text().strip()
            
            if name and self.main_window.bookmark_manager.add_bookmark(name, directory, description):
                QMessageBox.information(self.main_window, "Bookmark Saved", f"Location saved as '{name}'")
                self.update_bookmark_buttons()
            elif not name:
                QMessageBox.warning(self.main_window, "Invalid Name", "Please enter a bookmark name.")
            else:
                QMessageBox.warning(self.main_window, "Duplicate Bookmark", "This location is already bookmarked.")
    
    def quick_save_search(self):
        """Quick save current search settings as preset"""
        # Simple input dialog for preset name
        dialog = QDialog(self.main_window)
        dialog.setWindowTitle("Save Search Preset")
        layout = QFormLayout(dialog)
        
        name_edit = QLineEdit()
        name_edit.setPlaceholderText("Enter preset name...")
        desc_edit = QLineEdit()
        desc_edit.setPlaceholderText("Optional description...")
        
        layout.addRow("Preset Name:", name_edit)
        layout.addRow("Description:", desc_edit)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec():
            name = name_edit.text().strip()
            description = desc_edit.text().strip()
            
            if name:
                search_config = self.get_current_search_config()
                if self.main_window.bookmark_manager.add_preset(name, search_config, description):
                    QMessageBox.information(self.main_window, "Preset Saved", f"Search settings saved as '{name}'")
                else:
                    QMessageBox.warning(self, "Duplicate Preset", "A preset with this name already exists.")
            else:
                QMessageBox.warning(self, "Invalid Name", "Please enter a preset name.")
    
    def get_current_search_config(self):
        """Extract current search configuration"""
        return {
            "category": self.main_window.category_combo.currentText(),
            "min_size": self.main_window.min_size.value(),
            "max_size": self.main_window.max_size.value(),
            "max_depth": self.main_window.max_depth.value(),
            "date_filter_enabled": self.main_window.date_filter_enabled.isChecked(),
            "date_from": self.main_window.date_from.date().toString("yyyy-MM-dd") if self.main_window.date_filter_enabled.isChecked() else None,
            "date_to": self.main_window.date_to.date().toString("yyyy-MM-dd") if self.main_window.date_filter_enabled.isChecked() else None,
            "pattern_filter_enabled": self.main_window.pattern_filter_enabled.isChecked(),
            "filename_pattern": self.main_window.pattern_edit.text(),
            "content_filter_enabled": self.main_window.content_filter_enabled.isChecked(),
            "content_search": self.main_window.content_edit.text()
        }
    
    def open_bookmark_manager(self):
        """Open the bookmark manager dialog"""
        from dialogs.bookmark_dialog import BookmarkDialog
        dialog = BookmarkDialog(self.main_window.bookmark_manager, self.main_window, self.main_window.ui_manager)
        dialog.exec()
        self.update_bookmark_buttons()  # Refresh after closing
