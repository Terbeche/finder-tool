from PySide6.QtWidgets import QMenu, QMessageBox
from dialogs.settings_dialog import SettingsDialog
from services.theme_manager import theme_manager
from dialogs.search_history_dialog import SearchHistoryDialog
from dialogs.usage_analytics_dialog import UsageAnalyticsDialog
from dialogs.performance_dialog import PerformanceDialog
from dialogs.duplicate_dialog import DuplicateDialog
from dialogs.security_dialog import SecurityDialog

class DialogManager:

    def __init__(self, main_window):
        self.main_window = main_window
    
    def open_settings(self):
        """Open settings dialog"""
        dialog = SettingsDialog(self.main_window.categories, self.main_window)
        if dialog.exec():  # Dialog is fully closed when this returns
            # Now process the data safely
            try:
                print("Settings dialog accepted, updating settings...")
                # Update in-memory settings
                self.main_window.app_settings.update(dialog.app_settings)
                self.main_window.categories = dialog.categories
                
                # Apply theme if changed
                if "theme_internal" in dialog.app_settings:
                    theme_manager.apply_theme(dialog.app_settings["theme_internal"])
                
                # Save directly without threading
                print("Saving settings to disk...")
                self.main_window.config_manager.save_settings(self.main_window.app_settings)
                self.main_window.config_manager.save_categories(self.main_window.categories)
                print("Settings saved successfully")
                
                # Refresh UI with updated categories
                self.main_window.ui_manager.refresh_category_dropdown()
                if self.main_window.files:
                    self.main_window.results_manager.refresh_results()

            except Exception as e:
                print(f"Error in settings update: {e}")
                import traceback
                traceback.print_exc()

    def open_search_history(self):
        """Open the search history dialog"""
        from dialogs.search_history_dialog import SearchHistoryDialog
        dialog = SearchHistoryDialog(self.main_window.search_history_manager, self.main_window, self.main_window)
        dialog.exec()

    def open_usage_analytics(self):
        """Open usage analytics dialog"""
        from dialogs.usage_analytics_dialog import UsageAnalyticsDialog
        dialog = UsageAnalyticsDialog(self.main_window.usage_analytics, self.main_window.files, self.main_window)
        dialog.exec()
    
    def show_performance_report(self):
        """Show performance report dialog"""
        from dialogs.performance_dialog import PerformanceDialog
        dialog = PerformanceDialog(self.main_window.performance_optimizer, self.main_window)
        dialog.exec()
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self.main_window,
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
        menu.addAction(self.main_window.open_action)
        menu.addAction(self.main_window.open_containing_folder_action)
        menu.addSeparator()
        menu.addAction(self.main_window.rename_action)
        menu.addAction(self.main_window.batch_rename_action)
        menu.addAction(self.main_window.move_action)
        menu.addAction(self.main_window.delete_action)
        
        # Add tools submenu if there are results
        if self.main_window.files:
            menu.addSeparator()
            tools_menu = menu.addMenu("Tools")
            tools_menu.addAction(self.main_window.duplicate_action)
            tools_menu.addAction(self.main_window.batch_rename_action)
            
            menu.addSeparator()
            menu.addAction(self.main_window.export_action)
        
        # Show menu at cursor position
        menu.exec_(self.main_window.results_table.viewport().mapToGlobal(position))

    def find_duplicates(self):
        """Open duplicate detection dialog"""
        if not self.main_window.files:
            QMessageBox.information(self, "No Files", "Please search for files first before detecting duplicates.")
            return
        
        from dialogs.duplicate_dialog import DuplicateDialog
        dialog = DuplicateDialog(self.main_window.files, self.main_window)
        dialog.exec()

    def run_security_scan(self):
        """Run security scan on current search results"""
        if not self.main_window.files:
            QMessageBox.information(self, "No Files", "Please search for files first before running security scan.")
            return
        
        from dialogs.security_dialog import SecurityDialog
        dialog = SecurityDialog(self.main_window.files, self.main_window)
        dialog.exec()

    def check_file_integrity(self):
        """Check file integrity for selected files"""
        selected_rows = set(index.row() for index in self.main_window.results_table.selectedIndexes())
        
        if selected_rows:
            # Use selected files
            selected_files = [self.main_window.files[row] for row in selected_rows]
            dialog_title = f"Check Integrity of {len(selected_files)} Selected Files"
        elif self.main_window.files:
            # Use all files if none selected
            confirm = QMessageBox.question(
                self, "File Integrity Check",
                f"No files are selected. Check integrity of all {len(self.main_window.files)} files in the results?",
                QMessageBox.Yes | QMessageBox.No
            )
            if confirm != QMessageBox.Yes:
                return
            selected_files = self.main_window.files
            dialog_title = f"Check Integrity of All {len(self.main_window.files)} Files"
        else:
            QMessageBox.information(self.main_window, "No Files", "No files available to check. Please search for files first.")
            return
        
        from dialogs.security_dialog import SecurityDialog
        dialog = SecurityDialog(selected_files, self.main_window, integrity_mode=True)
        dialog.setWindowTitle(dialog_title)
        dialog.exec()