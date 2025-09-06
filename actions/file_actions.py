import os
import shutil
import platform
import subprocess
from PySide6.QtWidgets import QMessageBox, QFileDialog, QTableWidgetItem
from actions.batch_rename_dialog import BatchRenameDialog


class FileActions:
    """Class to handle file actions"""
    def __init__(self, main_window):
        self.main_window = main_window

    def delete_selected_files(self):
        """Move selected files to trash"""
        selected_rows = set(index.row() for index in self.main_window.results_table.selectedIndexes())
        if not selected_rows:
            return
            
        # Confirm move to trash
        confirm = QMessageBox.warning(
            self.main_window, "Move to Trash", 
            f"Are you sure you want to move {len(selected_rows)} file(s) to trash?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            # Move files to trash
            try:
                # First try to import send2trash
                import send2trash
                has_send2trash = True
            except ImportError:
                has_send2trash = False
                response = QMessageBox.question(
                    self.main_window, "Package Not Found", 
                    "The send2trash package is required for safely moving files to trash.\n"
                    "Would you like to permanently delete the files instead?\n\n"
                    "To use the trash feature, install send2trash: pip install send2trash",
                    QMessageBox.Yes | QMessageBox.No
                )
                if response != QMessageBox.Yes:
                    return
            
            # Delete/trash files
            processed_count = 0
            for row in sorted(selected_rows, reverse=True):
                file_path = self.main_window.files[row].path
                try:
                    if has_send2trash:
                        send2trash.send2trash(file_path)
                    else:
                        os.remove(file_path)
                        
                    self.main_window.results_table.removeRow(row)
                    self.main_window.files.pop(row)
                    processed_count += 1
                except Exception as e:
                    QMessageBox.warning(
                        self.main_window, "Error Processing File", 
                        f"Could not process {file_path}:\n{str(e)}"
                    )
            
            # Update status
            self.main_window.file_count_label.setText(f"{len(self.main_window.files)} files found")
            action_word = "moved to trash" if has_send2trash else "deleted"
            QMessageBox.information(self.main_window, "Operation Complete", f"Successfully {action_word} {processed_count} file(s).")
    
    def rename_file(self):
        """Rename selected file"""
        selected_rows = self.main_window.results_table.selectedIndexes()
        if not selected_rows:
            return
            
        row = selected_rows[0].row()
        file_info = self.main_window.files[row]
        
        new_name, ok = QFileDialog.getSaveFileName(
            self.main_window, "Rename File", file_info.path, "All Files (*.*)"
        )
        
        if ok and new_name:
            try:
                shutil.move(file_info.path, new_name)
                
                # Update file info
                file_info.path = new_name
                file_info.name = os.path.basename(new_name)
                
                # Update table
                self.main_window.results_table.setItem(row, 0, QTableWidgetItem(file_info.name))
                self.main_window.results_table.setItem(row, 1, QTableWidgetItem(file_info.path))
                
                QMessageBox.information(self.main_window, "File Renamed", f"File renamed successfully to {file_info.name}")
            except Exception as e:
                QMessageBox.warning(
                    self.main_window, "Error Renaming File", 
                    f"Could not rename {file_info.path}:\n{str(e)}"
                )
    
    def batch_rename_files(self):
        """Open batch rename dialog"""
        selected_rows = set(index.row() for index in self.main_window.results_table.selectedIndexes())
        
        if selected_rows:
            # Use selected files
            selected_files = [self.main_window.files[row] for row in selected_rows]
            dialog_title = f"Batch Rename {len(selected_files)} Selected Files"
        elif self.main_window.files:
            # Use all files if none selected
            confirm = QMessageBox.question(
                self.main_window, "Batch Rename",
                f"No files are selected. Rename all {len(self.main_window.files)} files in the results?",
                QMessageBox.Yes | QMessageBox.No
            )
            if confirm != QMessageBox.Yes:
                return
            selected_files = self.main_window.files
            dialog_title = f"Batch Rename All {len(self.main_window.files)} Files"
        else:
            QMessageBox.information(self.main_window, "No Files", "No files available to rename. Please search for files first.")
            return
        
        # Open batch rename dialog
        dialog = BatchRenameDialog(selected_files, self.main_window)
        dialog.setWindowTitle(dialog_title)
        
        if dialog.exec():
            # Refresh the results table to show new names
            self.main_window.refresh_results_display()

    def open_selected_file(self):
        """Open the selected file with default application"""
        selected_rows = self.main_window.results_table.selectedIndexes()
        if not selected_rows:
            return
            
        row = selected_rows[0].row()
        file_path = self.main_window.files[row].path
        
        # Record file access for analytics
        self.main_window.usage_analytics.record_access(file_path)
        
        try:
            if platform.system() == 'Windows':
                os.startfile(file_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', file_path])
            else:  # Linux
                subprocess.run(['xdg-open', file_path])
        except Exception as e:
            QMessageBox.warning(self.main_window, "Error Opening File", str(e))
