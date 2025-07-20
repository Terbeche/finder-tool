import os
import shutil

from pathlib import Path
import subprocess
import platform

from PySide6.QtWidgets import (
    QMainWindow, QFileDialog, QTableWidget, 
    QTableWidgetItem, QHeaderView, QVBoxLayout, QHBoxLayout, QWidget,
    QPushButton, QLabel, QLineEdit, QComboBox, QSpinBox,
    QMessageBox, QMenu, QProgressBar, QGroupBox, QAbstractItemView,
    QCheckBox, QDateEdit
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QAction, QColor
from file_category import FileCategory
from file_scanner_thread import FileScannerThread
from settings_dialog import SettingsDialog
from config_manager import ConfigManager

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
        
        # Initialize config manager
        self.config_manager = ConfigManager()
        
        # Load settings
        self.app_settings = self.config_manager.load_settings()
        # Initialize settings with loaded values
        self.categories = self.config_manager.load_categories(DEFAULT_CATEGORIES)
        self.current_directory = self.app_settings.get("last_directory", str(Path.home()))
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
        self.min_size.setValue(self.app_settings.get("default_min_size", 0))
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
        self.max_depth.setValue(self.app_settings.get("default_max_depth", 15))
        search_layout.addWidget(QLabel("Max Depth:"))
        search_layout.addWidget(self.max_depth)
        
        # Search button
        self.search_button = QPushButton("Search Files")
        self.search_button.clicked.connect(self.start_search)
        search_layout.addWidget(self.search_button)
        
        # Add pause/resume button
        self.pause_button = QPushButton("Pause")
        self.pause_button.clicked.connect(self.toggle_pause_scan)
        self.pause_button.setEnabled(False)
        search_layout.addWidget(self.pause_button)
        
        # Add stop button
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_scan)
        self.stop_button.setEnabled(False)
        search_layout.addWidget(self.stop_button)
        
        main_layout.addWidget(search_group)
        
        # Advanced Filters (Collapsible)
        self.advanced_group = QGroupBox("Advanced Filters")
        self.advanced_group.setCheckable(True)
        self.advanced_group.setChecked(False)
        advanced_layout = QVBoxLayout(self.advanced_group)
        
        # Date range filter
        date_layout = QHBoxLayout()
        self.date_filter_enabled = QCheckBox("Filter by date range")
        self.date_filter_enabled.toggled.connect(self.toggle_date_filter)
        date_layout.addWidget(self.date_filter_enabled)
        
        date_layout.addWidget(QLabel("From:"))
        self.date_from = QDateEdit()
        self.date_from.setDate(QDate.currentDate().addDays(-30))
        self.date_from.setCalendarPopup(True)
        self.date_from.setEnabled(False)
        date_layout.addWidget(self.date_from)
        
        date_layout.addWidget(QLabel("To:"))
        self.date_to = QDateEdit()
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setCalendarPopup(True)
        self.date_to.setEnabled(False)
        date_layout.addWidget(self.date_to)
        
        date_layout.addStretch()
        advanced_layout.addLayout(date_layout)
        
        # Filename pattern filter
        pattern_layout = QHBoxLayout()
        self.pattern_filter_enabled = QCheckBox("Filename pattern (regex)")
        self.pattern_filter_enabled.toggled.connect(self.toggle_pattern_filter)
        pattern_layout.addWidget(self.pattern_filter_enabled)
        
        self.pattern_edit = QLineEdit()
        self.pattern_edit.setPlaceholderText("e.g., IMG_\\d{4}, .*\\.backup\\..*, ^test.*\\.py$")
        self.pattern_edit.setEnabled(False)
        pattern_layout.addWidget(self.pattern_edit)
        
        advanced_layout.addLayout(pattern_layout)
        
        # Content search filter
        content_layout = QHBoxLayout()
        self.content_filter_enabled = QCheckBox("Content search (text files only)")
        self.content_filter_enabled.toggled.connect(self.toggle_content_filter)
        content_layout.addWidget(self.content_filter_enabled)
        
        self.content_edit = QLineEdit()
        self.content_edit.setPlaceholderText("Search for text within files...")
        self.content_edit.setEnabled(False)
        content_layout.addWidget(self.content_edit)
        
        advanced_layout.addLayout(content_layout)
        
        # Clear filters button
        clear_layout = QHBoxLayout()
        clear_layout.addStretch()
        self.clear_filters_button = QPushButton("Clear Filters")
        self.clear_filters_button.clicked.connect(self.clear_advanced_filters)
        clear_layout.addWidget(self.clear_filters_button)
        advanced_layout.addLayout(clear_layout)
        
        main_layout.addWidget(self.advanced_group)
        
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
    
    def toggle_date_filter(self, enabled):
        """Toggle date filter controls"""
        self.date_from.setEnabled(enabled)
        self.date_to.setEnabled(enabled)
    
    def toggle_pattern_filter(self, enabled):
        """Toggle pattern filter controls"""
        self.pattern_edit.setEnabled(enabled)
    
    def toggle_content_filter(self, enabled):
        """Toggle content filter controls"""
        self.content_edit.setEnabled(enabled)
    
    def clear_advanced_filters(self):
        """Clear all advanced filters"""
        self.date_filter_enabled.setChecked(False)
        self.pattern_filter_enabled.setChecked(False)
        self.content_filter_enabled.setChecked(False)
        self.date_from.setDate(QDate.currentDate().addDays(-30))
        self.date_to.setDate(QDate.currentDate())
        self.pattern_edit.clear()
        self.content_edit.clear()
    
    def get_advanced_filters(self):
        """Collect advanced filter settings"""
        filters = {}
        
        # Date range filter
        if self.date_filter_enabled.isChecked():
            filters['date_from'] = self.date_from.date().toPython()
            filters['date_to'] = self.date_to.date().toPython()
        
        # Filename pattern filter
        if self.pattern_filter_enabled.isChecked() and self.pattern_edit.text().strip():
            filters['filename_pattern'] = self.pattern_edit.text().strip()
        
        # Content search filter
        if self.content_filter_enabled.isChecked() and self.content_edit.text().strip():
            filters['content_search'] = self.content_edit.text().strip()
        
        return filters
    
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
        
        self.move_action = QAction("Move to Directory...", self)
        self.move_action.triggered.connect(self.move_selected_files)
        
        self.duplicate_action = QAction("Find Duplicates...", self)
        self.duplicate_action.triggered.connect(self.find_duplicates)
        
        # Export action
        self.export_action = QAction("Export Results to CSV", self)
        self.export_action.triggered.connect(self.export_results)
        
        # Help menu actions
        self.about_action = QAction("About", self)
        self.about_action.triggered.connect(self.show_about)
    
    def create_menu(self):
        """Create application menu"""
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("File")
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.open_containing_folder_action)
        file_menu.addSeparator()
        file_menu.addAction(self.export_action)
        file_menu.addSeparator()
        
        # Edit menu
        edit_menu = menu_bar.addMenu("Edit")
        edit_menu.addAction(self.settings_action)
        
        # Tools menu
        tools_menu = menu_bar.addMenu("Tools")
        tools_menu.addAction(self.duplicate_action)
        
        # Actions menu
        actions_menu = menu_bar.addMenu("Actions")
        actions_menu.addAction(self.delete_action)
        actions_menu.addAction(self.rename_action)
        actions_menu.addAction(self.move_action)
        actions_menu.addSeparator()
        actions_menu.addAction(self.export_action)
        
        # Help menu
        help_menu = menu_bar.addMenu("Help")
        help_menu.addAction(self.about_action)
    
    def browse_directory(self):
        """Open directory browser dialog"""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Directory", self.current_directory
        )
        if directory:
            self.current_directory = directory
            self.path_edit.setText(directory)
            
            # Save the current directory in settings
            self.app_settings["last_directory"] = directory
            self.config_manager.save_settings(self.app_settings)
    
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
        
        # Get advanced filters
        advanced_filters = self.get_advanced_filters()
        
        # Clear previous results
        self.results_table.setRowCount(0)
        self.files = []
        
        # Update UI
        self.search_button.setEnabled(False)
        self.pause_button.setEnabled(True)
        self.stop_button.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Stop any existing scanner thread
        if self.scanner_thread and self.scanner_thread.isRunning():
            self.scanner_thread.stop()
            self.scanner_thread.wait()
        
        # Create and start scanner thread
        self.scanner_thread = FileScannerThread(
            directory, min_size, max_size, extensions, 
            self.categories, self.max_depth.value(), advanced_filters
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
        self.add_file_to_table(file_info)
        
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
        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.statusBar().showMessage(f"Scan complete. Found {len(files)} files.")
        
        # Check for new file extensions
        if self.app_settings.get("auto_discover", True) and self.files:
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
        """Move selected files to trash"""
        selected_rows = set(index.row() for index in self.results_table.selectedIndexes())
        if not selected_rows:
            return
            
        # Confirm move to trash
        confirm = QMessageBox.warning(
            self, "Move to Trash", 
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
                    self, "Package Not Found", 
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
                file_path = self.files[row].path
                try:
                    if has_send2trash:
                        send2trash.send2trash(file_path)
                    else:
                        os.remove(file_path)
                        
                    self.results_table.removeRow(row)
                    self.files.pop(row)
                    processed_count += 1
                except Exception as e:
                    QMessageBox.warning(
                        self, "Error Processing File", 
                        f"Could not process {file_path}:\n{str(e)}"
                    )
            
            # Update status
            self.file_count_label.setText(f"{len(self.files)} files found")
            action_word = "moved to trash" if has_send2trash else "deleted"
            QMessageBox.information(self, "Operation Complete", f"Successfully {action_word} {processed_count} file(s).")
    
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
                    
            QMessageBox.information(self, "Export Complete", 
                f"Results exported to {file_path}\n\n"
                f"Exported {len(self.files)} files with 7 columns:\n"
                f"Name, Path, Size (Bytes), Size (Human), Type, Modified Date, Category\n\n"
                f"If columns appear merged when opening:\n"
                f"- In Excel: Use 'Data' > 'Text to Columns' with comma delimiter\n"
                f"- In LibreOffice: Choose comma as separator when opening")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export results: {str(e)}")
    
    def open_settings(self):
        """Open settings dialog"""
        dialog = SettingsDialog(self.categories, self)
        if dialog.exec():  # Dialog is fully closed when this returns
            # Now process the data safely
            try:
                print("Settings dialog accepted, updating settings...")
                # Update in-memory settings
                self.app_settings.update(dialog.app_settings)
                self.categories = dialog.categories
                
                # Save directly without threading
                print("Saving settings to disk...")
                self.config_manager.save_settings(dialog.app_settings)
                self.config_manager.save_categories(dialog.categories)
                print("Settings saved successfully")
                
                # Refresh UI with updated categories
                self.refresh_category_dropdown()
                if self.files:
                    self.refresh_results()
                    
            except Exception as e:
                print(f"Error in settings update: {e}")
    
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
            for category in self.categories:
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
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About Smart File Manager",
            "<h3>Smart File Manager</h3>"
            "<p>A powerful tool for finding and organizing files.</p>"
            "<p>Version 1.0</p>"
            "<p>© 2025 Mostefa Terbeche</p>"
            "<p>For more information, visit <a href='https://www.mostefaterbeche.me/'>our website</a>.</p>"
        )
    
    def show_context_menu(self, position):
        """Show context menu for selected files"""
        menu = QMenu()
        
        # Add actions
        menu.addAction(self.open_action)
        menu.addAction(self.open_containing_folder_action)
        menu.addSeparator()
        menu.addAction(self.rename_action)
        menu.addAction(self.move_action)
        menu.addAction(self.delete_action)
        
        # Add tools submenu if there are results
        if self.files:
            menu.addSeparator()
            tools_menu = menu.addMenu("Tools")
            tools_menu.addAction(self.duplicate_action)
            
            menu.addSeparator()
            menu.addAction(self.export_action)
        
        # Show menu at cursor position
        menu.exec_(self.results_table.viewport().mapToGlobal(position))
    
    def toggle_pause_scan(self):
        """Pause or resume the file scan"""
        if not self.scanner_thread or not self.scanner_thread.isRunning():
            return
            
        if self.scanner_thread.pause_requested:
            # Resume scan
            self.scanner_thread.resume()
            self.pause_button.setText("Pause")
            self.statusBar().showMessage("Scan resumed...")
        else:
            # Pause scan
            self.scanner_thread.pause()
            self.pause_button.setText("Resume")
            self.statusBar().showMessage("Scan paused. Click Resume to continue.")

    def stop_scan(self):
        """Stop the file scan"""
        if not self.scanner_thread or not self.scanner_thread.isRunning():
            return
            
        self.scanner_thread.stop()
        self.statusBar().showMessage("Stopping scan...")
        self.scanner_thread.wait(1000)  # Wait up to 1 second for thread to finish
        
        self.search_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.pause_button.setText("Pause")
        self.progress_bar.setVisible(False)
        self.statusBar().showMessage("Scan stopped by user.")

    def closeEvent(self, event):
        """Handle window close event"""
        # Save current settings before closing
        self.app_settings["last_directory"] = self.current_directory
        self.config_manager.save_settings(self.app_settings)
        print("Settings saved before closing.")
        super().closeEvent(event)
    
    def move_selected_files(self):
        """Move selected files to a custom directory"""
        selected_rows = set(index.row() for index in self.results_table.selectedIndexes())
        if not selected_rows:
            QMessageBox.information(self, "No Selection", "Please select files to move.")
            return
        
        # Get target directory
        target_dir = QFileDialog.getExistingDirectory(
            self, "Select Target Directory", self.current_directory
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
        files_to_move = [self.files[row] for row in selected_rows]
        
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
                    self.results_table.removeRow(row)
                    self.files.pop(row)
            
            # Update file count and total size
            self.file_count_label.setText(f"{len(self.files)} files found")
            total_size = sum(f.size for f in self.files)
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
    
    def find_duplicates(self):
        """Open duplicate detection dialog"""
        if not self.files:
            QMessageBox.information(self, "No Files", "Please search for files first before detecting duplicates.")
            return
        
        from duplicate_dialog import DuplicateDialog
        dialog = DuplicateDialog(self.files, self)
        dialog.exec()
