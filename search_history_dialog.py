from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox,
    QTabWidget, QWidget, QTextEdit, QMessageBox, QFileDialog,
    QComboBox, QSpinBox, QFormLayout, QProgressDialog
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont
from search_history_manager import SearchHistoryEntry
from datetime import datetime
from pathlib import Path

class SearchHistoryDialog(QDialog):
    """Dialog for viewing and managing search history"""
    
    def __init__(self, history_manager, main_window, parent=None):
        super().__init__(parent)
        self.history_manager = history_manager
        self.main_window = main_window
        self.setWindowTitle("Search History")
        self.setModal(True)
        self.resize(1000, 700)
        self.setup_ui()
        self.refresh_data()
    
    def setup_ui(self):
        """Set up the user interface"""
        layout = QVBoxLayout(self)
        
        # Create tab widget
        tab_widget = QTabWidget()
        
        # History Tab
        history_tab = QWidget()
        history_layout = QVBoxLayout(history_tab)
        
        # History controls
        controls_layout = QHBoxLayout()
        
        # Filter controls
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All Searches", "Last 7 Days", "Last 30 Days", "This Year"])
        self.filter_combo.currentTextChanged.connect(self.filter_history)
        controls_layout.addWidget(QLabel("Show:"))
        controls_layout.addWidget(self.filter_combo)
        
        controls_layout.addStretch()
        
        # Action buttons
        replay_btn = QPushButton("Replay Selected")
        replay_btn.clicked.connect(self.replay_search)
        controls_layout.addWidget(replay_btn)
        
        delete_btn = QPushButton("Delete Selected")
        delete_btn.clicked.connect(self.delete_search)
        controls_layout.addWidget(delete_btn)
        
        clear_all_btn = QPushButton("Clear All History")
        clear_all_btn.clicked.connect(self.clear_all_history)
        controls_layout.addWidget(clear_all_btn)
        
        history_layout.addLayout(controls_layout)
        
        # History table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(8)
        self.history_table.setHorizontalHeaderLabels([
            "Date/Time", "Directory", "Category", "Filters", 
            "Files Found", "Total Size", "Duration", "Description"
        ])
        self.history_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.history_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.history_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.history_table.setAlternatingRowColors(True)
        self.history_table.setSortingEnabled(True)
        
        # Connect selection change to show details
        self.history_table.selectionModel().selectionChanged.connect(self.on_selection_changed)
        
        history_layout.addWidget(self.history_table)
        
        # Details panel
        details_group = QGroupBox("Search Details")
        details_layout = QVBoxLayout(details_group)
        
        self.details_text = QTextEdit()
        self.details_text.setMaximumHeight(120)
        self.details_text.setReadOnly(True)
        details_layout.addWidget(self.details_text)
        
        history_layout.addWidget(details_group)
        
        tab_widget.addTab(history_tab, "Search History")
        
        # Statistics Tab
        stats_tab = QWidget()
        stats_layout = QVBoxLayout(stats_tab)
        
        # Statistics display
        self.stats_group = QGroupBox("Search Statistics")
        self.stats_layout = QFormLayout(self.stats_group)
        stats_layout.addWidget(self.stats_group)
        
        # Popular directories
        popular_dirs_group = QGroupBox("Most Searched Directories")
        popular_dirs_layout = QVBoxLayout(popular_dirs_group)
        
        self.popular_dirs_table = QTableWidget()
        self.popular_dirs_table.setColumnCount(3)
        self.popular_dirs_table.setHorizontalHeaderLabels(["Directory", "Search Count", "Actions"])
        self.popular_dirs_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        popular_dirs_layout.addWidget(self.popular_dirs_table)
        
        stats_layout.addWidget(popular_dirs_group)
        
        # Export controls
        export_layout = QHBoxLayout()
        export_btn = QPushButton("Export History to JSON")
        export_btn.clicked.connect(self.export_history)
        export_layout.addWidget(export_btn)
        export_layout.addStretch()
        
        stats_layout.addLayout(export_layout)
        stats_layout.addStretch()
        
        tab_widget.addTab(stats_tab, "Statistics")
        
        layout.addWidget(tab_widget)
        
        # Dialog buttons
        button_layout = QHBoxLayout()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def refresh_data(self):
        """Refresh all data in the dialog"""
        self.refresh_history()
        self.refresh_statistics()
    
    def filter_history(self):
        """Filter history based on selected criteria"""
        self.refresh_history()
    
    def refresh_history(self):
        """Refresh the history table"""
        filter_text = self.filter_combo.currentText()
        
        if filter_text == "All Searches":
            history = self.history_manager.get_history()
        elif filter_text == "Last 7 Days":
            history = self.history_manager.get_recent_searches(7)
        elif filter_text == "Last 30 Days":
            history = self.history_manager.get_recent_searches(30)
        elif filter_text == "This Year":
            history = self.history_manager.get_recent_searches(365)
        else:
            history = self.history_manager.get_history()
        
        self.history_table.setRowCount(len(history))
        
        for row, entry in enumerate(history):
            # Date/Time
            try:
                dt = datetime.fromisoformat(entry.timestamp)
                date_str = dt.strftime("%Y-%m-%d %H:%M")
            except:
                date_str = entry.timestamp[:16] if len(entry.timestamp) > 16 else entry.timestamp
            
            self.history_table.setItem(row, 0, QTableWidgetItem(date_str))
            
            # Directory
            dir_item = QTableWidgetItem(entry.directory)
            dir_item.setToolTip(entry.directory)
            self.history_table.setItem(row, 1, dir_item)
            
            # Category
            self.history_table.setItem(row, 2, QTableWidgetItem(entry.category))
            
            # Filters summary
            filters = []
            if entry.min_size > 0:
                filters.append(f"Min: {entry.min_size}MB")
            if entry.max_size > 0:
                filters.append(f"Max: {entry.max_size}MB")
            if entry.date_filter_enabled:
                filters.append("Date filter")
            if entry.pattern_filter_enabled:
                filters.append("Pattern")
            if entry.content_filter_enabled:
                filters.append("Content")
            
            filters_str = ", ".join(filters) if filters else "None"
            self.history_table.setItem(row, 3, QTableWidgetItem(filters_str))
            
            # Files found
            self.history_table.setItem(row, 4, QTableWidgetItem(str(entry.files_found)))
            
            # Total size
            size_str = self._format_size(entry.total_size)
            self.history_table.setItem(row, 5, QTableWidgetItem(size_str))
            
            # Duration
            duration_str = f"{entry.search_duration:.1f}s"
            self.history_table.setItem(row, 6, QTableWidgetItem(duration_str))
            
            # Description
            self.history_table.setItem(row, 7, QTableWidgetItem(entry.description or ""))
            
            # Store the entry object for later use
            self.history_table.item(row, 0).setData(Qt.UserRole, entry)
    
    def refresh_statistics(self):
        """Refresh the statistics display"""
        stats = self.history_manager.get_search_statistics()
        
        # Clear existing statistics
        while self.stats_layout.rowCount() > 0:
            self.stats_layout.removeRow(0)
        
        # Add statistics
        self.stats_layout.addRow("Total Searches:", QLabel(str(stats["total_searches"])))
        self.stats_layout.addRow("Average Files Found:", QLabel(f"{stats['average_files_found']:.1f}"))
        self.stats_layout.addRow("Total Data Scanned:", QLabel(self._format_size(stats["total_data_scanned"])))
        self.stats_layout.addRow("Average Search Time:", QLabel(f"{stats['average_search_time']:.1f}s"))
        self.stats_layout.addRow("Most Searched Directory:", QLabel(stats["most_searched_directory"]))
        self.stats_layout.addRow("Most Used Category:", QLabel(stats["most_used_category"]))
        
        # Popular directories
        popular_dirs = self.history_manager.get_popular_directories(10)
        self.popular_dirs_table.setRowCount(len(popular_dirs))
        
        for row, (directory, count) in enumerate(popular_dirs):
            self.popular_dirs_table.setItem(row, 0, QTableWidgetItem(directory))
            self.popular_dirs_table.setItem(row, 1, QTableWidgetItem(str(count)))
            
            # Quick search button
            quick_search_btn = QPushButton("Search Here")
            quick_search_btn.clicked.connect(lambda checked, d=directory: self.quick_search_directory(d))
            self.popular_dirs_table.setCellWidget(row, 2, quick_search_btn)
    
    def on_selection_changed(self):
        """Handle selection change in history table"""
        selected_rows = self.history_table.selectionModel().selectedRows()
        
        if not selected_rows:
            self.details_text.clear()
            return
        
        row = selected_rows[0].row()
        entry = self.history_table.item(row, 0).data(Qt.UserRole)
        
        if entry:
            details = self._format_search_details(entry)
            self.details_text.setPlainText(details)
    
    def _format_search_details(self, entry: SearchHistoryEntry) -> str:
        """Format search entry details for display"""
        try:
            dt = datetime.fromisoformat(entry.timestamp)
            date_str = dt.strftime("%A, %B %d, %Y at %I:%M %p")
        except:
            date_str = entry.timestamp
        
        details = [
            f"Search performed on: {date_str}",
            f"Directory: {entry.directory}",
            f"File Category: {entry.category}",
            f"Size Range: {entry.min_size}MB to {entry.max_size if entry.max_size > 0 else 'unlimited'}MB",
            f"Max Depth: {entry.max_depth}",
            ""
        ]
        
        if entry.date_filter_enabled:
            details.extend([
                "Date Filter:",
                f"  From: {entry.date_from or 'N/A'}",
                f"  To: {entry.date_to or 'N/A'}",
                ""
            ])
        
        if entry.pattern_filter_enabled:
            details.extend([
                "Filename Pattern Filter:",
                f"  Pattern: {entry.filename_pattern}",
                ""
            ])
        
        if entry.content_filter_enabled:
            details.extend([
                "Content Search Filter:",
                f"  Search Term: {entry.content_search}",
                ""
            ])
        
        details.extend([
            "Results:",
            f"  Files Found: {entry.files_found}",
            f"  Total Size: {self._format_size(entry.total_size)}",
            f"  Search Duration: {entry.search_duration:.2f} seconds",
            ""
        ])
        
        if entry.description:
            details.extend([
                "Description:",
                f"  {entry.description}"
            ])
        
        return "\n".join(details)
    
    def replay_search(self):
        """Replay the selected search"""
        selected_rows = self.history_table.selectionModel().selectedRows()
        
        if not selected_rows:
            QMessageBox.information(self, "No Selection", "Please select a search to replay.")
            return
        
        row = selected_rows[0].row()
        entry = self.history_table.item(row, 0).data(Qt.UserRole)
        
        if not entry:
            return
        
        # Apply the search configuration to the main window
        self._apply_search_config(entry)
        
        QMessageBox.information(self, "Search Applied", 
                              f"Search configuration has been applied.\nClick 'Search Files' to run the search.")
        self.accept()  # Close the dialog
    
    def _apply_search_config(self, entry: SearchHistoryEntry):
        """Apply search configuration from history entry to main window"""
        mw = self.main_window
        
        # Set directory
        mw.path_edit.setText(entry.directory)
        mw.current_directory = entry.directory
        
        # Set basic filters
        category_index = mw.category_combo.findText(entry.category)
        if category_index >= 0:
            mw.category_combo.setCurrentIndex(category_index)
        
        mw.min_size.setValue(entry.min_size)
        mw.max_size.setValue(entry.max_size)
        mw.max_depth.setValue(entry.max_depth)
        
        # Set advanced filters
        mw.date_filter_enabled.setChecked(entry.date_filter_enabled)
        if entry.date_from:
            mw.date_from.setDate(QDate.fromString(entry.date_from, "yyyy-MM-dd"))
        if entry.date_to:
            mw.date_to.setDate(QDate.fromString(entry.date_to, "yyyy-MM-dd"))
        
        mw.pattern_filter_enabled.setChecked(entry.pattern_filter_enabled)
        mw.pattern_edit.setText(entry.filename_pattern or "")
        
        mw.content_filter_enabled.setChecked(entry.content_filter_enabled)
        mw.content_edit.setText(entry.content_search or "")
        
        # Update filter control states
        mw.toggle_date_filter(entry.date_filter_enabled)
        mw.toggle_pattern_filter(entry.pattern_filter_enabled)
        mw.toggle_content_filter(entry.content_filter_enabled)
    
    def delete_search(self):
        """Delete the selected search from history"""
        selected_rows = self.history_table.selectionModel().selectedRows()
        
        if not selected_rows:
            QMessageBox.information(self, "No Selection", "Please select a search to delete.")
            return
        
        row = selected_rows[0].row()
        entry = self.history_table.item(row, 0).data(Qt.UserRole)
        
        if not entry:
            return
        
        confirm = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to delete this search from history?\n\n"
            f"Directory: {entry.directory}\n"
            f"Date: {entry.timestamp[:19]}",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            self.history_manager.remove_entry(entry.timestamp)
            self.refresh_data()
    
    def clear_all_history(self):
        """Clear all search history"""
        confirm = QMessageBox.question(
            self, "Confirm Clear All",
            "Are you sure you want to clear ALL search history?\n\n"
            "This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            self.history_manager.clear_history()
            self.refresh_data()
            QMessageBox.information(self, "History Cleared", "All search history has been cleared.")
    
    def export_history(self):
        """Export search history to JSON file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Search History",
            str(Path.home() / "search_history.json"),
            "JSON Files (*.json)"
        )
        
        if not file_path:
            return
        
        if self.history_manager.export_history(file_path):
            QMessageBox.information(self, "Export Complete", 
                                  f"Search history exported to:\n{file_path}")
        else:
            QMessageBox.warning(self, "Export Failed", "Failed to export search history.")
    
    def quick_search_directory(self, directory):
        """Quickly set up a search for the given directory"""
        self.main_window.path_edit.setText(directory)
        self.main_window.current_directory = directory
        
        QMessageBox.information(self, "Directory Set", 
                              f"Directory set to: {directory}\n"
                              f"You can now configure filters and search.")
        self.accept()
    
    def _format_size(self, size_bytes):
        """Format file size for display"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
