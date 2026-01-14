from PySide6.QtWidgets import QFileDialog, QMessageBox, QProgressBar
from PySide6.QtCore import QThread, Signal, QTimer
from pathlib import Path
import os
import time
from scanners.file_scanner_thread import FileScannerThread

class SearchManager:
    def __init__(self, main_window, results_manager):
        self.main_window = main_window
        self.results_manager = results_manager

    def browse_directory(self):
        """Open directory browser dialog"""
        directory = QFileDialog.getExistingDirectory(
            self.main_window, "Select Directory", self.main_window.current_directory
        )
        if directory:
            self.main_window.path_edit.setText(directory)
            self.main_window.current_directory = directory
            
            # Save the current directory in settings
            self.main_window.app_settings["last_directory"] = directory
            self.main_window.config_manager.save_settings(self.main_window.app_settings)
    
    def start_search(self):
        """Start file search operation"""
        # Record search start time
        from time import time
        search_start_time = time()
        
        # Check for cached results
        directory = self.main_window.path_edit.text()
        if not os.path.exists(directory):
            QMessageBox.warning(self.main_window, "Invalid Directory", "The specified directory does not exist.")
            return
        
        # Estimate file count for large directories
        scan_hidden = self.main_window.include_hidden.isChecked()
        max_depth = self.main_window.max_depth.value()
        estimated_count = self._estimate_file_count(directory, max_depth, scan_hidden)
        
        if estimated_count > 50000:
            # Warn user about large scan
            proceed = QMessageBox.question(
                self.main_window, "Large Directory Warning",
                f"This directory contains approximately {estimated_count:,} items.\n\n"
                f"Scanning may take a long time.\n\n"
                f"Options:\n"
                f"• Yes - Proceed with scan\n"
                f"• No - Cancel and adjust settings\n\n"
                f"Tip: Reduce 'Max Depth' or deselect 'Hidden' to scan faster.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if proceed != QMessageBox.Yes:
                return
        
        # Check cache first
        cached_result = self.main_window.performance_optimizer.get_cached_scan(directory)
        if cached_result:
            # Ask user if they want to use cached results
            use_cache = QMessageBox.question(
                self.main_window, "Cached Results Available",
                f"Found cached scan results for this directory.\n"
                f"Files: {cached_result['file_count']}\n"
                f"Scan time: {cached_result['scan_time']:.2f}s\n\n"
                f"Use cached results or perform new scan?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if use_cache == QMessageBox.Yes:
                self.main_window.statusBar().showMessage("Using cached results...")
                return
        
        # Get optimization strategy
        optimization = self.main_window.performance_optimizer.optimize_scan_strategy(directory)
        
        # Get search parameters
        if optimization == "fast":
            # Fast scan: only top-level files, no subdirectories
            directory = self.main_window.path_edit.text()
            if not os.path.exists(directory):
                QMessageBox.warning(self.main_window, "Invalid Directory", "The specified directory does not exist.")
                return
            
            # Update current directory
            self.main_window.current_directory = directory
            
            # Get selected category
            selected_category_index = self.main_window.category_combo.currentIndex()
            extensions = []
            if selected_category_index > 0:
                # Specific category selected
                category = self.main_window.categories[selected_category_index - 1]
                extensions = category.extensions
            
            # Get size constraints
            min_size = self.main_window.min_size.value()
            max_size = self.main_window.max_size.value() if self.main_window.max_size.value() > 0 else None
            
            # Get advanced filters
            advanced_filters = self.main_window.ui_manager.get_advanced_filters()
            
            # Clear previous results
            self.main_window.results_table.setRowCount(0)
            self.main_window.files.clear()  # Clear the list instead of replacing it
            
            # Update UI
            self.main_window.search_button.setEnabled(False)
            self.main_window.pause_button.setEnabled(True)
            self.main_window.stop_button.setEnabled(True)
            self.main_window.progress_bar.setVisible(True)
            self.main_window.progress_bar.setValue(0)
            
            # Stop any existing scanner thread
            if self.main_window.scanner_thread and self.main_window.scanner_thread.isRunning():
                self.main_window.scanner_thread.stop()
                self.main_window.scanner_thread.wait()
            
            # Create and start scanner thread
            self.main_window.scanner_thread = FileScannerThread(
                directory, min_size, max_size, extensions, 
                self.main_window.categories, 1, advanced_filters,
                scan_hidden=self.main_window.include_hidden.isChecked()
            )
            self.main_window.scanner_thread.update_progress.connect(self.update_progress)
            self.main_window.scanner_thread.file_found.connect(self.add_file_to_results)
            self.main_window.scanner_thread.scan_complete.connect(self.scan_complete)
            self.main_window.scanner_thread.start()
        else:
            # Full scan: all files and subdirectories
            directory = self.main_window.path_edit.text()
            if not os.path.exists(directory):
                QMessageBox.warning(self.main_window, "Invalid Directory", "The specified directory does not exist.")
                return
            
            # Update current directory
            self.main_window.current_directory = directory
            
            # Get selected category
            selected_category_index = self.main_window.category_combo.currentIndex()
            extensions = []
            if selected_category_index > 0:
                # Specific category selected
                category = self.main_window.categories[selected_category_index - 1]
                extensions = category.extensions
            
            # Get size constraints
            min_size = self.main_window.min_size.value()
            max_size = self.main_window.max_size.value() if self.main_window.max_size.value() > 0 else None
            
            # Get advanced filters
            advanced_filters = self.main_window.ui_manager.get_advanced_filters()
            
            # Clear previous results
            self.main_window.results_table.setRowCount(0)
            self.main_window.files.clear()  # Clear the list instead of replacing it
            
            # Update UI
            self.main_window.search_button.setEnabled(False)
            self.main_window.pause_button.setEnabled(True)
            self.main_window.stop_button.setEnabled(True)
            self.main_window.progress_bar.setVisible(True)
            self.main_window.progress_bar.setValue(0)
            
            # Stop any existing scanner thread
            if self.main_window.scanner_thread and self.main_window.scanner_thread.isRunning():
                self.main_window.scanner_thread.stop()
                self.main_window.scanner_thread.wait()
            
            # Create and start scanner thread
            self.main_window.scanner_thread = FileScannerThread(
                directory, min_size, max_size, extensions, 
                self.main_window.categories, self.main_window.max_depth.value(), advanced_filters,
                scan_hidden=self.main_window.include_hidden.isChecked()
            )
            self.main_window.scanner_thread.update_progress.connect(self.update_progress)
            self.main_window.scanner_thread.file_found.connect(self.add_file_to_results)
            self.main_window.scanner_thread.scan_complete.connect(self.scan_complete)
            self.main_window.scanner_thread.start()
        
        # Store search configuration for history
        self.current_search_config = {
            "directory": directory,
            "category": self.main_window.category_combo.currentText(),
            "min_size": self.main_window.min_size.value(),
            "max_size": self.main_window.max_size.value(),
            "max_depth": self.main_window.max_depth.value(),
            "date_filter_enabled": self.main_window.date_filter_enabled.isChecked(),
            "date_from": self.main_window.date_from.date().toString("yyyy-MM-dd") if self.main_window.date_filter_enabled.isChecked() else None,
            "date_to": self.main_window.date_to.date().toString("yyyy-MM-dd") if self.main_window.date_filter_enabled.isChecked() else None,
            "pattern_filter_enabled": self.main_window.pattern_filter_enabled.isChecked(),
            "filename_pattern": self.main_window.pattern_edit.text(),
            "content_filter_enabled": self.main_window.content_filter_enabled.isChecked(),
            "content_search": self.main_window.content_edit.text()
        }
        self.search_start_time = search_start_time
    
    def update_progress(self, current, total):
        """Update progress bar during scanning"""
        if total > 0:
            percent = int((current / total) * 100)
            self.main_window.progress_bar.setValue(percent)
            self.main_window.statusBar().showMessage(f"Scanning... {current} of {total} items processed")
    
    def add_file_to_results(self, file_info):
        """Add a file to the results table"""
        self.main_window.files.append(file_info)
        self.results_manager.add_file_to_table(file_info)
        
        # Update file count
        self.main_window.file_count_label.setText(f"{len(self.main_window.files)} files found")
        
        # Update total size
        total_size = sum(f.size for f in self.main_window.files)
        if total_size < 1024 * 1024:
            size_str = f"{total_size / 1024:.1f} KB"
        elif total_size < 1024 * 1024 * 1024:
            size_str = f"{total_size / (1024 * 1024):.1f} MB"
        else:
            size_str = f"{total_size / (1024 * 1024 * 1024):.2f} GB"
        self.main_window.total_size_label.setText(f"Total size: {size_str}")
    
    def scan_complete(self, files):
        """Handle scan completion"""
        self.main_window.search_button.setEnabled(True)
        self.main_window.pause_button.setEnabled(False)
        self.main_window.stop_button.setEnabled(False)
        self.main_window.progress_bar.setVisible(False)
        self.main_window.statusBar().showMessage(f"Scan complete. Found {len(files)} files.")
        
        # Record performance metrics
        from time import time
        search_duration = time() - getattr(self, 'search_start_time', time())
        self.main_window.performance_optimizer.record_scan_performance(
            self.main_window.current_directory, len(files), search_duration
        )
        
        # Add search to history
        from time import time
        search_duration = time() - getattr(self, 'search_start_time', time())
        
        # Calculate total size
        total_size = sum(f.size for f in self.main_window.files)
        
        # Add search to history
        results_summary = {
            "files_found": len(files),
            "total_size": total_size,
            "search_duration": search_duration
        }
        
        if hasattr(self, 'current_search_config'):
            self.main_window.search_history_manager.add_search(
                self.current_search_config,
                results_summary
            )
    
        # Check for new file extensions
        if self.main_window.app_settings.get("auto_discover", True) and self.main_window.files:
            self.check_for_new_extensions()
    
    def check_for_new_extensions(self):
        """Check for file extensions not in any category"""
        # Get all known extensions
        known_extensions = set()
        for category in self.main_window.categories:
            known_extensions.update([ext.lower() for ext in category.extensions])
        
        # Find new extensions
        new_extensions = set()
        for file_info in self.main_window.files:
            if file_info.extension and file_info.extension.lower() not in known_extensions:
                new_extensions.add(file_info.extension.lower())
        
        if new_extensions:
            # Ask user if they want to add these extensions
            extensions_str = ", ".join(sorted(new_extensions))
            confirm = QMessageBox.question(
                self.main_window, "New File Extensions Found", 
                f"Found {len(new_extensions)} new file extensions: {extensions_str}\n\n"
                "Would you like to categorize these extensions?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if confirm == QMessageBox.Yes:
                # Show dialog to categorize extensions
                # (In a full implementation, we would have a dialog for this)
                pass

    def toggle_pause_scan(self):
        """Pause or resume the file scan"""
        if not self.main_window.scanner_thread or not self.main_window.scanner_thread.isRunning():
            return
            
        if self.main_window.scanner_thread.pause_requested:
            # Resume scan
            self.main_window.scanner_thread.resume()
            self.main_window.pause_button.setText("Pause")
            self.main_window.statusBar().showMessage("Scan resumed...")
        else:
            # Pause scan
            self.main_window.scanner_thread.pause()
            self.main_window.pause_button.setText("Resume")
            self.main_window.statusBar().showMessage("Scan paused. Click Resume to continue.")

    def stop_scan(self):
        """Stop the file scan"""
        if not self.main_window.scanner_thread or not self.main_window.scanner_thread.isRunning():
            return
            
        self.main_window.scanner_thread.stop()
        self.main_window.statusBar().showMessage("Stopping scan...")
        self.main_window.scanner_thread.wait(1000)  # Wait up to 1 second for thread to finish
        
        self.main_window.search_button.setEnabled(True)
        self.main_window.pause_button.setEnabled(False)
        self.main_window.stop_button.setEnabled(False)
        self.main_window.pause_button.setText("Pause")
        self.main_window.progress_bar.setVisible(False)
        self.main_window.statusBar().showMessage("Scan stopped by user.")
    
    def _estimate_file_count(self, directory, max_depth, scan_hidden):
        """Quickly estimate file count before scanning (limited depth)"""
        count = 0
        sample_depth = min(max_depth, 3)  # Only sample first 3 levels
        
        try:
            for root, dirs, files in os.walk(directory):
                # Calculate current depth
                rel_path = os.path.relpath(root, directory)
                depth = 0 if rel_path == '.' else rel_path.count(os.sep) + 1
                
                # Check if we're in a hidden directory (skip entire subtree)
                if not scan_hidden and depth > 0:
                    # Check if any parent directory is hidden
                    parts = rel_path.split(os.sep)
                    if any(part.startswith('.') for part in parts):
                        dirs[:] = []  # Don't descend further
                        continue
                
                if depth >= sample_depth:
                    dirs[:] = []  # Don't go deeper
                    continue
                
                # Filter hidden items from counting AND from descent
                if not scan_hidden:
                    # Filter out hidden directories so os.walk won't enter them
                    original_dir_count = len(dirs)
                    dirs[:] = [d for d in dirs if not d.startswith('.')]
                    # Filter hidden files
                    files = [f for f in files if not f.startswith('.')]
                
                count += len(files) + len(dirs)
                
                # Stop early if we've seen enough
                if count > 100000:
                    break
        except (PermissionError, OSError):
            pass
        
        # Extrapolate estimate based on depth ratio
        if sample_depth < max_depth and count > 1000:
            depth_factor = max_depth / sample_depth
            count = int(count * (depth_factor ** 0.5))  # Sublinear extrapolation
        
        return count
