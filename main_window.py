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
from core.file_category import FileCategory
from scanners.file_scanner_thread import FileScannerThread
from dialogs.settings_dialog import SettingsDialog
from core.config_manager import ConfigManager
from services.theme_manager import theme_manager
from managers.bookmark_manager import BookmarkManager
from preview_panel import PreviewPanel
from managers.search_history_manager import SearchHistoryManager
from managers.usage_analytics import UsageAnalytics
from scanners.performance_optimizer import PerformanceOptimizer
from actions.batch_rename_dialog import BatchRenameDialog
from actions.file_actions import FileActions
from actions.search_manager import SearchManager
from actions.results_manager import ResultsManager
from actions.bookmark_actions import BookmarkActions
from actions.dialog_manager import DialogManager
from managers.ui_manager import UIManager

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
        
        # Initialize results manager (will be created after setup_ui)
        self.results_manager = None
        
        # Initialize search manager (will be created after results_manager)
        self.search_manager = None
        
        # Apply saved theme
        saved_theme = self.app_settings.get("theme_internal", "light")
        theme_manager.apply_theme(saved_theme)
        
        # Create results table before managers
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(6)
        self.results_table.setHorizontalHeaderLabels(["Name", "Path", "Size", "Type", "Modified", "Category"])
        self.results_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.results_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.results_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.results_table.setSortingEnabled(True)
        self.results_table.setAlternatingRowColors(True)
        
        # Create managers before UI setup so UI can connect to their methods
        self.results_manager = ResultsManager(self, self.results_table, self.files)
        self.search_manager = SearchManager(self, self.results_manager)
        
        # Initialize remaining managers
        self.bookmark_actions = BookmarkActions(self)
        self.dialog_manager = DialogManager(self)
        self.ui_manager = UIManager(self)
        
        # Now connect the context menu after dialog_manager is created
        self.results_table.customContextMenuRequested.connect(self.dialog_manager.show_context_menu)
        
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
            btn.clicked.connect(lambda checked, idx=i: self.bookmark_actions.use_quick_bookmark(idx))
            self.bookmark_buttons.append(btn)
            bookmarks_layout.addWidget(btn)

        # Manage bookmarks button
        manage_bookmarks_btn = QPushButton("Manage Bookmarks...")
        manage_bookmarks_btn.clicked.connect(self.bookmark_actions.open_bookmark_manager)
        bookmarks_layout.addWidget(manage_bookmarks_btn)
        
        # Quick save buttons
        pixmap = QStyle.SP_DirIcon
        save_location_icon = self.style().standardIcon(pixmap)
        save_location_btn = QPushButton(save_location_icon, " Save Location")
        save_location_btn.setToolTip("Save current directory as bookmark")
        save_location_btn.clicked.connect(self.bookmark_actions.quick_save_location)
        
        pixmap = QStyle.SP_DialogSaveButton
        save_search_icon = self.style().standardIcon(pixmap)
        save_search_btn = QPushButton(save_search_icon, " Save Search")
        save_search_btn.setToolTip("Save current search settings as preset")
        save_search_btn.clicked.connect(self.bookmark_actions.quick_save_search)
        
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
        browse_button.clicked.connect(self.search_manager.browse_directory)
        
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
        
        # Include hidden files checkbox
        self.include_hidden = QCheckBox("Hidden")
        self.include_hidden.setToolTip("Include hidden files and folders (starting with '.')")
        self.include_hidden.setChecked(self.app_settings.get("scan_hidden", False))
        main_search_layout.addWidget(self.include_hidden)
        
        # Search button
        self.search_button = QPushButton("Search Files")
        self.search_button.clicked.connect(self.search_manager.start_search)

        main_search_layout.addWidget(self.search_button)
        
        # Add pause/resume button
        self.pause_button = QPushButton("Pause")
        self.pause_button.clicked.connect(self.search_manager.toggle_pause_scan)
        self.pause_button.setEnabled(False)
        main_search_layout.addWidget(self.pause_button)
        
        # Add stop button
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.search_manager.stop_scan)
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
        self.date_filter_enabled.toggled.connect(self.ui_manager.toggle_date_filter)
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
        self.pattern_filter_enabled.toggled.connect(self.ui_manager.toggle_pattern_filter)
        pattern_layout.addWidget(self.pattern_filter_enabled)
        
        self.pattern_edit = QLineEdit()
        self.pattern_edit.setPlaceholderText("e.g., IMG_\\d{4}, .*\\.backup\\..*, ^test.*\\.py$")
        self.pattern_edit.setEnabled(False)
        pattern_layout.addWidget(self.pattern_edit)
        
        advanced_layout.addLayout(pattern_layout)
        
        # Content search filter
        content_layout = QHBoxLayout()
        self.content_filter_enabled = QCheckBox("Content search (text files only)")
        self.content_filter_enabled.toggled.connect(self.ui_manager.toggle_content_filter)
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
        self.clear_filters_button.clicked.connect(self.ui_manager.clear_advanced_filters)
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
        
        # Connect selection change to preview
        self.results_table.selectionModel().selectionChanged.connect(self.results_manager.on_file_selection_changed)
        
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
    
    def create_actions(self):
        """Create application actions"""
        # File menu actions
        self.open_action = QAction("Open", self)
        self.open_action.triggered.connect(self.file_actions.open_selected_file)
        
        self.open_containing_folder_action = QAction("Open Containing Folder", self)
        self.open_containing_folder_action.triggered.connect(self.file_actions.open_containing_folder)
        
        # Edit menu actions
        self.settings_action = QAction("Settings", self)
        self.settings_action.triggered.connect(self.dialog_manager.open_settings)
        
        # Actions menu
        self.delete_action = QAction("Delete Selected Files", self)
        self.delete_action.triggered.connect(self.file_actions.delete_selected_files)
        
        self.rename_action = QAction("Rename File", self)
        self.rename_action.triggered.connect(self.file_actions.rename_file)
        
        self.batch_rename_action = QAction("Batch Rename...", self)
        self.batch_rename_action.triggered.connect(self.file_actions.batch_rename_files)
        
        self.move_action = QAction("Move to Directory...", self)
        self.move_action.triggered.connect(self.file_actions.move_selected_files)

        self.duplicate_action = QAction("Find Duplicates...", self)
        self.duplicate_action.triggered.connect(self.dialog_manager.find_duplicates)
        
        # Export action
        self.export_action = QAction("Export Results to CSV", self)
        self.export_action.triggered.connect(self.results_manager.export_results)
        
        # Help menu actions
        self.about_action = QAction("About", self)
        self.about_action.triggered.connect(self.dialog_manager.show_about)
        
        # Bookmark actions
        self.bookmark_manager_action = QAction("Manage Bookmarks...", self)
        self.bookmark_manager_action.triggered.connect(self.bookmark_actions.open_bookmark_manager)
        
        # View menu actions
        self.toggle_preview_action = QAction("Toggle Preview Panel", self)
        self.toggle_preview_action.setCheckable(True)
        self.toggle_preview_action.setChecked(True)
        self.toggle_preview_action.triggered.connect(self.ui_manager.toggle_preview_panel)
        
        # Search history actions
        self.search_history_action = QAction("Search History...", self)
        self.search_history_action.triggered.connect(self.dialog_manager.open_search_history)
        
        # Security actions
        self.security_scan_action = QAction("Security Scan...", self)
        self.security_scan_action.triggered.connect(self.dialog_manager.run_security_scan)
        
        self.file_integrity_action = QAction("Check File Integrity...", self)
        self.file_integrity_action.triggered.connect(self.dialog_manager.check_file_integrity)
        
        # Usage analytics actions
        self.usage_analytics_action = QAction("Usage Analytics...", self)
        self.usage_analytics_action.triggered.connect(self.dialog_manager.open_usage_analytics)
        
        # Performance actions
        self.performance_report_action = QAction("Performance Report...", self)
        self.performance_report_action.triggered.connect(self.dialog_manager.show_performance_report)
        
        self.clear_cache_action = QAction("Clear Cache", self)
        self.clear_cache_action.triggered.connect(self.performance_optimizer.clear_cache)
    
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

    def closeEvent(self, event):
        """Handle window close event"""
        # Stop performance monitoring
        self.performance_optimizer.stop_monitoring()
        
        # Save current settings before closing
        self.app_settings["last_directory"] = self.current_directory
        self.config_manager.save_settings(self.app_settings)
        print("Settings saved before closing.")
        super().closeEvent(event)
    
    def clear_performance_cache(self):
        """Clear performance cache"""
        cleared_entries = self.performance_optimizer.clear_cache()
        QMessageBox.information(
            self, "Cache Cleared",
            f"Performance cache cleared.\nMemory optimization performed."
        )
