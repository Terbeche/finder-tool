from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QTreeWidget, QTreeWidgetItem, QComboBox, QProgressBar,
    QMessageBox, QGroupBox, QCheckBox, QSplitter, QTextEdit,
    QHeaderView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from duplicate_detector import DuplicateDetector
import os
from pathlib import Path

class DuplicateDialog(QDialog):
    """Dialog for duplicate file detection and management"""
    
    def __init__(self, files, parent=None):
        super().__init__(parent)
        self.files = files
        self.duplicate_groups = {}
        self.detector_thread = None
        self.setWindowTitle("Duplicate File Detector")
        self.setModal(True)
        self.resize(900, 600)
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface"""
        layout = QVBoxLayout(self)
        
        # Detection method selection
        method_group = QGroupBox("Detection Method")
        method_layout = QHBoxLayout(method_group)
        
        self.method_combo = QComboBox()
        self.method_combo.addItems([
            "Size + Name (Fast)",
            "Quick Hash (Medium)", 
            "Full Content Hash (Accurate but Slow)"
        ])
        method_layout.addWidget(QLabel("Method:"))
        method_layout.addWidget(self.method_combo)
        
        self.detect_button = QPushButton("Detect Duplicates")
        self.detect_button.clicked.connect(self.start_detection)
        method_layout.addWidget(self.detect_button)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_detection)
        self.stop_button.setEnabled(False)
        method_layout.addWidget(self.stop_button)
        
        layout.addWidget(method_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel(f"Ready to scan {len(self.files)} files for duplicates")
        layout.addWidget(self.status_label)
        
        # Results area with splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left side - duplicate groups tree
        left_widget = QGroupBox("Duplicate Groups")
        left_layout = QVBoxLayout(left_widget)
        
        self.results_tree = QTreeWidget()
        self.results_tree.setHeaderLabels(["Group", "Files", "Total Size", "Wasted Space"])
        self.results_tree.itemSelectionChanged.connect(self.on_group_selected)
        left_layout.addWidget(self.results_tree)
        
        # Selection controls
        selection_layout = QHBoxLayout()
        self.select_all_but_first = QPushButton("Select All But First")
        self.select_all_but_first.clicked.connect(self.select_all_but_first_in_groups)
        self.select_all_but_newest = QPushButton("Select All But Newest")
        self.select_all_but_newest.clicked.connect(self.select_all_but_newest_in_groups)
        selection_layout.addWidget(self.select_all_but_first)
        selection_layout.addWidget(self.select_all_but_newest)
        left_layout.addLayout(selection_layout)
        
        splitter.addWidget(left_widget)
        
        # Right side - file details
        right_widget = QGroupBox("File Details")
        right_layout = QVBoxLayout(right_widget)
        
        self.details_tree = QTreeWidget()
        self.details_tree.setHeaderLabels(["Select", "File Name", "Path", "Size", "Modified"])
        self.details_tree.setRootIsDecorated(False)
        header = self.details_tree.header()
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        right_layout.addWidget(self.details_tree)
        
        splitter.addWidget(right_widget)
        splitter.setSizes([400, 500])
        layout.addWidget(splitter)
        
        # Action buttons
        action_layout = QHBoxLayout()
        self.delete_selected = QPushButton("Delete Selected Files")
        self.delete_selected.clicked.connect(self.delete_selected_files)
        self.delete_selected.setEnabled(False)
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        
        action_layout.addWidget(self.delete_selected)
        action_layout.addStretch()
        action_layout.addWidget(self.close_button)
        layout.addLayout(action_layout)
    
    def start_detection(self):
        """Start duplicate detection"""
        method_map = {
            0: "size_name",
            1: "quick_hash", 
            2: "content_hash"
        }
        
        method = method_map[self.method_combo.currentIndex()]
        
        self.detect_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.results_tree.clear()
        self.details_tree.clear()
        
        # Start detection thread
        self.detector_thread = DuplicateDetector(self.files, method)
        self.detector_thread.progress_updated.connect(self.update_progress)
        self.detector_thread.detection_complete.connect(self.detection_finished)
        self.detector_thread.start()
    
    def stop_detection(self):
        """Stop duplicate detection"""
        if self.detector_thread:
            self.detector_thread.stop()
            self.detector_thread.wait()
        
        self.detect_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.status_label.setText("Detection stopped by user")
    
    def update_progress(self, current, total, status):
        """Update progress during detection"""
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.status_label.setText(status)
    
    def detection_finished(self, duplicate_groups):
        """Handle detection completion"""
        self.duplicate_groups = duplicate_groups
        self.detect_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_bar.setVisible(False)
        
        if not duplicate_groups:
            self.status_label.setText("No duplicates found!")
            QMessageBox.information(self, "No Duplicates", "No duplicate files were found.")
            return
        
        # Populate results tree
        total_groups = len(duplicate_groups)
        total_duplicates = sum(len(files) for files in duplicate_groups.values())
        total_wasted = 0
        
        for group_key, files in duplicate_groups.items():
            if len(files) < 2:
                continue
            
            # Calculate wasted space (all files except the largest one)
            files.sort(key=lambda f: f.size, reverse=True)
            wasted_space = sum(f.size for f in files[1:])
            total_wasted += wasted_space
            
            # Create tree item
            group_item = QTreeWidgetItem(self.results_tree)
            group_item.setText(0, f"Group {len(self.results_tree.topLevelItems()) + 1}")
            group_item.setText(1, f"{len(files)} files")
            group_item.setText(2, self._format_size(files[0].size))
            group_item.setText(3, self._format_size(wasted_space))
            group_item.setData(0, Qt.UserRole, group_key)
        
        self.results_tree.expandAll()
        self.status_label.setText(
            f"Found {total_groups} duplicate groups with {total_duplicates} files. "
            f"Potential space savings: {self._format_size(total_wasted)}"
        )
    
    def on_group_selected(self):
        """Handle group selection in tree"""
        selected_items = self.results_tree.selectedItems()
        if not selected_items:
            return
        
        group_key = selected_items[0].data(0, Qt.UserRole)
        if group_key not in self.duplicate_groups:
            return
        
        # Populate details tree
        self.details_tree.clear()
        files = self.duplicate_groups[group_key]
        
        for file_info in files:
            item = QTreeWidgetItem(self.details_tree)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(0, Qt.Unchecked)
            item.setText(1, file_info.name)
            item.setText(2, file_info.path)
            item.setText(3, file_info.get_size_str())
            item.setText(4, file_info.modified_date.strftime("%Y-%m-%d %H:%M"))
            item.setData(0, Qt.UserRole, file_info)
        
        self.details_tree.expandAll()
        self.delete_selected.setEnabled(True)
    
    def select_all_but_first_in_groups(self):
        """Select all files except the first one in each group"""
        for group_key, files in self.duplicate_groups.items():
            if len(files) < 2:
                continue
            # Skip first file, select the rest
            for i in range(1, len(files)):
                self._set_file_selected(files[i], True)
        self._update_details_view()
    
    def select_all_but_newest_in_groups(self):
        """Select all files except the newest one in each group"""
        for group_key, files in self.duplicate_groups.items():
            if len(files) < 2:
                continue
            # Sort by modification date, newest first
            sorted_files = sorted(files, key=lambda f: f.modified_date, reverse=True)
            # Skip newest file, select the rest
            for i in range(1, len(sorted_files)):
                self._set_file_selected(sorted_files[i], True)
        self._update_details_view()
    
    def _set_file_selected(self, file_info, selected):
        """Mark a file as selected for deletion"""
        file_info.selected = selected
    
    def _update_details_view(self):
        """Update the details view to reflect selections"""
        current_group = self.results_tree.selectedItems()
        if current_group:
            self.on_group_selected()
    
    def delete_selected_files(self):
        """Delete selected duplicate files"""
        selected_files = []
        
        # Get all selected files from current group
        for i in range(self.details_tree.topLevelItemCount()):
            item = self.details_tree.topLevelItem(i)
            if item.checkState(0) == Qt.Checked:
                file_info = item.data(0, Qt.UserRole)
                selected_files.append(file_info)
        
        if not selected_files:
            QMessageBox.information(self, "No Selection", "Please select files to delete.")
            return
        
        # Confirm deletion
        total_size = sum(f.size for f in selected_files)
        confirm = QMessageBox.question(
            self, "Confirm Deletion",
            f"Delete {len(selected_files)} duplicate files?\n"
            f"Total size: {self._format_size(total_size)}\n\n"
            f"This action cannot be undone!",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm != QMessageBox.Yes:
            return
        
        # Delete files
        deleted_count = 0
        failed_files = []
        
        for file_info in selected_files:
            try:
                os.remove(file_info.path)
                deleted_count += 1
            except Exception as e:
                failed_files.append((file_info.name, str(e)))
        
        # Show results
        if failed_files:
            failed_list = "\n".join([f"• {name}: {error}" for name, error in failed_files[:5]])
            if len(failed_files) > 5:
                failed_list += f"\n... and {len(failed_files) - 5} more"
            
            QMessageBox.warning(
                self, "Deletion Results",
                f"Deleted {deleted_count} files successfully.\n"
                f"Failed to delete {len(failed_files)} files:\n\n{failed_list}"
            )
        else:
            saved_space = sum(f.size for f in selected_files)
            QMessageBox.information(
                self, "Deletion Complete",
                f"Successfully deleted {deleted_count} duplicate files.\n"
                f"Space saved: {self._format_size(saved_space)}"
            )
        
        # Refresh the view
        self.start_detection()
    
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
