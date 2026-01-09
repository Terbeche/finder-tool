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
            self.results_manager.refresh_results_display()

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

    def move_selected_files(self):
        """Move selected files to a custom directory"""
        selected_rows = set(index.row() for index in self.main_window.results_table.selectedIndexes())
        if not selected_rows:
            QMessageBox.information(self.main_window, "No Selection", "Please select files to move.")
            return
        
        # Get target directory
        target_dir = QFileDialog.getExistingDirectory(
            self.main_window, "Select Target Directory", self.main_window.current_directory
        )
        
        if not target_dir:
            return
        
        # Ask user about organization options
        organize_reply = QMessageBox.question(
            self, "File Organization", 
            f"How would you like to organize the files in {target_dir}?\n\n"
            f"Yes: Organize by category (create subdirectories)\n"
            f"No: Move all files directly to target directory\n"
            f"Cancel: Cancel the operation",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
        )
        
        if organize_reply == QMessageBox.Cancel:
            return
        
        organize_by_category = organize_reply == QMessageBox.Yes
        
        # Confirm the operation
        confirm = QMessageBox.question(
            self, "Confirm Move Operation", 
            f"Move {len(selected_rows)} file(s) to:\n{target_dir}\n\n"
            f"Organization: {'By category' if organize_by_category else 'Direct move'}\n\n"
            f"This operation cannot be undone. Continue?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm != QMessageBox.Yes:
            return
        
        # Perform the move operation
        self._move_files_to_directory(selected_rows, target_dir, organize_by_category)
    
    def _move_files_to_directory(self, selected_rows, target_dir, organize_by_category):
        """Perform the actual file move operation"""
        from PySide6.QtWidgets import QProgressDialog
        from PySide6.QtCore import Qt
        
        target_path = Path(target_dir)
        files_to_move = [self.main_window.files[row] for row in selected_rows]
        
        # Create progress dialog
        progress = QProgressDialog("Moving files...", "Cancel", 0, len(files_to_move), self)
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)
        progress.show()
        
        moved_count = 0
        failed_moves = []
        
        for i, file_info in enumerate(files_to_move):
            if progress.wasCanceled():
                break
            
            progress.setValue(i)
            progress.setLabelText(f"Moving: {file_info.name}")
            
            try:
                source_path = Path(file_info.path)
                
                if organize_by_category:
                    # Create category subdirectory
                    category_name = file_info.category.name if file_info.category else "Uncategorized"
                    category_dir = target_path / category_name
                    category_dir.mkdir(exist_ok=True)
                    target_file_path = category_dir / source_path.name
                else:
                    # Move directly to target directory
                    target_file_path = target_path / source_path.name
                
                # Handle name conflicts
                counter = 1
                original_target = target_file_path
                while target_file_path.exists():
                    stem = original_target.stem
                    suffix = original_target.suffix
                    target_file_path = original_target.parent / f"{stem}_{counter}{suffix}"
                    counter += 1
                
                # Move the file
                shutil.move(str(source_path), str(target_file_path))
                moved_count += 1
                
            except Exception as e:
                failed_moves.append((file_info.name, str(e)))
        
        progress.setValue(len(files_to_move))
        progress.close()
        
        # Remove moved files from results
        if moved_count > 0:
            for row in sorted(selected_rows, reverse=True):
                if row - len([r for r in selected_rows if r > row]) < len(files_to_move) - len(failed_moves):
                    self.main_window.results_table.removeRow(row)
                    self.main_window.files.pop(row)
            
            # Update file count and total size
            self.file_count_label.setText(f"{len(self.main_window.files)} files found")
            total_size = sum(f.size for f in self.main_window.files)
            if total_size < 1024 * 1024:
                size_str = f"{total_size / 1024:.1f} KB"
            elif total_size < 1024 * 1024 * 1024:
                size_str = f"{total_size / (1024 * 1024):.1f} MB"
            else:
                size_str = f"{total_size / (1024 * 1024 * 1024):.2f} GB"
            self.total_size_label.setText(f"Total size: {size_str}")
        
        # Show results
        if failed_moves:
            failed_list = "\n".join([f"• {name}: {error}" for name, error in failed_moves[:10]])
            if len(failed_moves) > 10:
                failed_list += f"\n... and {len(failed_moves) - 10} more"
            
            QMessageBox.warning(
                self, "Move Operation Results",
                f"Move operation completed.\n\n"
                f"Successfully moved: {moved_count} files\n"
                f"Failed to move: {len(failed_moves)} files\n\n"
                f"Failed files:\n{failed_list}"
            )
        else:
            QMessageBox.information(
                self, "Move Operation Complete",
                f"Successfully moved {moved_count} files to:\n{target_dir}"
            )

    def open_file_by_path(self, file_path):
        """Open a file by its path (called from preview panel)"""
        try:
            if platform.system() == 'Windows':
                os.startfile(file_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', file_path])
            else:  # Linux
                subprocess.run(['xdg-open', file_path])
        except Exception as e:
            QMessageBox.warning(self, "Error Opening File", str(e))

    def open_containing_folder(self):
        """Open the folder containing the selected file"""
        selected_rows = self.main_window.results_table.selectedIndexes()
        if not selected_rows:
            return
            
        row = selected_rows[0].row()
        file_path = self.main_window.files[row].path
        parent_dir = os.path.dirname(file_path)
        
        try:
            if platform.system() == 'Windows':
                # Open Explorer and select the file
                subprocess.run(['explorer', '/select,', file_path])
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', parent_dir])
            else:  # Linux
                subprocess.run(['xdg-open', parent_dir])
        except Exception as e:
            QMessageBox.warning(self, "Error Opening Folder", str(e))

    def open_folder_by_path(self, file_path):
        """Open the folder containing a file (called from preview panel)"""
        parent_dir = os.path.dirname(file_path)
        
        try:
            if platform.system() == 'Windows':
                # Open Explorer and select the file
                subprocess.run(['explorer', '/select,', file_path])
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', parent_dir])
            else:  # Linux
                subprocess.run(['xdg-open', parent_dir])
        except Exception as e:
            QMessageBox.warning(self, "Error Opening Folder", str(e))
    
    