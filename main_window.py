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
    QCheckBox, QDateEdit, QDialog, QFormLayout, QDialogButtonBox, QSplitter, QStyle
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QAction, QColor
from file_category import FileCategory
from file_scanner_thread import FileScannerThread
from settings_dialog import SettingsDialog
from config_manager import ConfigManager
from theme_manager import theme_manager
from bookmark_manager import BookmarkManager
from preview_panel import PreviewPanel
from search_history_manager import SearchHistoryManager
from usage_analytics import UsageAnalytics
from performance_optimizer import PerformanceOptimizer
from actions.batch_rename_dialog import BatchRenameDialog
from actions.file_actions import FileActions

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
        self.resize(1200, 800)
        
        # Initialize config manager
        self.config_manager = ConfigManager()
        
        # Initialize bookmark manager
        self.bookmark_manager = BookmarkManager(self.config_manager)
        
        # Initialize search history manager
        self.search_history_manager = SearchHistoryManager(self.config_manager)
        
        # Load settings
        self.app_settings = self.config_manager.load_settings()
        # Initialize settings with loaded values
        self.categories = self.config_manager.load_categories(DEFAULT_CATEGORIES)
        self.current_directory = self.app_settings.get("last_directory", str(Path.home()))
        self.files = []
        self.scanner_thread = None
        
        # Initialize usage analytics
        self.usage_analytics = UsageAnalytics()
        
        # Initialize performance optimizer
        self.performance_optimizer = PerformanceOptimizer()
        self.performance_optimizer.start_monitoring()
        
        # Initialize file actions handler
        self.file_actions = FileActions(self)
        
        # Apply saved theme
        saved_theme = self.app_settings.get("theme_internal", "light")
        theme_manager.apply_theme(saved_theme)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface"""
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(16, 16, 16, 16)
        
        # Search options with bookmark panel
        search_group = QGroupBox("Search Options")
        search_layout = QVBoxLayout(search_group)
        search_layout.setSpacing(8)
        
        # Quick Access Bookmarks Panel
        bookmarks_panel = QGroupBox("Quick Access")
        bookmarks_layout = QHBoxLayout(bookmarks_panel)
        bookmarks_layout.setSpacing(8)
        
        # Recent bookmarks buttons (max 5)
        self.bookmark_buttons = []
        for i in range(5):
            btn = QPushButton("Empty")
            btn.setVisible(False)
            btn.clicked.connect(lambda checked, idx=i: self.use_quick_bookmark(idx))
            self.bookmark_buttons.append(btn)
            bookmarks_layout.addWidget(btn)
        
        # Manage bookmarks button
        manage_bookmarks_btn = QPushButton("Manage Bookmarks...")
        manage_bookmarks_btn.clicked.connect(self.open_bookmark_manager)
        bookmarks_layout.addWidget(manage_bookmarks_btn)
        
        # Quick save buttons
        pixmap = QStyle.SP_DirIcon
        save_location_icon = self.style().standardIcon(pixmap)
        save_location_btn = QPushButton(save_location_icon, " Save Location")
        save_location_btn.setToolTip("Save current directory as bookmark")
        save_location_btn.clicked.connect(self.quick_save_location)
        
        pixmap = QStyle.SP_DialogSaveButton
        save_search_icon = self.style().standardIcon(pixmap)
        save_search_btn = QPushButton(save_search_icon, " Save Search")
        save_search_btn.setToolTip("Save current search settings as preset")
        save_search_btn.clicked.connect(self.quick_save_search)
        
        bookmarks_layout.addWidget(save_location_btn)
        bookmarks_layout.addWidget(save_search_btn)
        bookmarks_layout.addStretch()
        
        search_layout.addWidget(bookmarks_panel)
        
        # Main search controls
        main_search_layout = QHBoxLayout()
        
        # Directory selection
        self.path_edit = QLineEdit(self.current_directory)
        self.path_edit.setPlaceholderText("Enter directory path or browse...")
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.browse_directory)
        
        main_search_layout.addWidget(QLabel("Directory:"))
        main_search_layout.addWidget(self.path_edit, 1)
        main_search_layout.addWidget(browse_button)
        
        # File type selection
        self.category_combo = QComboBox()
        self.category_combo.addItem("All Files")
        for category in self.categories:
            self.category_combo.addItem(category.name)
        
        main_search_layout.addWidget(QLabel("File Type:"))
        main_search_layout.addWidget(self.category_combo)
        
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
        
        main_search_layout.addWidget(QLabel("Size:"))
        main_search_layout.addWidget(self.min_size)
        main_search_layout.addWidget(QLabel("to"))
        main_search_layout.addWidget(self.max_size)
        
        # Depth setting
        self.max_depth = QSpinBox()
        self.max_depth.setRange(1, 100)
        self.max_depth.setValue(self.app_settings.get("default_max_depth", 15))
        main_search_layout.addWidget(QLabel("Max Depth:"))
        main_search_layout.addWidget(self.max_depth)
        
        # Search button
        self.search_button = QPushButton("Search Files")
        self.search_button.clicked.connect(self.start_search)
        main_search_layout.addWidget(self.search_button)
        
        # Add pause/resume button
        self.pause_button = QPushButton("Pause")
        self.pause_button.clicked.connect(self.toggle_pause_scan)
        self.pause_button.setEnabled(False)
        main_search_layout.addWidget(self.pause_button)
        
        # Add stop button
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_scan)
        self.stop_button.setEnabled(False)
        main_search_layout.addWidget(self.stop_button)
        
        search_layout.addLayout(main_search_layout)
        main_layout.addWidget(search_group)
        
        # Advanced Filters (Collapsible)
        self.advanced_group = QGroupBox("Advanced Filters")
        self.advanced_group.setCheckable(True)
        self.advanced_group.setChecked(False)
        advanced_layout = QVBoxLayout(self.advanced_group)
        advanced_layout.setSpacing(8)
        
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
        self.clear_filters_button.setProperty("class", "secondary")
        self.clear_filters_button.clicked.connect(self.clear_advanced_filters)
        clear_layout.addWidget(self.clear_filters_button)
        advanced_layout.addLayout(clear_layout)
        
        main_layout.addWidget(self.advanced_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        main_layout.addWidget(self.progress_bar)
        
        # Main content area with splitter for results and preview
        content_splitter = QSplitter(Qt.Horizontal)
        
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
        self.results_table.setAlternatingRowColors(True)
        
        # Connect selection change to preview
        self.results_table.selectionModel().selectionChanged.connect(self.on_file_selection_changed)
        
        content_splitter.addWidget(self.results_table)
        
        # Preview panel
        self.preview_panel = PreviewPanel()
        content_splitter.addWidget(self.preview_panel)
        
        # Set splitter proportions (70% for table, 30% for preview)
        content_splitter.setSizes([700, 300])
        content_splitter.setCollapsible(0, False)  # Don't allow table to be collapsed
        content_splitter.setCollapsible(1, True)   # Allow preview panel to be collapsed
        
        main_layout.addWidget(content_splitter, 1)
        
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
        self.open_action.triggered.connect(self.file_actions.open_selected_file)
        
        self.open_containing_folder_action = QAction("Open Containing Folder", self)
        self.open_containing_folder_action.triggered.connect(self.open_containing_folder)
        
        # Edit menu actions
        self.settings_action = QAction("Settings", self)
        self.settings_action.triggered.connect(self.open_settings)
        
        # Actions menu
        self.delete_action = QAction("Delete Selected Files", self)
        self.delete_action.triggered.connect(self.file_actions.delete_selected_files)
        
        self.rename_action = QAction("Rename File", self)
        self.rename_action.triggered.connect(self.file_actions.rename_file)
        
        self.batch_rename_action = QAction("Batch Rename...", self)
        self.batch_rename_action.triggered.connect(self.file_actions.batch_rename_files)
        
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
        
        # Bookmark actions
        self.bookmark_manager_action = QAction("Manage Bookmarks...", self)
        self.bookmark_manager_action.triggered.connect(self.open_bookmark_manager)
        
        # View menu actions
        self.toggle_preview_action = QAction("Toggle Preview Panel", self)
        self.toggle_preview_action.setCheckable(True)
        self.toggle_preview_action.setChecked(True)
        self.toggle_preview_action.triggered.connect(self.toggle_preview_panel)
        
        # Search history actions
        self.search_history_action = QAction("Search History...", self)
        self.search_history_action.triggered.connect(self.open_search_history)
        
        # Security actions
        self.security_scan_action = QAction("Security Scan...", self)
        self.security_scan_action.triggered.connect(self.run_security_scan)
        
        self.file_integrity_action = QAction("Check File Integrity...", self)
        self.file_integrity_action.triggered.connect(self.check_file_integrity)
        
        # Usage analytics actions
        self.usage_analytics_action = QAction("Usage Analytics...", self)
        self.usage_analytics_action.triggered.connect(self.open_usage_analytics)
        
        # Performance actions
        self.performance_report_action = QAction("Performance Report...", self)
        self.performance_report_action.triggered.connect(self.show_performance_report)
        
        self.clear_cache_action = QAction("Clear Cache", self)
        self.clear_cache_action.triggered.connect(self.clear_performance_cache)
    
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
        tools_menu.addAction(self.batch_rename_action)
        
        # Add bookmarks to Tools menu
        tools_menu.addSeparator()
        tools_menu.addAction(self.bookmark_manager_action)
        
        # Add search history to Tools menu
        tools_menu.addAction(self.search_history_action)
        
        # Add security features to Tools menu
        tools_menu.addSeparator()
        security_menu = tools_menu.addMenu("Security")
        security_menu.addAction(self.security_scan_action)
        security_menu.addAction(self.file_integrity_action)
        
        # Add usage analytics to Tools menu
        tools_menu.addAction(self.usage_analytics_action)
        
        # Add performance menu
        tools_menu.addSeparator()
        performance_menu = tools_menu.addMenu("Performance")
        performance_menu.addAction(self.performance_report_action)
        performance_menu.addAction(self.clear_cache_action)
        
        # Actions menu
        actions_menu = menu_bar.addMenu("Actions")
        actions_menu.addAction(self.delete_action)
        actions_menu.addAction(self.rename_action)
        actions_menu.addAction(self.batch_rename_action)
        actions_menu.addAction(self.move_action)
        actions_menu.addSeparator()
        actions_menu.addAction(self.export_action)
        
        # Help menu
        help_menu = menu_bar.addMenu("Help")
        help_menu.addAction(self.about_action)
        
        # View menu
        view_menu = menu_bar.addMenu("View")
        view_menu.addAction(self.toggle_preview_action)
    
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
        # Record search start time
        from time import time
        search_start_time = time()
        
        # Check for cached results
        directory = self.path_edit.text()
        if not os.path.exists(directory):
            QMessageBox.warning(self, "Invalid Directory", "The specified directory does not exist.")
            return
        
        # Check cache first
        cached_result = self.performance_optimizer.get_cached_scan(directory)
        if cached_result:
            # Ask user if they want to use cached results
            use_cache = QMessageBox.question(
                self, "Cached Results Available",
                f"Found cached scan results for this directory.\n"
                f"Files: {cached_result['file_count']}\n"
                f"Scan time: {cached_result['scan_time']:.2f}s\n\n"
                f"Use cached results or perform new scan?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if use_cache == QMessageBox.Yes:
                self.statusBar().showMessage("Using cached results...")
                return
        
        # Get optimization strategy
        optimization = self.performance_optimizer.optimize_scan_strategy(directory)
        
        # Get search parameters
        if optimization == "fast":
            # Fast scan: only top-level files, no subdirectories
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
                self.categories, 1, advanced_filters
            )
            self.scanner_thread.update_progress.connect(self.update_progress)
            self.scanner_thread.file_found.connect(self.add_file_to_results)
            self.scanner_thread.scan_complete.connect(self.scan_complete)
            self.scanner_thread.start()
        else:
            # Full scan: all files and subdirectories
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
        
        # Store search configuration for history
        self.current_search_config = {
            "directory": directory,
            "category": self.category_combo.currentText(),
            "min_size": self.min_size.value(),
            "max_size": self.max_size.value(),
            "max_depth": self.max_depth.value(),
            "date_filter_enabled": self.date_filter_enabled.isChecked(),
            "date_from": self.date_from.date().toString("yyyy-MM-dd") if self.date_filter_enabled.isChecked() else None,
            "date_to": self.date_to.date().toString("yyyy-MM-dd") if self.date_filter_enabled.isChecked() else None,
            "pattern_filter_enabled": self.pattern_filter_enabled.isChecked(),
            "filename_pattern": self.pattern_edit.text(),
            "content_filter_enabled": self.content_filter_enabled.isChecked(),
            "content_search": self.content_edit.text()
        }
        self.search_start_time = search_start_time
    
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
        
        # Record performance metrics
        from time import time
        search_duration = time() - getattr(self, 'search_start_time', time())
        self.performance_optimizer.record_scan_performance(
            self.current_directory, len(files), search_duration
        )
        
        # Add search to history
        from time import time
        search_duration = time() - getattr(self, 'search_start_time', time())
        
        # Calculate total size
        total_size = sum(f.size for f in self.files)
        
        # Add search to history
        results_summary = {
            "files_found": len(files),
            "total_size": total_size,
            "search_duration": search_duration
        }
        
        if hasattr(self, 'current_search_config'):
            self.search_history_manager.add_search(
                self.current_search_config,
                results_summary
            )
    
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
        
    def refresh_results_display(self):
        """Refresh the results table display"""
        # Update the table with current file information
        for row in range(self.results_table.rowCount()):
            if row < len(self.files):
                file_info = self.files[row]
                self.results_table.setItem(row, 0, QTableWidgetItem(file_info.name))
                self.results_table.setItem(row, 1, QTableWidgetItem(file_info.path))
    
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
                
                # Apply theme if changed
                if "theme_internal" in dialog.app_settings:
                    theme_manager.apply_theme(dialog.app_settings["theme_internal"])
                
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
        menu.addAction(self.batch_rename_action)
        menu.addAction(self.move_action)
        menu.addAction(self.delete_action)
        
        # Add tools submenu if there are results
        if self.files:
            menu.addSeparator()
            tools_menu = menu.addMenu("Tools")
            tools_menu.addAction(self.duplicate_action)
            tools_menu.addAction(self.batch_rename_action)
            
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
        # Stop performance monitoring
        self.performance_optimizer.stop_monitoring()
        
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
    
    def update_bookmark_buttons(self):
        """Update the quick access bookmark buttons"""
        bookmarks = self.bookmark_manager.get_bookmarks()[:5]  # Top 5 most used
        
        for i, btn in enumerate(self.bookmark_buttons):
            if i < len(bookmarks):
                bookmark = bookmarks[i]
                btn.setText(bookmark.name)
                btn.setToolTip(f"{bookmark.path}\n{bookmark.description}" if bookmark.description else bookmark.path)
                btn.setVisible(True)
            else:
                btn.setVisible(False)
    
    def use_quick_bookmark(self, index):
        """Use a quick access bookmark"""
        bookmarks = self.bookmark_manager.get_bookmarks()
        if index < len(bookmarks):
            bookmark = bookmarks[index]
            self.path_edit.setText(bookmark.path)
            self.current_directory = bookmark.path
            self.bookmark_manager.use_bookmark(bookmark.path)
            self.update_bookmark_buttons()  # Refresh order based on usage
    
    def quick_save_location(self):
        """Quick save current directory as bookmark"""
        directory = self.path_edit.text()
        if not directory or not os.path.exists(directory):
            QMessageBox.warning(self, "Invalid Directory", "Please select a valid directory first.")
            return
        
        # Generate a default name
        default_name = Path(directory).name or "Root"
        
        name, _ = QLineEdit().text(), True
        # Simple input dialog
        dialog = QDialog(self)
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
            
            if name and self.bookmark_manager.add_bookmark(name, directory, description):
                QMessageBox.information(self, "Bookmark Saved", f"Location saved as '{name}'")
                self.update_bookmark_buttons()
            elif not name:
                QMessageBox.warning(self, "Invalid Name", "Please enter a bookmark name.")
            else:
                QMessageBox.warning(self, "Duplicate Bookmark", "This location is already bookmarked.")
    
    def quick_save_search(self):
        """Quick save current search settings as preset"""
        # Simple input dialog for preset name
        dialog = QDialog(self)
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
                if self.bookmark_manager.add_preset(name, search_config, description):
                    QMessageBox.information(self, "Preset Saved", f"Search settings saved as '{name}'")
                else:
                    QMessageBox.warning(self, "Duplicate Preset", "A preset with this name already exists.")
            else:
                QMessageBox.warning(self, "Invalid Name", "Please enter a preset name.")
    
    def get_current_search_config(self):
        """Extract current search configuration"""
        return {
            "category": self.category_combo.currentText(),
            "min_size": self.min_size.value(),
            "max_size": self.max_size.value(),
            "max_depth": self.max_depth.value(),
            "date_filter_enabled": self.date_filter_enabled.isChecked(),
            "date_from": self.date_from.date().toString("yyyy-MM-dd") if self.date_filter_enabled.isChecked() else None,
            "date_to": self.date_to.date().toString("yyyy-MM-dd") if self.date_filter_enabled.isChecked() else None,
            "pattern_filter_enabled": self.pattern_filter_enabled.isChecked(),
            "filename_pattern": self.pattern_edit.text(),
            "content_filter_enabled": self.content_filter_enabled.isChecked(),
            "content_search": self.content_edit.text()
        }
    
    def open_bookmark_manager(self):
        """Open the bookmark manager dialog"""
        from bookmark_dialog import BookmarkDialog
        dialog = BookmarkDialog(self.bookmark_manager, self, self)
        dialog.exec()
        self.update_bookmark_buttons()  # Refresh after closing
    
    def open_search_history(self):
        """Open the search history dialog"""
        from search_history_dialog import SearchHistoryDialog
        dialog = SearchHistoryDialog(self.search_history_manager, self, self)
        dialog.exec()
    
    def on_file_selection_changed(self, selected, deselected):
        """Handle file selection change to update preview"""
        selected_indexes = self.results_table.selectionModel().selectedRows()
        
        if selected_indexes:
            row = selected_indexes[0].row()
            if row < len(self.files):
                file_info = self.files[row]
                # Record preview access for analytics
                self.usage_analytics.record_access(file_info.path)
                self.preview_panel.preview_file(file_info)
        else:
            self.preview_panel.clear_preview()
    
    def toggle_preview_panel(self, checked):
        """Toggle the preview panel visibility"""
        self.preview_panel.setVisible(checked)
        
        # Update splitter sizes when hiding/showing preview
        if checked:
            # Show preview panel
            splitter = self.preview_panel.parent()
            if isinstance(splitter, QSplitter):
                splitter.setSizes([700, 300])
        else:
            # Hide preview panel  
            splitter = self.preview_panel.parent()
            if isinstance(splitter, QSplitter):
                splitter.setSizes([1000, 0])
    
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
    
    def run_security_scan(self):
        """Run security scan on current search results"""
        if not self.files:
            QMessageBox.information(self, "No Files", "Please search for files first before running security scan.")
            return
        
        from security_dialog import SecurityDialog
        dialog = SecurityDialog(self.files, self)
        dialog.exec()
    
    def check_file_integrity(self):
        """Check file integrity for selected files"""
        selected_rows = set(index.row() for index in self.results_table.selectedIndexes())
        
        if selected_rows:
            # Use selected files
            selected_files = [self.files[row] for row in selected_rows]
            dialog_title = f"Check Integrity of {len(selected_files)} Selected Files"
        elif self.files:
            # Use all files if none selected
            confirm = QMessageBox.question(
                self, "File Integrity Check",
                f"No files are selected. Check integrity of all {len(self.files)} files in the results?",
                QMessageBox.Yes | QMessageBox.No
            )
            if confirm != QMessageBox.Yes:
                return
            selected_files = self.files
            dialog_title = f"Check Integrity of All {len(self.files)} Files"
        else:
            QMessageBox.information(self, "No Files", "No files available to check. Please search for files first.")
            return
        
        from security_dialog import SecurityDialog
        dialog = SecurityDialog(selected_files, self, integrity_mode=True)
        dialog.setWindowTitle(dialog_title)
        dialog.exec()
    
    def open_usage_analytics(self):
        """Open usage analytics dialog"""
        from usage_analytics_dialog import UsageAnalyticsDialog
        dialog = UsageAnalyticsDialog(self.usage_analytics, self.files, self)
        dialog.exec()
    
    def show_performance_report(self):
        """Show performance report dialog"""
        from performance_dialog import PerformanceDialog
        dialog = PerformanceDialog(self.performance_optimizer, self)
        dialog.exec()
    
    def clear_performance_cache(self):
        """Clear performance cache"""
        cleared_entries = self.performance_optimizer.clear_cache()
        QMessageBox.information(
            self, "Cache Cleared",
            f"Performance cache cleared.\nMemory optimization performed."
        )
