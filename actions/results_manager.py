from PySide6.QtWidgets import QTableWidgetItem, QMessageBox, QFileDialog
from PySide6.QtGui import QColor

class ResultsManager:
    """Manager for handling results display and export"""
    def __init__(self, main_window, results_table, files):
        self.main_window = main_window
        self.results_table = results_table  # QTableWidget instance
        self.files = files  # List of FileInfo objects
    
    def refresh_results_display(self):
        """Refresh the results table display"""
        # Update the table with current file information
        for row in range(self.results_table.rowCount()):
            if row < len(self.files):
                file_info = self.files[row]
                self.results_table.setItem(row, 0, QTableWidgetItem(file_info.name))
                self.results_table.setItem(row, 1, QTableWidgetItem(file_info.path))
    
    def refresh_results(self):
        """Refresh the results table with current categories"""
        # Store current scroll position and selection
        scroll_value = self.results_table.verticalScrollBar().value()
        selected_rows = [index.row() for index in self.results_table.selectedIndexes()]
        
        # Clear the table but keep the files list
        self.results_table.setRowCount(0)
        
        # Re-add all files with updated categories
        for file_info in self.files:
            # Update category for each file
            extension = file_info.extension.lower() if file_info.extension else ""
            file_info.category = None
            for category in self.main_window.categories:
                if category.matches(extension):
                    file_info.category = category
                    break
        
        # Re-populate the table
        for file_info in self.files:
            self.add_file_to_table(file_info)
        
        # Restore scroll position and selection
        self.results_table.verticalScrollBar().setValue(scroll_value)
        if selected_rows:
            for row in selected_rows:
                if row < self.results_table.rowCount():
                    self.results_table.selectRow(row)
    
    def add_file_to_table(self, file_info):
        """Add a file to the results table without adding to files list"""
        row = self.results_table.rowCount()
        self.results_table.insertRow(row)
        
        # Name
        self.results_table.setItem(row, 0, QTableWidgetItem(file_info.name))
        
        # Path
        self.results_table.setItem(row, 1, QTableWidgetItem(file_info.path))
        
        # Size
        self.results_table.setItem(row, 2, QTableWidgetItem(file_info.get_size_str()))
        
        # Type
        self.results_table.setItem(row, 3, QTableWidgetItem(file_info.extension))
        
        # Modified date
        date_str = file_info.modified_date.strftime("%Y-%m-%d %H:%M")
        self.results_table.setItem(row, 4, QTableWidgetItem(date_str))
        
        # Category
        category_name = file_info.category.name if file_info.category else "Uncategorized"
        category_item = QTableWidgetItem(category_name)
        if file_info.category:
            category_item.setForeground(QColor(file_info.category.color))
        self.results_table.setItem(row, 5, category_item)

    def on_file_selection_changed(self, selected, deselected):
        """Handle file selection change to update preview"""
        selected_indexes = self.results_table.selectionModel().selectedRows()
        
        if selected_indexes:
            row = selected_indexes[0].row()
            if row < len(self.files):
                file_info = self.files[row]
                # Record preview access for analytics
                self.main_window.usage_analytics.record_access(file_info.path)
                self.main_window.preview_panel.preview_file(file_info)
        else:
            self.main_window.preview_panel.clear_preview()

    def export_results(self):
        """Export results to CSV"""
        if not self.files:
            QMessageBox.warning(self.main_window, "Export Error", "No files to export.")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self.main_window, "Export Results", 
            str(Path.home() / "file_search_results.csv"),
            "CSV Files (*.csv)"
        )
        
        if not file_path:
            return
            
        try:
            import csv
            with open(file_path, 'w', encoding='utf-8-sig', newline='') as f:
                # Use comma as delimiter with proper quoting
                writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_ALL)
                
                # Write header
                writer.writerow(["Name", "Path", "Size (Bytes)", "Size (Human)", "Type", "Modified Date", "Category"])
                
                # Write data
                for file_info in self.files:
                    category_name = file_info.category.name if file_info.category else "Uncategorized"
                    writer.writerow([
                        file_info.name,
                        file_info.path,
                        str(file_info.size),
                        file_info.get_size_str(),
                        file_info.extension or "",
                        file_info.modified_date.strftime("%Y-%m-%d %H:%M:%S"),
                        category_name
                    ])
                    
            QMessageBox.information(self.main_window, "Export Complete", 
                f"Results exported to {file_path}\n\n"
                f"Exported {len(self.files)} files with 7 columns:\n"
                f"Name, Path, Size (Bytes), Size (Human), Type, Modified Date, Category\n\n"
                f"If columns appear merged when opening:\n"
                f"- In Excel: Use 'Data' > 'Text to Columns' with comma delimiter\n"
                f"- In LibreOffice: Choose comma as separator when opening")
        except Exception as e:
            QMessageBox.critical(self.main_window, "Export Error", f"Failed to export results: {str(e)}")
    
  