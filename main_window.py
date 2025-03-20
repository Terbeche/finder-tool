import os
import shutil

from pathlib import Path
import subprocess
import platform

from PySide6.QtWidgets import (
    QMainWindow, QFileDialog, QTableWidget, 
    QTableWidgetItem, QHeaderView, QVBoxLayout, QHBoxLayout, QWidget,
    QPushButton, QLabel, QLineEdit, QComboBox, QSpinBox, QCheckBox,
    QMessageBox, QMenu, QProgressBar, QGroupBox, QAbstractItemView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QColor
from file_category import FileCategory
from file_scanner_thread import FileScannerThread
from settings_dialog import SettingsDialog

DEFAULT_CATEGORIES = [
    FileCategory("Video", ["mp4", "avi", "mkv", "mov", "wmv", "flv", "webm", "m4v", "3gp"], "#e74c3c"),
    FileCategory("Audio", ["mp3", "wav", "ogg", "flac", "aac", "wma", "m4a"], "#9b59b6"),
    FileCategory("Images", ["jpg", "jpeg", "png", "gif", "bmp", "tiff", "webp", "svg"], "#2ecc71"),
    FileCategory("Documents", ["pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "txt", "csv", "rtf"], "#f39c12"),
    FileCategory("Archives", ["zip", "rar", "7z", "tar", "gz", "bz2"], "#34495e"),
    FileCategory("Executables", ["exe", "msi", "app", "dmg", "deb", "rpm"], "#e67e22")
]

class MainWindow(QMainWindow):
    """Main application window"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart File Manager")
        self.resize(1000, 700)
        
        # Initialize settings
        self.categories = DEFAULT_CATEGORIES.copy()
        self.current_directory = str(Path.home())
        self.files = []
        self.scanner_thread = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface"""
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        # Search options
        search_group = QGroupBox("Search Options")
        search_layout = QHBoxLayout(search_group)
        
        # Directory selection
        self.path_edit = QLineEdit(self.current_directory)
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.browse_directory)
        
        search_layout.addWidget(QLabel("Directory:"))
        search_layout.addWidget(self.path_edit, 1)
        search_layout.addWidget(browse_button)
        
        # File type selection
        self.category_combo = QComboBox()
        self.category_combo.addItem("All Files")
        for category in self.categories:
            self.category_combo.addItem(category.name)
        
        search_layout.addWidget(QLabel("File Type:"))
        search_layout.addWidget(self.category_combo)
        
        # Size filters
        self.min_size = QSpinBox()
        self.min_size.setRange(0, 10000)
        self.min_size.setValue(1)
        self.min_size.setSuffix(" MB")

        self.max_size = QSpinBox()
        self.max_size.setRange(0, 100000)
        self.max_size.setValue(0)  # 0 means no limit
        self.max_size.setSuffix(" MB")
        self.max_size.setSpecialValueText("No Limit")
        
        search_layout.addWidget(QLabel("Size:"))
        search_layout.addWidget(self.min_size)
        search_layout.addWidget(QLabel("to"))
        search_layout.addWidget(self.max_size)
        
        # Depth setting
        self.max_depth = QSpinBox()
        self.max_depth.setRange(1, 100)
        self.max_depth.setValue(15)
        search_layout.addWidget(QLabel("Max Depth:"))
        search_layout.addWidget(self.max_depth)
        
        # Search button
        self.search_button = QPushButton("Search Files")
        self.search_button.clicked.connect(self.start_search)
        search_layout.addWidget(self.search_button)
        
        main_layout.addWidget(search_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(6)
        self.results_table.setHorizontalHeaderLabels(["Name", "Path", "Size", "Type", "Modified", "Category"])
        self.results_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.results_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.results_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.results_table.customContextMenuRequested.connect(self.show_context_menu)
        self.results_table.setSortingEnabled(True)
        
        main_layout.addWidget(self.results_table, 1)
        
        # Status bar with counts
        self.file_count_label = QLabel("0 files found")
        self.total_size_label = QLabel("Total size: 0 B")
        
        status_bar = self.statusBar()
        status_bar.addPermanentWidget(self.file_count_label)
        status_bar.addPermanentWidget(self.total_size_label)
        
        # Set the main widget
        self.setCentralWidget(main_widget)
        
        # Create actions
        self.create_actions()
        
        # Create menu
        self.create_menu()
    
    def create_actions(self):
        """Create application actions"""
        # File menu actions
        self.open_action = QAction("Open", self)
        self.open_action.triggered.connect(self.open_selected_file)
        
        self.open_containing_folder_action = QAction("Open Containing Folder", self)
        self.open_containing_folder_action.triggered.connect(self.open_containing_folder)
        
        # Edit menu actions
        self.settings_action = QAction("Settings", self)
        self.settings_action.triggered.connect(self.open_settings)
        
        # Actions menu
        self.delete_action = QAction("Delete Selected Files", self)
        self.delete_action.triggered.connect(self.delete_selected_files)
        
        self.rename_action = QAction("Rename File", self)
        self.rename_action.triggered.connect(self.rename_file)
    
    def create_menu(self):
        """Create application menu"""
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("File")
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.open_containing_folder_action)
        file_menu.addSeparator()
        
        # Edit menu
        edit_menu = menu_bar.addMenu("Edit")
        edit_menu.addAction(self.settings_action)
        
        # Actions menu
        actions_menu = menu_bar.addMenu("Actions")
        actions_menu.addAction(self.delete_action)
        actions_menu.addAction(self.rename_action)
    
    def browse_directory(self):
        """Open directory browser dialog"""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Directory", self.current_directory
        )
        if directory:
            self.current_directory = directory
            self.path_edit.setText(directory)
    
    def start_search(self):
        """Start file search operation"""
        # Get search parameters
        directory = self.path_edit.text()
        if not os.path.exists(directory):
            QMessageBox.warning(self, "Invalid Directory", "The specified directory does not exist.")
            return
        
        # Update current directory
        self.current_directory = directory
        
        # Get selected category
        selected_category_index = self.category_combo.currentIndex()
        extensions = []
        if selected_category_index > 0:
            # Specific category selected
            category = self.categories[selected_category_index - 1]
            extensions = category.extensions
        
        # Get size constraints
        min_size = self.min_size.value()
        max_size = self.max_size.value() if self.max_size.value() > 0 else None
        
        # Clear previous results
        self.results_table.setRowCount(0)
        self.files = []
        
        # Update UI
        self.search_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Stop any existing scanner thread
        if self.scanner_thread and self.scanner_thread.isRunning():
            self.scanner_thread.stop()
            self.scanner_thread.wait()
        
        # Create and start scanner thread
        self.scanner_thread = FileScannerThread(
            directory, min_size, max_size, extensions, 
            self.categories, self.max_depth.value()
        )
        self.scanner_thread.update_progress.connect(self.update_progress)
        self.scanner_thread.file_found.connect(self.add_file_to_results)
        self.scanner_thread.scan_complete.connect(self.scan_complete)
        self.scanner_thread.start()
    
    def update_progress(self, current, total):
        """Update progress bar during scanning"""
        if total > 0:
            percent = int((current / total) * 100)
            self.progress_bar.setValue(percent)
            self.statusBar().showMessage(f"Scanning... {current} of {total} items processed")
    
    def add_file_to_results(self, file_info):
        """Add a file to the results table"""
        self.files.append(file_info)
        
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
        category_name = file_info.category.name if file_info.category else ""
        category_item = QTableWidgetItem(category_name)
        if file_info.category:
            category_item.setForeground(QColor(file_info.category.color))
        self.results_table.setItem(row, 5, category_item)
        
        # Update file count
        self.file_count_label.setText(f"{len(self.files)} files found")
        
        # Update total size
        total_size = sum(f.size for f in self.files)
        if total_size < 1024 * 1024:
            size_str = f"{total_size / 1024:.1f} KB"
        elif total_size < 1024 * 1024 * 1024:
            size_str = f"{total_size / (1024 * 1024):.1f} MB"
        else:
            size_str = f"{total_size / (1024 * 1024 * 1024):.2f} GB"
        self.total_size_label.setText(f"Total size: {size_str}")
    
    def scan_complete(self, files):
        """Handle scan completion"""
        self.search_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.statusBar().showMessage(f"Scan complete. Found {len(files)} files.")
        
        # Check for new file extensions
        self.check_for_new_extensions()
    
    def check_for_new_extensions(self):
        """Check for file extensions not in any category"""
        # Get all known extensions
        known_extensions = set()
        for category in self.categories:
            known_extensions.update([ext.lower() for ext in category.extensions])
        
        # Find new extensions
        new_extensions = set()
        for file_info in self.files:
            if file_info.extension and file_info.extension.lower() not in known_extensions:
                new_extensions.add(file_info.extension.lower())
        
        if new_extensions:
            # Ask user if they want to add these extensions
            extensions_str = ", ".join(sorted(new_extensions))
            confirm = QMessageBox.question(
                self, "New File Extensions Found", 
                f"Found {len(new_extensions)} new file extensions: {extensions_str}\n\n"
                "Would you like to categorize these extensions?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if confirm == QMessageBox.Yes:
                # Show dialog to categorize extensions
                # (In a full implementation, we would have a dialog for this)
                pass
    
    def open_selected_file(self):
        """Open the selected file with default application"""
        selected_rows = self.results_table.selectedIndexes()
        if not selected_rows:
            return
            
        row = selected_rows[0].row()
        file_path = self.files[row].path
        
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
        selected_rows = self.results_table.selectedIndexes()
        if not selected_rows:
            return
            
        row = selected_rows[0].row()
        file_path = self.files[row].path
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
    
    def delete_selected_files(self):
        """Delete selected files"""
        selected_rows = set(index.row() for index in self.results_table.selectedIndexes())
        if not selected_rows:
            return
            
        # Confirm deletion
        confirm = QMessageBox.warning(
            self, "Confirm Deletion", 
            f"Are you sure you want to delete {len(selected_rows)} file(s)?\nThis cannot be undone!",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            # Delete files
            deleted_count = 0
            for row in sorted(selected_rows, reverse=True):
                file_path = self.files[row].path
                try:
                    os.remove(file_path)
                    self.results_table.removeRow(row)
                    self.files.pop(row)
                    deleted_count += 1
                except Exception as e:
                    QMessageBox.warning(
                        self, "Error Deleting File", 
                        f"Could not delete {file_path}:\n{str(e)}"
                    )
            
            # Update status
            self.file_count_label.setText(f"{len(self.files)} files found")
            QMessageBox.information(self, "Deletion Complete", f"Successfully deleted {deleted_count} file(s).")
    
    def rename_file(self):
        """Rename selected file"""
        selected_rows = self.results_table.selectedIndexes()
        if not selected_rows:
            return
            
        row = selected_rows[0].row()
        file_info = self.files[row]
        
        new_name, ok = QFileDialog.getSaveFileName(
            self, "Rename File", file_info.path, "All Files (*.*)"
        )
        
        if ok and new_name:
            try:
                shutil.move(file_info.path, new_name)
                
                # Update file info
                file_info.path = new_name
                file_info.name = os.path.basename(new_name)
                
                # Update table
                self.results_table.setItem(row, 0, QTableWidgetItem(file_info.name))
                self.results_table.setItem(row, 1, QTableWidgetItem(file_info.path))
                
                QMessageBox.information(self, "File Renamed", f"File renamed successfully to {file_info.name}")
            except Exception as e:
                QMessageBox.warning(
                    self, "Error Renaming File", 
                    f"Could not rename {file_info.path}:\n{str(e)}"
                )
    
    def open_settings(self):
        """Open settings dialog"""
        dialog = SettingsDialog(self.categories, self)
        if dialog.exec():
            self.categories = dialog.categories
            # Refresh the view if needed
            if self.files:
                self.refresh_results()
    
    def refresh_results(self):
        """Refresh the results table with current categories"""
        # Clear the table
        self.results_table.setRowCount(0)
        
        # Re-add all files with updated categories
        for file_info in self.files:
            # Update category
            extension = file_info.extension.lower()
            file_info.category = None
            for category in self.categories:
                if category.matches(extension):
                    file_info.category = category
                    break
            
            self.add_file_to_results(file_info)
    
    def export_results(self):
        """Export results to CSV"""
        if not self.files:
            QMessageBox.warning(self, "Export Error", "No files to export.")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Results", 
            str(Path.home() / "file_search_results.csv"),
            "CSV Files (*.csv)"
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                # Write header
                f.write("Name,Path,Size,Modified Date,Category\n")
                
                # Write data
                for file_info in self.files:
                    category_name = file_info.category.name if file_info.category else "Uncategorized"
                    f.write(f'"{file_info.name}","{file_info.path}",{file_info.size},"{file_info.modified_date}","{category_name}"\n')
                    
            QMessageBox.information(self, "Export Complete", f"Results exported to {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export results: {str(e)}")
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About Smart File Manager",
            "<h3>Smart File Manager</h3>"
            "<p>A powerful tool for finding and organizing files.</p>"
            "<p>Version 1.0</p>"
        )
    
    def show_context_menu(self, position):
        """Show context menu for selected files"""
        menu = QMenu()
        
        # Add actions
        menu.addAction(self.open_action)
        menu.addAction(self.open_containing_folder_action)
        menu.addSeparator()
        menu.addAction(self.rename_action)
        menu.addAction(self.delete_action)
        
        # Show menu at cursor position
        menu.exec_(self.results_table.viewport().mapToGlobal(position))

