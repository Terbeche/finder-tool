from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox,
    QTabWidget, QWidget, QTextEdit, QFormLayout, QSpinBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import os
from pathlib import Path

class UsageAnalyticsDialog(QDialog):
    """Dialog for viewing usage analytics and insights"""
    
    def __init__(self, usage_analytics, files, parent=None):
        super().__init__(parent)
        self.usage_analytics = usage_analytics
        self.files = files
        self.setWindowTitle("Usage Analytics")
        self.setModal(True)
        self.resize(800, 600)
        self.setup_ui()
        self.refresh_data()
    
    def setup_ui(self):
        """Set up the user interface"""
        layout = QVBoxLayout(self)
        
        # Create tab widget
        tab_widget = QTabWidget()
        
        # Frequently Accessed Tab
        frequent_tab = QWidget()
        frequent_layout = QVBoxLayout(frequent_tab)
        
        # Controls
        controls_layout = QHBoxLayout()
        self.frequent_limit = QSpinBox()
        self.frequent_limit.setRange(5, 100)
        self.frequent_limit.setValue(20)
        self.frequent_limit.valueChanged.connect(self.refresh_frequent_files)
        controls_layout.addWidget(QLabel("Show top:"))
        controls_layout.addWidget(self.frequent_limit)
        controls_layout.addWidget(QLabel("files"))
        controls_layout.addStretch()
        frequent_layout.addLayout(controls_layout)
        
        # Frequently accessed files table
        self.frequent_table = QTableWidget()
        self.frequent_table.setColumnCount(4)
        self.frequent_table.setHorizontalHeaderLabels([
            "File Name", "Path", "Access Count", "Last Accessed"
        ])
        self.frequent_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.frequent_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.frequent_table.setAlternatingRowColors(True)
        frequent_layout.addWidget(self.frequent_table)
        
        tab_widget.addTab(frequent_tab, "Frequently Accessed")
        
        # Cleanup Suggestions Tab
        cleanup_tab = QWidget()
        cleanup_layout = QVBoxLayout(cleanup_tab)
        
        # Controls
        cleanup_controls_layout = QHBoxLayout()
        self.cleanup_limit = QSpinBox()
        self.cleanup_limit.setRange(5, 100)
        self.cleanup_limit.setValue(20)
        self.cleanup_limit.valueChanged.connect(self.refresh_cleanup_suggestions)
        cleanup_controls_layout.addWidget(QLabel("Show top:"))
        cleanup_controls_layout.addWidget(self.cleanup_limit)
        cleanup_controls_layout.addWidget(QLabel("files for cleanup"))
        cleanup_controls_layout.addStretch()
        cleanup_layout.addLayout(cleanup_controls_layout)
        
        # Cleanup suggestions table
        self.cleanup_table = QTableWidget()
        self.cleanup_table.setColumnCount(5)
        self.cleanup_table.setHorizontalHeaderLabels([
            "File Name", "Path", "Size", "Access Count", "Cleanup Priority"
        ])
        self.cleanup_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.cleanup_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.cleanup_table.setAlternatingRowColors(True)
        cleanup_layout.addWidget(self.cleanup_table)
        
        tab_widget.addTab(cleanup_tab, "Cleanup Suggestions")
        
        # Storage Analysis Tab
        storage_tab = QWidget()
        storage_layout = QVBoxLayout(storage_tab)
        
        # Storage cost configuration
        cost_group = QGroupBox("Storage Cost Configuration")
        cost_layout = QFormLayout(cost_group)
        
        self.cost_per_gb = QSpinBox()
        self.cost_per_gb.setRange(1, 1000)
        self.cost_per_gb.setValue(10)  # 10 cents per GB
        self.cost_per_gb.setSuffix(" cents/GB")
        self.cost_per_gb.valueChanged.connect(self.refresh_storage_analysis)
        cost_layout.addRow("Storage Cost:", self.cost_per_gb)
        
        storage_layout.addWidget(cost_group)
        
        # Storage analysis display
        analysis_group = QGroupBox("Storage Analysis")
        analysis_layout = QVBoxLayout(analysis_group)
        
        self.storage_analysis_text = QTextEdit()
        self.storage_analysis_text.setReadOnly(True)
        self.storage_analysis_text.setMaximumHeight(200)
        analysis_layout.addWidget(self.storage_analysis_text)
        
        storage_layout.addWidget(analysis_group)
        
        # Category breakdown table
        category_group = QGroupBox("Storage by Category")
        category_layout = QVBoxLayout(category_group)
        
        self.category_table = QTableWidget()
        self.category_table.setColumnCount(4)
        self.category_table.setHorizontalHeaderLabels([
            "Category", "File Count", "Total Size", "Average Access"
        ])
        self.category_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.category_table.setAlternatingRowColors(True)
        category_layout.addWidget(self.category_table)
        
        storage_layout.addWidget(category_group)
        storage_layout.addStretch()
        
        tab_widget.addTab(storage_tab, "Storage Analysis")
        
        layout.addWidget(tab_widget)
        
        # Dialog buttons
        button_layout = QHBoxLayout()
        
        refresh_button = QPushButton("Refresh Data")
        refresh_button.clicked.connect(self.refresh_data)
        
        export_button = QPushButton("Export Report")
        export_button.clicked.connect(self.export_report)
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        
        button_layout.addWidget(refresh_button)
        button_layout.addWidget(export_button)
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
    
    def refresh_data(self):
        """Refresh all analytics data"""
        self.refresh_frequent_files()
        self.refresh_cleanup_suggestions()
        self.refresh_storage_analysis()
    
    def refresh_frequent_files(self):
        """Refresh frequently accessed files table"""
        limit = self.frequent_limit.value()
        frequent_files = self.usage_analytics.get_frequently_accessed(limit)
        
        self.frequent_table.setRowCount(len(frequent_files))
        
        for row, (file_path, data) in enumerate(frequent_files):
            # File name
            name = os.path.basename(file_path)
            self.frequent_table.setItem(row, 0, QTableWidgetItem(name))
            
            # Path
            self.frequent_table.setItem(row, 1, QTableWidgetItem(file_path))
            
            # Access count
            count = str(data["access_count"])
            self.frequent_table.setItem(row, 2, QTableWidgetItem(count))
            
            # Last accessed
            last_accessed = "Never"
            if data["last_accessed"]:
                last_accessed = data["last_accessed"].strftime("%Y-%m-%d %H:%M")
            self.frequent_table.setItem(row, 3, QTableWidgetItem(last_accessed))
    
    def refresh_cleanup_suggestions(self):
        """Refresh cleanup suggestions table"""
        limit = self.cleanup_limit.value()
        
        # Calculate cleanup suggestions based on size vs access frequency
        cleanup_candidates = []
        
        for file_info in self.files:
            file_path = file_info.path
            usage_data = self.usage_analytics.usage_data.get(file_path, {"access_count": 0})
            
            # Calculate cleanup priority (larger files with fewer accesses = higher priority)
            if usage_data["access_count"] == 0:
                priority = file_info.size  # Never accessed files get priority by size
            else:
                priority = file_info.size / (usage_data["access_count"] + 1)
            
            cleanup_candidates.append((file_info, usage_data["access_count"], priority))
        
        # Sort by cleanup priority (highest first)
        cleanup_candidates.sort(key=lambda x: x[2], reverse=True)
        
        self.cleanup_table.setRowCount(min(len(cleanup_candidates), limit))
        
        for row, (file_info, access_count, priority) in enumerate(cleanup_candidates[:limit]):
            # File name
            self.cleanup_table.setItem(row, 0, QTableWidgetItem(file_info.name))
            
            # Path
            self.cleanup_table.setItem(row, 1, QTableWidgetItem(file_info.path))
            
            # Size
            self.cleanup_table.setItem(row, 2, QTableWidgetItem(file_info.get_size_str()))
            
            # Access count
            self.cleanup_table.setItem(row, 3, QTableWidgetItem(str(access_count)))
            
            # Priority (simplified)
            if access_count == 0:
                priority_text = "High (Never accessed)"
            elif access_count < 3:
                priority_text = "Medium (Rarely accessed)"
            else:
                priority_text = "Low (Frequently accessed)"
            
            self.cleanup_table.setItem(row, 4, QTableWidgetItem(priority_text))
    
    def refresh_storage_analysis(self):
        """Refresh storage analysis"""
        cost_per_gb = self.cost_per_gb.value() / 100.0  # Convert cents to dollars
        
        # Calculate total storage cost
        total_cost = self.usage_analytics.get_storage_cost(cost_per_gb)
        total_size = sum(f.size for f in self.files)
        total_size_gb = total_size / (1024 ** 3)
        
        # Calculate category breakdown
        category_stats = {}
        for file_info in self.files:
            category = file_info.category.name if file_info.category else "Uncategorized"
            if category not in category_stats:
                category_stats[category] = {"count": 0, "size": 0, "total_access": 0}
            
            category_stats[category]["count"] += 1
            category_stats[category]["size"] += file_info.size
            
            # Get access count for this file
            usage_data = self.usage_analytics.usage_data.get(file_info.path, {"access_count": 0})
            category_stats[category]["total_access"] += usage_data["access_count"]
        
        # Update storage analysis text
        analysis_text = f"""Storage Cost Analysis:
        
Total Files: {len(self.files):,}
Total Storage: {total_size_gb:.2f} GB
Estimated Monthly Cost: ${total_cost:.2f}

Cost Breakdown:
• Files with 0 accesses: {len([f for f in self.files if self.usage_analytics.usage_data.get(f.path, {}).get('access_count', 0) == 0])} files
• Files with 1-5 accesses: {len([f for f in self.files if 1 <= self.usage_analytics.usage_data.get(f.path, {}).get('access_count', 0) <= 5])} files
• Files with 6+ accesses: {len([f for f in self.files if self.usage_analytics.usage_data.get(f.path, {}).get('access_count', 0) > 5])} files

Optimization Suggestions:
• Consider archiving or deleting files with 0 accesses
• Move rarely accessed large files to cheaper storage
• Keep frequently accessed files on fast storage"""
        
        self.storage_analysis_text.setPlainText(analysis_text)
        
        # Update category table
        self.category_table.setRowCount(len(category_stats))
        
        for row, (category, stats) in enumerate(category_stats.items()):
            # Category name
            self.category_table.setItem(row, 0, QTableWidgetItem(category))
            
            # File count
            self.category_table.setItem(row, 1, QTableWidgetItem(str(stats["count"])))
            
            # Total size
            size_gb = stats["size"] / (1024 ** 3)
            if size_gb < 0.01:
                size_str = f"{stats['size'] / (1024 ** 2):.1f} MB"
            else:
                size_str = f"{size_gb:.2f} GB"
            self.category_table.setItem(row, 2, QTableWidgetItem(size_str))
            
            # Average access
            avg_access = stats["total_access"] / stats["count"] if stats["count"] > 0 else 0
            self.category_table.setItem(row, 3, QTableWidgetItem(f"{avg_access:.1f}"))
    
    def export_report(self):
        """Export usage analytics report"""
        from PySide6.QtWidgets import QFileDialog, QMessageBox
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Usage Analytics Report",
            "usage_analytics_report.txt",
            "Text Files (*.txt)"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("USAGE ANALYTICS REPORT\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Generated: {QDate.currentDate().toString()}\n")
                f.write(f"Total Files Analyzed: {len(self.files)}\n\n")
                
                # Frequently accessed files
                f.write("FREQUENTLY ACCESSED FILES:\n")
                f.write("-" * 30 + "\n")
                frequent_files = self.usage_analytics.get_frequently_accessed(10)
                for file_path, data in frequent_files:
                    name = os.path.basename(file_path)
                    f.write(f"• {name} - {data['access_count']} accesses\n")
                
                f.write("\n")
                
                # Cleanup suggestions
                f.write("CLEANUP SUGGESTIONS:\n")
                f.write("-" * 30 + "\n")
                cleanup_files = self.usage_analytics.get_infrequently_accessed(10)
                for file_path, data in cleanup_files:
                    if os.path.exists(file_path):
                        name = os.path.basename(file_path)
                        size = os.path.getsize(file_path)
                        if size > 1024 * 1024:
                            size_str = f"{size / (1024 * 1024):.1f} MB"
                        else:
                            size_str = f"{size / 1024:.1f} KB"
                        f.write(f"• {name} - {size_str} - {data['access_count']} accesses\n")
                
                f.write("\n")
                
                # Storage analysis
                cost_per_gb = self.cost_per_gb.value() / 100.0
                total_cost = self.usage_analytics.get_storage_cost(cost_per_gb)
                f.write("STORAGE ANALYSIS:\n")
                f.write("-" * 30 + "\n")
                f.write(f"Estimated monthly storage cost: ${total_cost:.2f}\n")
                f.write(f"Based on ${cost_per_gb:.2f} per GB\n")
            
            QMessageBox.information(
                self, "Report Exported",
                f"Usage analytics report exported to:\n{file_path}"
            )
            
        except Exception as e:
            QMessageBox.warning(
                self, "Export Failed",
                f"Failed to export report:\n{str(e)}"
            )
