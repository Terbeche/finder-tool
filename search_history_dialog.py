from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox,
    QTabWidget, QWidget, QTextEdit, QMessageBox, QFileDialog,
    QComboBox, QSpinBox, QFormLayout, QProgressDialog, QLineEdit
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
    
    def setup_ui(self):
        """Set up the user interface"""
        layout = QVBoxLayout(self)
        
        # Create tab widget
        tab_widget = QTabWidget()
        
        # History tab
        history_tab = QWidget()
        history_layout = QVBoxLayout(history_tab)
        
        # Filter controls
        filter_group = QGroupBox("Filter History")
        filter_layout = QHBoxLayout(filter_group)
        
        filter_layout.addWidget(QLabel("Directory:"))
        self.dir_filter = QLineEdit()
        self.dir_filter.textChanged.connect(self.filter_history)
        filter_layout.addWidget(self.dir_filter)
        
        filter_layout.addWidget(QLabel("Results:"))
        self.results_filter = QComboBox()
        self.results_filter.addItems(["Any", "With results", "No results"])
        self.results_filter.currentIndexChanged.connect(self.filter_history)
        filter_layout.addWidget(self.results_filter)
        
        filter_layout.addWidget(QLabel("Sort by:"))
        self.sort_by = QComboBox()
        self.sort_by.addItems(["Most recent", "Directory", "Most files found", "Longest duration"])
        self.sort_by.currentIndexChanged.connect(self.filter_history)
        filter_layout.addWidget(self.sort_by)
        
        history_layout.addWidget(filter_group)
        
        # History table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels(["Timestamp", "Directory", "Files Found", "Duration", "Filters"])
        self.history_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.history_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.history_table.itemSelectionChanged.connect(self.on_selection_changed)
        history_layout.addWidget(self.history_table)
        
        # Details section
        details_group = QGroupBox("Search Details")
        details_layout = QVBoxLayout(details_group)
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        details_layout.addWidget(self.details_text)
        
        history_layout.addWidget(details_group)
        
        # Action buttons
        actions_layout = QHBoxLayout()
        
        self.replay_button = QPushButton("Replay Search")
        self.replay_button.clicked.connect(self.replay_search)
        self.replay_button.setEnabled(False)
        
        self.delete_button = QPushButton("Delete Entry")
        self.delete_button.clicked.connect(self.delete_search)
        self.delete_button.setEnabled(False)
        
        self.clear_all_button = QPushButton("Clear All History")
        self.clear_all_button.clicked.connect(self.clear_all_history)
        
        self.export_button = QPushButton("Export History")
        self.export_button.clicked.connect(self.export_history)
        
        actions_layout.addWidget(self.replay_button)
        actions_layout.addWidget(self.delete_button)
        actions_layout.addWidget(self.clear_all_button)
        actions_layout.addWidget(self.export_button)
        actions_layout.addStretch()
        
        history_layout.addLayout(actions_layout)
        
        tab_widget.addTab(history_tab, "Search History")
        
        # Statistics tab
        stats_tab = QWidget()
        stats_layout = QVBoxLayout(stats_tab)
        
        # Quick stats
        stats_group = QGroupBox("Search Statistics")
        stats_form = QFormLayout(stats_group)
        
        self.total_searches_label = QLabel("0")
        self.avg_results_label = QLabel("0")
        self.most_searched_dir_label = QLabel("None")
        
        stats_form.addRow("Total Searches:", self.total_searches_label)
        stats_form.addRow("Average Results:", self.avg_results_label)
        stats_form.addRow("Most Searched Directory:", self.most_searched_dir_label)
        
        stats_layout.addWidget(stats_group)
        
        # Top directories
        top_dirs_group = QGroupBox("Most Searched Directories")
        top_dirs_layout = QVBoxLayout(top_dirs_group)
        
        self.top_dirs_table = QTableWidget()
        self.top_dirs_table.setColumnCount(3)
        self.top_dirs_table.setHorizontalHeaderLabels(["Directory", "Search Count", "Last Search"])
        self.top_dirs_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        top_dirs_layout.addWidget(self.top_dirs_table)
        
        # Quick search buttons
        quick_search_layout = QHBoxLayout()
        quick_search_layout.addWidget(QLabel("Quick Search:"))
        
        for i in range(3):
            btn = QPushButton("Directory")
            btn.setVisible(False)
            btn.clicked.connect(lambda checked, idx=i: self.quick_search_directory(idx))
            quick_search_layout.addWidget(btn)
            setattr(self, f"quick_search_btn_{i}", btn)
        
        quick_search_layout.addStretch()
        top_dirs_layout.addLayout(quick_search_layout)
        
        stats_layout.addWidget(top_dirs_group)
        stats_layout.addStretch()
        
        tab_widget.addTab(stats_tab, "Statistics")
        
        layout.addWidget(tab_widget)
        
        # Close button
        close_layout = QHBoxLayout()
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        close_layout.addStretch()
        close_layout.addWidget(close_button)
        
        layout.addLayout(close_layout)
        
        self.refresh_data()
    
    def refresh_data(self):
        """Refresh all history data"""
        self.refresh_history()
        self.refresh_statistics()
    
    def filter_history(self):
        """Filter history based on current filter settings"""
        dir_filter = self.dir_filter.text().lower()
        results_filter_idx = self.results_filter.currentIndex()
        sort_idx = self.sort_by.currentIndex()
        
        entries = self.history_manager.get_entries()
        
        # Apply directory filter
        if dir_filter:
            entries = [e for e in entries if dir_filter in e.directory.lower()]
        
        # Apply results filter
        if results_filter_idx == 1:  # With results
            entries = [e for e in entries if e.results and e.results.get("files_found", 0) > 0]
        elif results_filter_idx == 2:  # No results
            entries = [e for e in entries if not e.results or e.results.get("files_found", 0) == 0]
        
        # Sort entries
        if sort_idx == 0:  # Most recent
            entries.sort(key=lambda e: e.timestamp if e.timestamp else "", reverse=True)
        elif sort_idx == 1:  # Directory
            entries.sort(key=lambda e: e.directory.lower())
        elif sort_idx == 2:  # Most files found
            entries.sort(key=lambda e: e.results.get("files_found", 0) if e.results else 0, reverse=True)
        elif sort_idx == 3:  # Longest duration
            entries.sort(key=lambda e: e.results.get("search_duration", 0) if e.results else 0, reverse=True)
        
        # Update table
        self.history_table.setRowCount(len(entries))
        
        for row, entry in enumerate(entries):
            # Timestamp
            timestamp = "Unknown"
            if entry.timestamp:
                try:
                    dt = datetime.fromisoformat(entry.timestamp)
                    timestamp = dt.strftime("%Y-%m-%d %H:%M")
                except (ValueError, TypeError):
                    pass
            
            self.history_table.setItem(row, 0, QTableWidgetItem(timestamp))
            
            # Directory
            self.history_table.setItem(row, 1, QTableWidgetItem(entry.directory))
            
            # Files found
            files_found = entry.results.get("files_found", 0) if entry.results else 0
            self.history_table.setItem(row, 2, QTableWidgetItem(str(files_found)))
            
            # Duration
            duration = entry.results.get("search_duration", 0) if entry.results else 0
            self.history_table.setItem(row, 3, QTableWidgetItem(f"{duration:.2f}s"))
            
            # Filters
            filters = []
            if entry.category != "All Files":
                filters.append(entry.category)
            if entry.min_size > 0:
                filters.append(f"Min: {entry.min_size}MB")
            if entry.max_size > 0:
                filters.append(f"Max: {entry.max_size}MB")
            if entry.date_filter_enabled:
                filters.append("Date filter")
            if entry.pattern_filter_enabled:
                filters.append("Pattern filter")
            if entry.content_filter_enabled:
                filters.append("Content filter")
            
            filter_text = ", ".join(filters) if filters else "None"
            self.history_table.setItem(row, 4, QTableWidgetItem(filter_text))
    
    def refresh_history(self):
        """Refresh history with current filters"""
        self.filter_history()
    
    def refresh_statistics(self):
        """Refresh statistics tab"""
        entries = self.history_manager.get_entries()
        
        # Basic stats
        self.total_searches_label.setText(str(len(entries)))
        
        total_files = sum(e.results.get("files_found", 0) for e in entries if e.results)
        avg_files = total_files / len(entries) if entries else 0
        self.avg_results_label.setText(f"{avg_files:.1f}")
        
        # Most searched directories
        dir_counts = {}
        dir_last_search = {}
        
        for entry in entries:
            dir_counts[entry.directory] = dir_counts.get(entry.directory, 0) + 1
            
            # Track last search time for each directory
            timestamp = entry.timestamp
            if timestamp:
                if entry.directory not in dir_last_search or timestamp > dir_last_search[entry.directory]:
                    dir_last_search[entry.directory] = timestamp
        
        # Most searched directory
        if dir_counts:
            most_searched = max(dir_counts.items(), key=lambda x: x[1])
            self.most_searched_dir_label.setText(f"{most_searched[0]} ({most_searched[1]} searches)")
        
        # Top directories table
        top_dirs = sorted(dir_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        self.top_dirs_table.setRowCount(len(top_dirs))
        
        for row, (directory, count) in enumerate(top_dirs):
            self.top_dirs_table.setItem(row, 0, QTableWidgetItem(directory))
            self.top_dirs_table.setItem(row, 1, QTableWidgetItem(str(count)))
            
            # Last search time
            last_search = "Unknown"
            if directory in dir_last_search:
                try:
                    dt = datetime.fromisoformat(dir_last_search[directory])
                    last_search = dt.strftime("%Y-%m-%d %H:%M")
                except (ValueError, TypeError):
                    pass
            
            self.top_dirs_table.setItem(row, 2, QTableWidgetItem(last_search))
        
        # Quick search buttons
        for i, (directory, count) in enumerate(top_dirs[:3]):
            button = getattr(self, f"quick_search_btn_{i}")
            button.setText(Path(directory).name)
            button.setToolTip(directory)
            button.setVisible(True)
    
    def on_selection_changed(self):
        """Handle selection change in history table"""
        selected_rows = self.history_table.selectedIndexes()
        if not selected_rows:
            self.details_text.clear()
            self.replay_button.setEnabled(False)
            self.delete_button.setEnabled(False)
            return
        
        # Get selected entry
        row = selected_rows[0].row()
        entries = self.history_manager.get_entries()
        
        # Apply current filters to get filtered entries
        dir_filter = self.dir_filter.text().lower()
        results_filter_idx = self.results_filter.currentIndex()
        
        if dir_filter:
            entries = [e for e in entries if dir_filter in e.directory.lower()]
        
        if results_filter_idx == 1:  # With results
            entries = [e for e in entries if e.results and e.results.get("files_found", 0) > 0]
        elif results_filter_idx == 2:  # No results
            entries = [e for e in entries if not e.results or e.results.get("files_found", 0) == 0]
        
        sort_idx = self.sort_by.currentIndex()
        if sort_idx == 0:  # Most recent
            entries.sort(key=lambda e: e.timestamp if e.timestamp else "", reverse=True)
        elif sort_idx == 1:  # Directory
            entries.sort(key=lambda e: e.directory.lower())
        elif sort_idx == 2:  # Most files found
            entries.sort(key=lambda e: e.results.get("files_found", 0) if e.results else 0, reverse=True)
        elif sort_idx == 3:  # Longest duration
            entries.sort(key=lambda e: e.results.get("search_duration", 0) if e.results else 0, reverse=True)
        
        if row >= len(entries):
            return
        
        entry = entries[row]
        self.details_text.setText(self._format_search_details(entry))
        self.replay_button.setEnabled(True)
        self.delete_button.setEnabled(True)
    
    def _format_search_details(self, entry: SearchHistoryEntry) -> str:
        """Format search details for display"""
        details = []
        
        details.append(f"<b>Search Directory:</b> {entry.directory}")
        
        # Timestamp
        if entry.timestamp:
            try:
                dt = datetime.fromisoformat(entry.timestamp)
                timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
                details.append(f"<b>Time:</b> {timestamp}")
            except (ValueError, TypeError):
                details.append("<b>Time:</b> Unknown")
        
        # Basic filters
        details.append(f"<b>Category:</b> {entry.category}")
        details.append(f"<b>Min Size:</b> {entry.min_size} MB")
        details.append(f"<b>Max Size:</b> {entry.max_size if entry.max_size > 0 else 'No limit'} MB")
        details.append(f"<b>Max Depth:</b> {entry.max_depth}")
        
        # Advanced filters
        if entry.date_filter_enabled:
            date_from = entry.date_from or "Any"
            date_to = entry.date_to or "Any"
            details.append(f"<b>Date Range:</b> {date_from} to {date_to}")
        
        if entry.pattern_filter_enabled:
            details.append(f"<b>Pattern Filter:</b> {entry.filename_pattern}")
        
        if entry.content_filter_enabled:
            details.append(f"<b>Content Search:</b> {entry.content_search}")
        
        # Results
        if entry.results:
            details.append("<br><b>Results:</b>")
            files_found = entry.results.get("files_found", 0)
            details.append(f"• Found {files_found} files")
            
            total_size = entry.results.get("total_size", 0)
            details.append(f"• Total size: {self._format_size(total_size)}")
            
            duration = entry.results.get("search_duration", 0)
            details.append(f"• Search time: {duration:.2f} seconds")
        
        return "<br>".join(details)
    
    def replay_search(self):
        """Replay the selected search"""
        selected_rows = self.history_table.selectedIndexes()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        entries = self.history_manager.get_entries()
        
        # Apply current filters to get filtered entries
        dir_filter = self.dir_filter.text().lower()
        results_filter_idx = self.results_filter.currentIndex()
        
        if dir_filter:
            entries = [e for e in entries if dir_filter in e.directory.lower()]
        
        if results_filter_idx == 1:  # With results
            entries = [e for e in entries if e.results and e.results.get("files_found", 0) > 0]
        elif results_filter_idx == 2:  # No results
            entries = [e for e in entries if not e.results or e.results.get("files_found", 0) == 0]
        
        sort_idx = self.sort_by.currentIndex()
        if sort_idx == 0:  # Most recent
            entries.sort(key=lambda e: e.timestamp if e.timestamp else "", reverse=True)
        elif sort_idx == 1:  # Directory
            entries.sort(key=lambda e: e.directory.lower())
        elif sort_idx == 2:  # Most files found
            entries.sort(key=lambda e: e.results.get("files_found", 0) if e.results else 0, reverse=True)
        elif sort_idx == 3:  # Longest duration
            entries.sort(key=lambda e: e.results.get("search_duration", 0) if e.results else 0, reverse=True)
        
        if row >= len(entries):
            return
        
        entry = entries[row]
        
        # Apply search configuration to main window
        self._apply_search_config(entry)
        
        # Close dialog and trigger search
        self.accept()
        self.main_window.start_search()
    
    def _apply_search_config(self, entry: SearchHistoryEntry):
        """Apply search configuration to main window"""
        mw = self.main_window
        
        # Set directory
        mw.path_edit.setText(entry.directory)
        mw.current_directory = entry.directory
        
        # Set category
        category_index = mw.category_combo.findText(entry.category)
        if category_index >= 0:
            mw.category_combo.setCurrentIndex(category_index)
        
        # Set size filters
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
        
        # Update advanced filter control states
        mw.toggle_date_filter(entry.date_filter_enabled)
        mw.toggle_pattern_filter(entry.pattern_filter_enabled)
        mw.toggle_content_filter(entry.content_filter_enabled)
    
    def delete_search(self):
        """Delete the selected search entry"""
        selected_rows = self.history_table.selectedIndexes()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        entries = self.history_manager.get_entries()
        
        # Apply current filters to get filtered entries
        dir_filter = self.dir_filter.text().lower()
        results_filter_idx = self.results_filter.currentIndex()
        
        if dir_filter:
            entries = [e for e in entries if dir_filter in e.directory.lower()]
        
        if results_filter_idx == 1:  # With results
            entries = [e for e in entries if e.results and e.results.get("files_found", 0) > 0]
        elif results_filter_idx == 2:  # No results
            entries = [e for e in entries if not e.results or e.results.get("files_found", 0) == 0]
        
        sort_idx = self.sort_by.currentIndex()
        if sort_idx == 0:  # Most recent
            entries.sort(key=lambda e: e.timestamp if e.timestamp else "", reverse=True)
        elif sort_idx == 1:  # Directory
            entries.sort(key=lambda e: e.directory.lower())
        elif sort_idx == 2:  # Most files found
            entries.sort(key=lambda e: e.results.get("files_found", 0) if e.results else 0, reverse=True)
        elif sort_idx == 3:  # Longest duration
            entries.sort(key=lambda e: e.results.get("search_duration", 0) if e.results else 0, reverse=True)
        
        if row >= len(entries):
            return
        
        entry = entries[row]
        
        confirm = QMessageBox.question(
            self, "Confirm Deletion",
            f"Delete this search history entry?\n\nDirectory: {entry.directory}",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            self.history_manager.delete_entry(entry.timestamp)
            self.refresh_data()
    
    def clear_all_history(self):
        """Clear all search history"""
        confirm = QMessageBox.question(
            self, "Confirm Clear All",
            "Are you sure you want to clear ALL search history?\n"
            "This cannot be undone.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            self.history_manager.clear_history()
            self.refresh_data()
    
    def export_history(self):
        """Export search history to file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Search History",
            str(Path.home() / "search_history.csv"),
            "CSV Files (*.csv)"
        )
        
        if not file_path:
            return
        
        try:
            entries = self.history_manager.get_entries()
            
            import csv
            with open(file_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "Timestamp", "Directory", "Files Found", "Total Size", 
                    "Duration", "Category", "Filters Used"
                ])
                
                for entry in entries:
                    # Format timestamp
                    timestamp = "Unknown"
                    if entry.timestamp:
                        try:
                            dt = datetime.fromisoformat(entry.timestamp)
                            timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
                        except (ValueError, TypeError):
                            pass
                    
                    # Get results
                    files_found = entry.results.get("files_found", 0) if entry.results else 0
                    total_size = entry.results.get("total_size", 0) if entry.results else 0
                    duration = entry.results.get("search_duration", 0) if entry.results else 0
                    
                    # Format filters
                    filters = []
                    if entry.min_size > 0:
                        filters.append(f"Min: {entry.min_size}MB")
                    if entry.max_size > 0:
                        filters.append(f"Max: {entry.max_size}MB")
                    if entry.date_filter_enabled:
                        filters.append(f"Date: {entry.date_from} to {entry.date_to}")
                    if entry.pattern_filter_enabled:
                        filters.append(f"Pattern: {entry.filename_pattern}")
                    if entry.content_filter_enabled:
                        filters.append(f"Content: {entry.content_search}")
                    
                    filters_str = "; ".join(filters)
                    
                    writer.writerow([
                        timestamp, 
                        entry.directory, 
                        files_found,
                        self._format_size(total_size), 
                        f"{duration:.2f}s",
                        entry.category,
                        filters_str
                    ])
            
            QMessageBox.information(
                self, "Export Complete", 
                f"Search history exported successfully to:\n{file_path}"
            )
        
        except Exception as e:
            QMessageBox.critical(
                self, "Export Failed", 
                f"Failed to export search history:\n{str(e)}"
            )
    
    def quick_search_directory(self, directory_index):
        """Perform quick search on frequently used directory"""
        entries = self.history_manager.get_entries()
        
        # Count directory occurrences
        dir_counts = {}
        for entry in entries:
            dir_counts[entry.directory] = dir_counts.get(entry.directory, 0) + 1
        
        # Get top directories
        top_dirs = sorted(dir_counts.items(), key=lambda x: x[1], reverse=True)
        
        if directory_index < len(top_dirs):
            directory = top_dirs[directory_index][0]
            
            # Set directory in main window
            self.main_window.path_edit.setText(directory)
            self.main_window.current_directory = directory
            
            # Close dialog and trigger search
            self.accept()
            self.main_window.start_search()
    
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
