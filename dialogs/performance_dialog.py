from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox,
    QTabWidget, QWidget, QTextEdit, QProgressBar, QFormLayout,
    QSpinBox, QCheckBox, QMessageBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from pathlib import Path
import time

class PerformanceDialog(QDialog):
    """Dialog for viewing and managing performance metrics"""
    
    def __init__(self, performance_optimizer, parent=None):
        super().__init__(parent)
        self.performance_optimizer = performance_optimizer
        self.setWindowTitle("Performance Monitor")
        self.setModal(True)
        self.resize(800, 600)
        
        # Timer for real-time updates
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.refresh_data)
        self.update_timer.start(5000)  # Update every 5 seconds
        
        self.setup_ui()
        self.refresh_data()
    
    def setup_ui(self):
        """Set up the user interface"""
        layout = QVBoxLayout(self)
        
        # Create tab widget
        tab_widget = QTabWidget()
        
        # Performance Overview Tab
        overview_tab = QWidget()
        overview_layout = QVBoxLayout(overview_tab)
        
        # Current status
        status_group = QGroupBox("Current Performance")
        status_layout = QFormLayout(status_group)
        
        self.memory_label = QLabel("0 MB")
        self.cpu_label = QLabel("0%")
        self.cache_efficiency_label = QLabel("0%")
        
        status_layout.addRow("Memory Usage:", self.memory_label)
        status_layout.addRow("CPU Usage:", self.cpu_label)
        status_layout.addRow("Cache Efficiency:", self.cache_efficiency_label)
        
        overview_layout.addWidget(status_group)
        
        # Recommendations
        recommendations_group = QGroupBox("Performance Recommendations")
        recommendations_layout = QVBoxLayout(recommendations_group)
        
        self.recommendations_text = QTextEdit()
        self.recommendations_text.setMaximumHeight(150)
        self.recommendations_text.setReadOnly(True)
        recommendations_layout.addWidget(self.recommendations_text)
        
        overview_layout.addWidget(recommendations_group)
        
        # Quick actions
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QHBoxLayout(actions_group)
        
        clear_cache_btn = QPushButton("Clear Cache")
        clear_cache_btn.clicked.connect(self.clear_cache)
        
        optimize_memory_btn = QPushButton("Optimize Memory")
        optimize_memory_btn.clicked.connect(self.optimize_memory)
        
        refresh_btn = QPushButton("Refresh Data")
        refresh_btn.clicked.connect(self.refresh_data)
        
        actions_layout.addWidget(clear_cache_btn)
        actions_layout.addWidget(optimize_memory_btn)
        actions_layout.addWidget(refresh_btn)
        actions_layout.addStretch()
        
        overview_layout.addWidget(actions_group)
        overview_layout.addStretch()
        
        tab_widget.addTab(overview_tab, "Overview")
        
        # Detailed Metrics Tab
        metrics_tab = QWidget()
        metrics_layout = QVBoxLayout(metrics_tab)
        
        # Scan history
        scan_history_group = QGroupBox("Recent Scans")
        scan_history_layout = QVBoxLayout(scan_history_group)
        
        self.scan_history_table = QTableWidget()
        self.scan_history_table.setColumnCount(4)
        self.scan_history_table.setHorizontalHeaderLabels([
            "Directory", "File Count", "Scan Time (s)", "Time per File (ms)"
        ])
        self.scan_history_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        scan_history_layout.addWidget(self.scan_history_table)
        
        metrics_layout.addWidget(scan_history_group)
        
        # Cache statistics
        cache_stats_group = QGroupBox("Cache Statistics")
        cache_stats_layout = QFormLayout(cache_stats_group)
        
        self.cache_hits_label = QLabel("0")
        self.cache_misses_label = QLabel("0")
        self.cache_size_label = QLabel("0")
        
        cache_stats_layout.addRow("Cache Hits:", self.cache_hits_label)
        cache_stats_layout.addRow("Cache Misses:", self.cache_misses_label)
        cache_stats_layout.addRow("Cache Size:", self.cache_size_label)
        
        metrics_layout.addWidget(cache_stats_group)
        
        tab_widget.addTab(metrics_tab, "Detailed Metrics")
        
        # Settings Tab
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)
        
        # Cache settings
        cache_settings_group = QGroupBox("Cache Settings")
        cache_settings_layout = QFormLayout(cache_settings_group)
        
        self.cache_timeout_spin = QSpinBox()
        self.cache_timeout_spin.setRange(60, 3600)
        self.cache_timeout_spin.setValue(self.performance_optimizer.cache_timeout)
        self.cache_timeout_spin.setSuffix(" seconds")
        
        self.max_cache_size_spin = QSpinBox()
        self.max_cache_size_spin.setRange(100, 10000)
        self.max_cache_size_spin.setValue(self.performance_optimizer.max_cache_size)
        self.max_cache_size_spin.setSuffix(" entries")
        
        cache_settings_layout.addRow("Cache Timeout:", self.cache_timeout_spin)
        cache_settings_layout.addRow("Max Cache Size:", self.max_cache_size_spin)
        
        # Apply settings button
        apply_settings_btn = QPushButton("Apply Settings")
        apply_settings_btn.clicked.connect(self.apply_settings)
        cache_settings_layout.addRow("", apply_settings_btn)
        
        settings_layout.addWidget(cache_settings_group)
        
        # Monitoring settings
        monitoring_group = QGroupBox("Monitoring")
        monitoring_layout = QVBoxLayout(monitoring_group)
        
        self.enable_monitoring_check = QCheckBox("Enable real-time monitoring")
        self.enable_monitoring_check.setChecked(self.performance_optimizer.monitoring_enabled)
        self.enable_monitoring_check.toggled.connect(self.toggle_monitoring)
        
        monitoring_layout.addWidget(self.enable_monitoring_check)
        settings_layout.addWidget(monitoring_group)
        
        settings_layout.addStretch()
        
        tab_widget.addTab(settings_tab, "Settings")
        
        layout.addWidget(tab_widget)
        
        # Dialog buttons
        button_layout = QHBoxLayout()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def refresh_data(self):
        """Refresh all performance data"""
        report = self.performance_optimizer.get_performance_report()
        
        # Update overview
        memory = report["memory_usage"]
        cpu = report["cpu_usage"]
        
        self.memory_label.setText(f"{memory['current']:.1f} MB")
        self.cpu_label.setText(f"{cpu['current']:.1f}%")
        self.cache_efficiency_label.setText(f"{report['cache_efficiency']:.1f}%")
        
        # Update recommendations
        recommendations = "\n".join(f"• {rec}" for rec in report["recommendations"])
        self.recommendations_text.setPlainText(recommendations)
        
        # Update scan history
        scan_times = self.performance_optimizer.performance_stats["scan_times"]
        self.scan_history_table.setRowCount(len(scan_times))
        
        for row, scan in enumerate(reversed(scan_times[-10:])):  # Show last 10
            directory = Path(scan["directory"]).name
            file_count = scan["file_count"]
            scan_time = scan["scan_time"]
            time_per_file = (scan_time / file_count * 1000) if file_count > 0 else 0
            
            self.scan_history_table.setItem(row, 0, QTableWidgetItem(directory))
            self.scan_history_table.setItem(row, 1, QTableWidgetItem(str(file_count)))
            self.scan_history_table.setItem(row, 2, QTableWidgetItem(f"{scan_time:.2f}"))
            self.scan_history_table.setItem(row, 3, QTableWidgetItem(f"{time_per_file:.2f}"))
        
        # Update cache statistics
        stats = self.performance_optimizer.performance_stats
        self.cache_hits_label.setText(str(stats["cache_hits"]))
        self.cache_misses_label.setText(str(stats["cache_misses"]))
        self.cache_size_label.setText(str(len(self.performance_optimizer.scan_cache)))
    
    def clear_cache(self):
        """Clear performance cache"""
        self.performance_optimizer.clear_cache()
        self.refresh_data()
        QMessageBox.information(self, "Cache Cleared", "Performance cache has been cleared.")
    
    def optimize_memory(self):
        """Optimize memory usage"""
        cleared_entries = self.performance_optimizer.optimize_memory_usage()
        self.refresh_data()
        QMessageBox.information(
            self, "Memory Optimized", 
            f"Memory optimization completed.\nCleared {cleared_entries} expired cache entries."
        )
    
    def apply_settings(self):
        """Apply performance settings"""
        self.performance_optimizer.cache_timeout = self.cache_timeout_spin.value()
        self.performance_optimizer.max_cache_size = self.max_cache_size_spin.value()
        QMessageBox.information(self, "Settings Applied", "Performance settings have been updated.")
    
    def toggle_monitoring(self, enabled):
        """Toggle performance monitoring"""
        if enabled:
            self.performance_optimizer.start_monitoring()
        else:
            self.performance_optimizer.stop_monitoring()
    
    def closeEvent(self, event):
        """Handle dialog close"""
        self.update_timer.stop()
        super().closeEvent(event)
