from PySide6.QtWidgets import QSplitter

class UIManager:
    def __init__(self, main_window):
        self.main_window = main_window

    def toggle_date_filter(self, enabled):
        """Toggle date filter controls"""
        self.main_window.date_from.setEnabled(enabled)
        self.main_window.date_to.setEnabled(enabled)
    
    def toggle_pattern_filter(self, enabled):
        """Toggle pattern filter controls"""
        self.main_window.pattern_edit.setEnabled(enabled)
    
    def toggle_content_filter(self, enabled):
        """Toggle content filter controls"""
        self.main_window.content_edit.setEnabled(enabled)
    
    def clear_advanced_filters(self):
        """Clear all advanced filters"""
        self.main_window.date_filter_enabled.setChecked(False)
        self.main_window.pattern_filter_enabled.setChecked(False)
        self.main_window.content_filter_enabled.setChecked(False)
        self.main_window.date_from.setDate(QDate.currentDate().addDays(-30))
        self.main_window.date_to.setDate(QDate.currentDate())
        self.main_window.pattern_edit.clear()
        self.main_window.content_edit.clear()
    
    def get_advanced_filters(self):
        """Collect advanced filter settings"""
        filters = {}
        
        # Date range filter
        if self.main_window.date_filter_enabled.isChecked():
            filters['date_from'] = self.main_window.date_from.date().toPython()
            filters['date_to'] = self.main_window.date_to.date().toPython()
        
        # Filename pattern filter
        if self.main_window.pattern_filter_enabled.isChecked() and self.main_window.pattern_edit.text().strip():
            filters['filename_pattern'] = self.main_window.pattern_edit.text().strip()
        
        # Content search filter
        if self.main_window.content_filter_enabled.isChecked() and self.main_window.content_edit.text().strip():
            filters['content_search'] = self.main_window.content_edit.text().strip()
        
        return filters
    
    def refresh_category_dropdown(self):
        """Refresh the category dropdown with current categories"""
        # Save current selection
        current_selection = self.category_combo.currentText()
        
        # Clear and repopulate
        self.category_combo.clear()
        self.category_combo.addItem("All Files")
        for category in self.categories:
            self.category_combo.addItem(category.name)
        
        # Restore selection if it still exists
        index = self.category_combo.findText(current_selection)
        if index >= 0:
            self.category_combo.setCurrentIndex(index)
        else:
            self.category_combo.setCurrentIndex(0)  # Default to "All Files"

    def toggle_preview_panel(self, checked):
        """Toggle the preview panel visibility"""
        self.main_window.preview_panel.setVisible(checked)
        
        # Update splitter sizes when hiding/showing preview
        if checked:
            # Show preview panel
            splitter = self.main_window.preview_panel.parent()
            if isinstance(splitter, QSplitter):
                splitter.setSizes([700, 300])
        else:
            # Hide preview panel  
            splitter = self.main_window.preview_panel.parent()
            if isinstance(splitter, QSplitter):
                splitter.setSizes([1000, 0])
