from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox,
    QTabWidget, QWidget, QTextEdit, QProgressBar, QFormLayout,
    QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from pathlib import Path
from core.utils import format_size
import time
from datetime import datetime, timedelta

class UsageAnalyticsDialog(QDialog):
    """Dialog for viewing file usage analytics and storage insights"""
    
    def __init__(self, usage_analytics, files, parent=None):
        super().__init__(parent)
        self.usage_analytics = usage_analytics
        self.files = files
        self.setWindowTitle("Usage Analytics")
        self.setModal(True)
        self.resize(900, 700)
        
        # Timer for real-time updates
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.refresh_data)
        self.update_timer.start(10000)  # Update every 10 seconds
        
        self.setup_ui()
        self.refresh_data()
    
    def setup_ui(self):
        """Set up the user interface"""
        layout = QVBoxLayout(self)
        
        # Create tab widget
        tab_widget = QTabWidget()
        
        # Overview Tab
        overview_tab = QWidget()
        overview_layout = QVBoxLayout(overview_tab)
        
        # Storage overview
        storage_group = QGroupBox("Storage Overview")
        storage_layout = QFormLayout(storage_group)
        
        self.total_files_label = QLabel("0")
        self.total_size_label = QLabel("0 B")
        self.avg_file_size_label = QLabel("0 B")
        self.largest_file_label = QLabel("None")
        
        storage_layout.addRow("Total Files Scanned:", self.total_files_label)
        storage_layout.addRow("Total Size:", self.total_size_label)
        storage_layout.addRow("Average File Size:", self.avg_file_size_label)
        storage_layout.addRow("Largest File:", self.largest_file_label)
        
        overview_layout.addWidget(storage_group)
        
        # Usage statistics
        usage_group = QGroupBox("Usage Statistics")
        usage_layout = QFormLayout(usage_group)
        
        self.accessed_files_label = QLabel("0")
        self.never_accessed_label = QLabel("0")
        self.recent_access_label = QLabel("0")
        self.storage_cost_label = QLabel("$0.00")
        
        usage_layout.addRow("Files Accessed:", self.accessed_files_label)
        usage_layout.addRow("Never Accessed:", self.never_accessed_label)
        usage_layout.addRow("Recently Accessed (7 days):", self.recent_access_label)
        usage_layout.addRow("Estimated Storage Cost (monthly):", self.storage_cost_label)
        
        overview_layout.addWidget(usage_group)
        
        # Recommendations
        recommendations_group = QGroupBox("Recommendations")
        recommendations_layout = QVBoxLayout(recommendations_group)
        
        self.recommendations_text = QTextEdit()
        self.recommendations_text.setMaximumHeight(150)
        self.recommendations_text.setReadOnly(True)
        recommendations_layout.addWidget(self.recommendations_text)
        
        overview_layout.addWidget(recommendations_group)
        overview_layout.addStretch()
        
        tab_widget.addTab(overview_tab, "Overview")
        
        # File Access Tab
        access_tab = QWidget()
        access_layout = QVBoxLayout(access_tab)
        
        # Most accessed files
        most_accessed_group = QGroupBox("Most Frequently Accessed Files")
        most_accessed_layout = QVBoxLayout(most_accessed_group)
        
        self.most_accessed_table = QTableWidget()
        self.most_accessed_table.setColumnCount(4)
        self.most_accessed_table.setHorizontalHeaderLabels([
            "File Name", "Access Count", "Last Accessed", "Size"
        ])
        self.most_accessed_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.most_accessed_table.setMaximumHeight(200)
        most_accessed_layout.addWidget(self.most_accessed_table)
        
        access_layout.addWidget(most_accessed_group)
        
        # Least accessed files
        least_accessed_group = QGroupBox("Rarely Accessed Large Files (Cleanup Candidates)")
        least_accessed_layout = QVBoxLayout(least_accessed_group)
        
        self.least_accessed_table = QTableWidget()
        self.least_accessed_table.setColumnCount(4)
        self.least_accessed_table.setHorizontalHeaderLabels([
            "File Name", "Size", "Last Modified", "Path"
        ])
        self.least_accessed_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.least_accessed_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        least_accessed_layout.addWidget(self.least_accessed_table)
        
        access_layout.addWidget(least_accessed_group)
        
        tab_widget.addTab(access_tab, "File Access")
        
        # Storage Analysis Tab
        storage_tab = QWidget()
        storage_layout = QVBoxLayout(storage_tab)
        
        # File type breakdown
        breakdown_group = QGroupBox("Storage Breakdown by File Type")
        breakdown_layout = QVBoxLayout(breakdown_group)
        
        self.breakdown_table = QTableWidget()
        self.breakdown_table.setColumnCount(4)
        self.breakdown_table.setHorizontalHeaderLabels([
            "File Type", "File Count", "Total Size", "Percentage"
        ])
        self.breakdown_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        breakdown_layout.addWidget(self.breakdown_table)
        
        storage_layout.addWidget(breakdown_group)
        
        # Large files analysis
        large_files_group = QGroupBox("Largest Files")
        large_files_layout = QVBoxLayout(large_files_group)
        
        self.large_files_table = QTableWidget()
        self.large_files_table.setColumnCount(4)
        self.large_files_table.setHorizontalHeaderLabels([
            "File Name", "Size", "Type", "Path"
        ])
        self.large_files_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.large_files_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        large_files_layout.addWidget(self.large_files_table)
        
        storage_layout.addWidget(large_files_group)
        
        tab_widget.addTab(storage_tab, "Storage Analysis")
        
        layout.addWidget(tab_widget)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        export_btn = QPushButton("Export Analytics Report")
        export_btn.clicked.connect(self.export_report)
        
        clear_data_btn = QPushButton("Clear Usage Data")
        clear_data_btn.clicked.connect(self.clear_usage_data)
        
        refresh_btn = QPushButton("Refresh Data")
        refresh_btn.clicked.connect(self.refresh_data)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        
        button_layout.addWidget(export_btn)
        button_layout.addWidget(clear_data_btn)
        button_layout.addWidget(refresh_btn)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def refresh_data(self):
        """Refresh all analytics data"""
        self.update_overview()
        self.update_file_access_tables()
        self.update_storage_analysis()
        self.update_recommendations()
    
    def update_overview(self):
        """Update the overview statistics"""
        if not self.files:
            return
        
        # Basic file statistics
        total_files = len(self.files)
        total_size = sum(f.size for f in self.files)
        avg_size = total_size / total_files if total_files > 0 else 0
        largest_file = max(self.files, key=lambda f: f.size) if self.files else None
        
        self.total_files_label.setText(str(total_files))
        self.total_size_label.setText(format_size(total_size))
        self.avg_file_size_label.setText(format_size(avg_size))
        self.largest_file_label.setText(largest_file.name if largest_file else "None")
        
        # Usage statistics (now using get_access_statistics)
        stats = self.usage_analytics.get_access_statistics()
        self.accessed_files_label.setText(str(stats["accessed_files"]))
        self.never_accessed_label.setText(str(stats["never_accessed"]))
        # Recent access (last 7 days)
        cutoff_date = datetime.now() - timedelta(days=7)
        recent_access = 0
        for file_path, data in self.usage_analytics.usage_data.items():
            if data["last_accessed"]:
                try:
                    last_access = data["last_accessed"]
                    if isinstance(last_access, str):
                        last_access = datetime.fromisoformat(last_access)
                    if last_access > cutoff_date:
                        recent_access += 1
                except (ValueError, TypeError):
                    pass
        self.recent_access_label.setText(str(recent_access))
        # Storage cost calculation
        storage_cost = self.usage_analytics.get_storage_cost()
        self.storage_cost_label.setText(f"${storage_cost:.2f}")
        # Optionally show access rate
        self.total_files_label.setToolTip(f"Access rate: {stats['access_rate']:.1f}%")
    
    def update_file_access_tables(self):
        """Update the file access tables"""
        # Most accessed files
        frequently_accessed = self.usage_analytics.get_frequently_accessed(10)
        self.most_accessed_table.setRowCount(len(frequently_accessed))
        
        for row, (file_path, data) in enumerate(frequently_accessed):
            file_name = Path(file_path).name
            access_count = data["access_count"]
            last_accessed = data["last_accessed"] or "Never"
            if last_accessed != "Never":
                try:
                    dt = datetime.fromisoformat(last_accessed)
                    last_accessed = dt.strftime("%Y-%m-%d %H:%M")
                except (ValueError, TypeError):
                    last_accessed = "Unknown"
            
            # Find file size
            file_size = "Unknown"
            for file_info in self.files:
                if file_info.path == file_path:
                    file_size = file_info.get_size_str()
                    break
            
            self.most_accessed_table.setItem(row, 0, QTableWidgetItem(file_name))
            self.most_accessed_table.setItem(row, 1, QTableWidgetItem(str(access_count)))
            self.most_accessed_table.setItem(row, 2, QTableWidgetItem(last_accessed))
            self.most_accessed_table.setItem(row, 3, QTableWidgetItem(file_size))
        
        # Cleanup candidates (large files, rarely accessed)
        cleanup_candidates = self._get_cleanup_candidates()
        self.least_accessed_table.setRowCount(len(cleanup_candidates))
        
        for row, file_info in enumerate(cleanup_candidates):
            self.least_accessed_table.setItem(row, 0, QTableWidgetItem(file_info.name))
            self.least_accessed_table.setItem(row, 1, QTableWidgetItem(file_info.get_size_str()))
            self.least_accessed_table.setItem(row, 2, QTableWidgetItem(
                file_info.modified_date.strftime("%Y-%m-%d %H:%M")
            ))
            self.least_accessed_table.setItem(row, 3, QTableWidgetItem(file_info.path))
    
    def update_storage_analysis(self):
        """Update the storage analysis tables"""
        # File type breakdown
        type_breakdown = self._calculate_type_breakdown()
        self.breakdown_table.setRowCount(len(type_breakdown))
        
        total_size = sum(data["size"] for data in type_breakdown.values())
        
        for row, (file_type, data) in enumerate(sorted(
            type_breakdown.items(), 
            key=lambda x: x[1]["size"], 
            reverse=True
        )):
            count = data["count"]
            size = data["size"]
            percentage = (size / total_size * 100) if total_size > 0 else 0
            
            self.breakdown_table.setItem(row, 0, QTableWidgetItem(file_type))
            self.breakdown_table.setItem(row, 1, QTableWidgetItem(str(count)))
            self.breakdown_table.setItem(row, 2, QTableWidgetItem(format_size(size)))
            self.breakdown_table.setItem(row, 3, QTableWidgetItem(f"{percentage:.1f}%"))
        
        # Largest files
        largest_files = sorted(self.files, key=lambda f: f.size, reverse=True)[:20]
        self.large_files_table.setRowCount(len(largest_files))
        
        for row, file_info in enumerate(largest_files):
            self.large_files_table.setItem(row, 0, QTableWidgetItem(file_info.name))
            self.large_files_table.setItem(row, 1, QTableWidgetItem(file_info.get_size_str()))
            self.large_files_table.setItem(row, 2, QTableWidgetItem(file_info.extension.upper()))
            self.large_files_table.setItem(row, 3, QTableWidgetItem(file_info.path))
    
    def update_recommendations(self):
        """Update storage optimization recommendations"""
        recommendations = []
        # Use access statistics for recommendations
        stats = self.usage_analytics.get_access_statistics()
        if stats["total_files"] > 0:
            recommendations.append(
                f"📈 {stats['access_rate']:.1f}% of files have been accessed at least once."
            )
            if stats["never_accessed"] > 0:
                recommendations.append(
                    f"🔍 {stats['never_accessed']} files have never been accessed - consider archiving or removing them"
                )
        
        # Analyze cleanup potential
        cleanup_candidates = self._get_cleanup_candidates()
        if cleanup_candidates:
            total_cleanup_size = sum(f.size for f in cleanup_candidates)
            recommendations.append(
                f"🗑️ Consider removing {len(cleanup_candidates)} rarely accessed large files "
                f"to save {format_size(total_cleanup_size)}"
            )
        
        # Analyze file types
        type_breakdown = self._calculate_type_breakdown()
        if type_breakdown:
            largest_type = max(type_breakdown.items(), key=lambda x: x[1]["size"])
            recommendations.append(
                f"📊 {largest_type[0]} files take up the most space: "
                f"{format_size(largest_type[1]['size'])} ({largest_type[1]['count']} files)"
            )
        
        # Storage cost analysis
        storage_cost = self.usage_analytics.get_storage_cost()
        if storage_cost > 10:  # $10 threshold
            recommendations.append(
                f"💰 Monthly storage cost is ${storage_cost:.2f} - consider cloud archiving for old files"
            )
        
        # Duplicate file potential
        extensions = {}
        for file_info in self.files:
            ext = file_info.extension.lower()
            if ext:
                extensions[ext] = extensions.get(ext, 0) + 1
        
        duplicate_prone = [ext for ext, count in extensions.items() if count > 50]
        if duplicate_prone:
            recommendations.append(
                f"🔍 High file counts for {', '.join(duplicate_prone[:3])} files - check for duplicates"
            )
        
        if not recommendations:
            recommendations.append("✅ Your file organization looks good! Keep up the great work.")
        
        self.recommendations_text.setPlainText("\n\n".join(f"• {rec}" for rec in recommendations))
    
    def _get_cleanup_candidates(self):
        """Get files that are candidates for cleanup (large, rarely accessed)"""
        candidates = []
        usage_data = self.usage_analytics.usage_data
        
        for file_info in self.files:
            # Only consider files larger than 50MB
            if file_info.size < 50 * 1024 * 1024:
                continue
            
            # Check access history
            file_usage = usage_data.get(file_info.path, {"access_count": 0, "last_accessed": None})
            
            # Never accessed or not accessed in 30 days
            is_candidate = False
            if file_usage["access_count"] == 0:
                is_candidate = True
            elif file_usage["last_accessed"]:
                try:
                    last_access = datetime.fromisoformat(file_usage["last_accessed"])
                    cutoff_date = datetime.now() - timedelta(days=30)
                    if last_access < cutoff_date:
                        is_candidate = True
                except (ValueError, TypeError):
                    is_candidate = True
            
            if is_candidate:
                candidates.append(file_info)
        
        # Sort by size (largest first) and limit to top 20
        return sorted(candidates, key=lambda f: f.size, reverse=True)[:20]
    
    def _calculate_type_breakdown(self):
        """Calculate storage breakdown by file type"""
        breakdown = {}
        
        for file_info in self.files:
            file_type = file_info.extension.upper() if file_info.extension else "No Extension"
            
            if file_type not in breakdown:
                breakdown[file_type] = {"count": 0, "size": 0}
            
            breakdown[file_type]["count"] += 1
            breakdown[file_type]["size"] += file_info.size
        
        return breakdown
    
    def export_report(self):
        """Export analytics report to file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Analytics Report",
            str(Path.home() / "usage_analytics_report.txt"),
            "Text Files (*.txt)"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("USAGE ANALYTICS REPORT\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Overview
                f.write("STORAGE OVERVIEW\n")
                f.write("-" * 20 + "\n")
                f.write(f"Total Files: {self.total_files_label.text()}\n")
                f.write(f"Total Size: {self.total_size_label.text()}\n")
                f.write(f"Average File Size: {self.avg_file_size_label.text()}\n")
                f.write(f"Largest File: {self.largest_file_label.text()}\n\n")
                
                # Usage stats
                f.write("USAGE STATISTICS\n")
                f.write("-" * 20 + "\n")
                f.write(f"Files Accessed: {self.accessed_files_label.text()}\n")
                f.write(f"Never Accessed: {self.never_accessed_label.text()}\n")
                f.write(f"Recently Accessed: {self.recent_access_label.text()}\n")
                f.write(f"Storage Cost: {self.storage_cost_label.text()}\n\n")
                
                # Recommendations
                f.write("RECOMMENDATIONS\n")
                f.write("-" * 20 + "\n")
                f.write(self.recommendations_text.toPlainText())
                f.write("\n\n")
                
                # File type breakdown
                f.write("FILE TYPE BREAKDOWN\n")
                f.write("-" * 20 + "\n")
                for row in range(self.breakdown_table.rowCount()):
                    file_type = self.breakdown_table.item(row, 0).text()
                    count = self.breakdown_table.item(row, 1).text()
                    size = self.breakdown_table.item(row, 2).text()
                    percentage = self.breakdown_table.item(row, 3).text()
                    f.write(f"{file_type}: {count} files, {size} ({percentage})\n")
            
            QMessageBox.information(
                self, "Report Exported",
                f"Analytics report exported to:\n{file_path}"
            )
            
        except Exception as e:
            QMessageBox.warning(
                self, "Export Failed",
                f"Failed to export report:\n{str(e)}"
            )
    
    def clear_usage_data(self):
        """Clear all usage tracking data"""
        confirm = QMessageBox.question(
            self, "Clear Usage Data",
            "Are you sure you want to clear all usage tracking data?\n\n"
            "This will reset access counts and timestamps for all files.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            self.usage_analytics.usage_data.clear()
            self.refresh_data()
            QMessageBox.information(
                self, "Data Cleared",
                "Usage tracking data has been cleared."
            )
    
    def closeEvent(self, event):
        """Handle dialog close"""
        self.update_timer.stop()
        super().closeEvent(event)
