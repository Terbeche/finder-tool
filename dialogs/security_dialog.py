from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox,
    QTabWidget, QWidget, QTextEdit, QMessageBox, QProgressDialog,
    QComboBox, QCheckBox
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QColor
import hashlib
import tempfile
import os
from pathlib import Path

class SecurityScanThread(QThread):
    """Thread for running security scans without blocking UI"""
    progress_updated = Signal(int, int, str)  # current, total, status
    file_analyzed = Signal(object, dict)  # file_info, analysis_result
    scan_complete = Signal(list)  # list of security issues
    
    def __init__(self, files, scan_type="full"):
        super().__init__()
        self.files = files
        self.scan_type = scan_type  # "full", "integrity_only", "suspicious_only"
        self.issues = []
        self.stop_requested = False
    
    def run(self):
        """Run the security scan"""
        for i, file_info in enumerate(self.files):
            if self.stop_requested:
                break
            
            self.progress_updated.emit(i, len(self.files), f"Scanning: {file_info.name}")
            
            analysis = {}
            
            # Check file integrity
            if self.scan_type in ["full", "integrity_only"]:
                analysis["integrity"] = self.check_file_integrity(file_info.path)
            
            # Check for suspicious patterns
            if self.scan_type in ["full", "suspicious_only"]:
                analysis["suspicious"] = self.check_suspicious_file(
                    file_info.path, file_info.name, file_info.extension
                )
            
            # Emit results
            self.file_analyzed.emit(file_info, analysis)
            
            # Collect issues
            if not analysis.get("integrity", True):
                self.issues.append(("Integrity", file_info, "File integrity check failed"))
            
            if analysis.get("suspicious"):
                self.issues.append(("Suspicious", file_info, analysis["suspicious"]))
        
        if not self.stop_requested:
            self.scan_complete.emit(self.issues)
    
    def stop(self):
        """Stop the scan"""
        self.stop_requested = True
    
    def check_file_integrity(self, file_path):
        """Check if file is readable and calculate hash"""
        try:
            # Only check files smaller than 100MB for performance
            if os.path.getsize(file_path) > 100 * 1024 * 1024:
                return True
            with open(file_path, "rb") as f:
                hasher = hashlib.sha256()
                while True:
                    chunk = f.read(8192)
                    if not chunk:
                        break
                    hasher.update(chunk)
            return True
        except Exception:
            return False
    
    def check_suspicious_file(self, file_path, file_name, extension):
        """Detect suspicious files"""
        # Double extension (e.g., .jpg.exe)
        parts = file_name.lower().split('.')
        if len(parts) > 2 and parts[-1] in {"exe", "bat", "cmd", "scr"}:
            return "Double extension (e.g., .jpg.exe)"
        
        # Executable in non-standard location
        if extension in {"exe", "bat", "cmd", "scr"}:
            sysdirs = [os.environ.get("SystemRoot", ""), "/bin", "/usr/bin", "/usr/local/bin"]
            if not any(file_path.startswith(d) for d in sysdirs if d):
                return "Executable file outside system directories"
        
        # File in temp/system directory
        tempdirs = [tempfile.gettempdir(), "/tmp", "/var/tmp"]
        if any(file_path.startswith(d) for d in tempdirs if d):
            return "File in temporary directory"
        
        # Zero size or extremely large
        try:
            size = os.path.getsize(file_path)
            if size == 0:
                return "Zero-size file"
            if size > 10 * 1024 * 1024 * 1024:  # >10GB
                return "Unusually large file"
        except Exception:
            return "Unreadable file"
        
        return None

class SecurityDialog(QDialog):
    """Dialog for security scanning and file integrity checking"""
    
    def __init__(self, files, parent=None, integrity_mode=False):
        super().__init__(parent)
        self.files = files
        self.integrity_mode = integrity_mode
        self.scan_thread = None
        self.security_issues = []
        
        self.setWindowTitle("File Security Scan" if not integrity_mode else "File Integrity Check")
        self.setModal(True)
        self.resize(900, 600)
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface"""
        layout = QVBoxLayout(self)
        
        # Scan options
        options_group = QGroupBox("Scan Options")
        options_layout = QHBoxLayout(options_group)
        
        if not self.integrity_mode:
            self.scan_type = QComboBox()
            self.scan_type.addItems([
                "Full Security Scan",
                "Integrity Check Only", 
                "Suspicious Files Only"
            ])
            options_layout.addWidget(QLabel("Scan Type:"))
            options_layout.addWidget(self.scan_type)
        
        self.scan_button = QPushButton("Start Scan")
        self.scan_button.clicked.connect(self.start_scan)
        options_layout.addWidget(self.scan_button)
        
        self.stop_button = QPushButton("Stop Scan")
        self.stop_button.clicked.connect(self.stop_scan)
        self.stop_button.setEnabled(False)
        options_layout.addWidget(self.stop_button)
        
        options_layout.addStretch()
        layout.addWidget(options_group)
        
        # Status and progress
        self.status_label = QLabel(f"Ready to scan {len(self.files)} files")
        layout.addWidget(self.status_label)
        
        # Results table
        results_group = QGroupBox("Scan Results")
        results_layout = QVBoxLayout(results_group)
        
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(5)
        self.results_table.setHorizontalHeaderLabels([
            "Issue Type", "File Name", "Path", "Problem", "Risk Level"
        ])
        self.results_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.results_table.setAlternatingRowColors(True)
        results_layout.addWidget(self.results_table)
        
        # Statistics
        self.stats_label = QLabel("No scan performed yet")
        results_layout.addWidget(self.stats_label)
        
        layout.addWidget(results_group)
        
        # Action buttons
        action_layout = QHBoxLayout()
        
        self.quarantine_button = QPushButton("Quarantine Selected")
        self.quarantine_button.clicked.connect(self.quarantine_files)
        self.quarantine_button.setEnabled(False)
        
        self.export_report_button = QPushButton("Export Report")
        self.export_report_button.clicked.connect(self.export_report)
        self.export_report_button.setEnabled(False)
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        
        action_layout.addWidget(self.quarantine_button)
        action_layout.addWidget(self.export_report_button)
        action_layout.addStretch()
        action_layout.addWidget(close_button)
        
        layout.addLayout(action_layout)
    
    def start_scan(self):
        """Start the security scan"""
        if self.integrity_mode:
            scan_type = "integrity_only"
        else:
            scan_types = {
                0: "full",
                1: "integrity_only", 
                2: "suspicious_only"
            }
            scan_type = scan_types[self.scan_type.currentIndex()]
        
        self.scan_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.results_table.setRowCount(0)
        self.security_issues = []
        
        # Start scan thread
        self.scan_thread = SecurityScanThread(self.files, scan_type)
        self.scan_thread.progress_updated.connect(self.update_progress)
        self.scan_thread.file_analyzed.connect(self.file_analyzed)
        self.scan_thread.scan_complete.connect(self.scan_finished)
        self.scan_thread.start()
    
    def stop_scan(self):
        """Stop the security scan"""
        if self.scan_thread:
            self.scan_thread.stop()
            self.scan_thread.wait()
        
        self.scan_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_label.setText("Scan stopped by user")
    
    def update_progress(self, current, total, status):
        """Update scan progress"""
        self.status_label.setText(f"Progress: {current}/{total} - {status}")
    
    def file_analyzed(self, file_info, analysis):
        """Handle analysis of individual file"""
        # Add to results table if there are issues
        issues_found = False
        
        if not analysis.get("integrity", True):
            self.add_result_row("Integrity", file_info, "File integrity check failed", "High")
            issues_found = True
        
        if analysis.get("suspicious"):
            risk_level = self.assess_risk_level(analysis["suspicious"])
            self.add_result_row("Suspicious", file_info, analysis["suspicious"], risk_level)
            issues_found = True
    
    def add_result_row(self, issue_type, file_info, problem, risk_level):
        """Add a row to the results table"""
        row = self.results_table.rowCount()
        self.results_table.insertRow(row)
        
        # Issue type
        type_item = QTableWidgetItem(issue_type)
        if issue_type == "Integrity":
            type_item.setBackground(QColor("#ffcccc"))
        else:
            type_item.setBackground(QColor("#ffffcc"))
        self.results_table.setItem(row, 0, type_item)
        
        # File name
        self.results_table.setItem(row, 1, QTableWidgetItem(file_info.name))
        
        # Path
        self.results_table.setItem(row, 2, QTableWidgetItem(file_info.path))
        
        # Problem
        self.results_table.setItem(row, 3, QTableWidgetItem(problem))
        
        # Risk level
        risk_item = QTableWidgetItem(risk_level)
        if risk_level == "High":
            risk_item.setBackground(QColor("#ff9999"))
        elif risk_level == "Medium":
            risk_item.setBackground(QColor("#ffff99"))
        else:
            risk_item.setBackground(QColor("#ccffcc"))
        self.results_table.setItem(row, 4, risk_item)
        
        # Store file info for later use
        self.results_table.item(row, 0).setData(Qt.UserRole, file_info)
    
    def assess_risk_level(self, problem):
        """Assess risk level based on the problem type"""
        high_risk = [
            "Double extension",
            "Executable file outside system directories"
        ]
        medium_risk = [
            "File in temporary directory",
            "Unusually large file"
        ]
        
        for risk in high_risk:
            if risk in problem:
                return "High"
        for risk in medium_risk:
            if risk in problem:
                return "Medium"
        return "Low"
    
    def scan_finished(self, issues):
        """Handle scan completion"""
        self.security_issues = issues
        self.scan_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        # Update statistics
        total_files = len(self.files)
        issues_count = len(issues)
        integrity_issues = len([i for i in issues if i[0] == "Integrity"])
        suspicious_issues = len([i for i in issues if i[0] == "Suspicious"])
        
        stats_text = (
            f"Scan complete: {total_files} files scanned, {issues_count} issues found\n"
            f"Integrity issues: {integrity_issues}, Suspicious files: {suspicious_issues}"
        )
        self.stats_label.setText(stats_text)
        self.status_label.setText("Scan completed")
        
        # Enable action buttons if issues found
        if issues:
            self.quarantine_button.setEnabled(True)
            self.export_report_button.setEnabled(True)
            
            # Show summary message
            QMessageBox.warning(
                self, "Security Issues Found",
                f"Found {issues_count} security issues:\n"
                f"• {integrity_issues} integrity problems\n"
                f"• {suspicious_issues} suspicious files\n\n"
                f"Review the results and consider quarantining problematic files."
            )
        else:
            QMessageBox.information(
                self, "Scan Complete",
                "No security issues found. All files passed the security scan."
            )
    
    def quarantine_files(self):
        """Move selected problematic files to quarantine"""
        selected_rows = set(index.row() for index in self.results_table.selectedIndexes())
        
        if not selected_rows:
            QMessageBox.information(self, "No Selection", "Please select files to quarantine.")
            return
        
        # Get quarantine directory
        from PySide6.QtWidgets import QFileDialog
        quarantine_dir = QFileDialog.getExistingDirectory(
            self, "Select Quarantine Directory"
        )
        
        if not quarantine_dir:
            return
        
        confirm = QMessageBox.question(
            self, "Confirm Quarantine",
            f"Move {len(selected_rows)} selected files to quarantine?\n"
            f"Quarantine location: {quarantine_dir}\n\n"
            f"This will move the files out of their current locations.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm != QMessageBox.Yes:
            return
        
        # Move files to quarantine
        import shutil
        quarantined_count = 0
        failed_files = []
        
        for row in selected_rows:
            file_info = self.results_table.item(row, 0).data(Qt.UserRole)
            if not file_info:
                continue
            
            try:
                source_path = Path(file_info.path)
                target_path = Path(quarantine_dir) / source_path.name
                
                # Handle name conflicts
                counter = 1
                while target_path.exists():
                    stem = source_path.stem
                    suffix = source_path.suffix
                    target_path = Path(quarantine_dir) / f"{stem}_quarantine_{counter}{suffix}"
                    counter += 1
                
                shutil.move(str(source_path), str(target_path))
                quarantined_count += 1
                
            except Exception as e:
                failed_files.append((file_info.name, str(e)))
        
        # Show results
        if failed_files:
            failed_list = "\n".join([f"• {name}: {error}" for name, error in failed_files[:5]])
            if len(failed_files) > 5:
                failed_list += f"\n... and {len(failed_files) - 5} more"
            
            QMessageBox.warning(
                self, "Quarantine Results",
                f"Quarantined {quarantined_count} files successfully.\n"
                f"Failed to quarantine {len(failed_files)} files:\n\n{failed_list}"
            )
        else:
            QMessageBox.information(
                self, "Quarantine Complete",
                f"Successfully quarantined {quarantined_count} files to:\n{quarantine_dir}"
            )
    
    def export_report(self):
        """Export security scan report"""
        if not self.security_issues:
            QMessageBox.information(self, "No Report", "No security issues to export.")
            return
        
        from PySide6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Security Report",
            "security_scan_report.txt",
            "Text Files (*.txt)"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("SECURITY SCAN REPORT\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Scan Date: {QDate.currentDate().toString()}\n")
                f.write(f"Files Scanned: {len(self.files)}\n")
                f.write(f"Issues Found: {len(self.security_issues)}\n\n")
                
                f.write("DETAILED RESULTS:\n")
                f.write("-" * 30 + "\n\n")
                
                for issue_type, file_info, problem in self.security_issues:
                    f.write(f"Issue Type: {issue_type}\n")
                    f.write(f"File: {file_info.name}\n")
                    f.write(f"Path: {file_info.path}\n")
                    f.write(f"Problem: {problem}\n")
                    f.write(f"Size: {file_info.get_size_str()}\n")
                    f.write(f"Modified: {file_info.modified_date}\n")
                    f.write("-" * 30 + "\n")
            
            QMessageBox.information(
                self, "Report Exported",
                f"Security scan report exported to:\n{file_path}"
            )
            
        except Exception as e:
            QMessageBox.warning(
                self, "Export Failed",
                f"Failed to export report:\n{str(e)}"
            )
