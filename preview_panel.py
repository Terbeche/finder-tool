from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QTextEdit, QGroupBox, QSplitter, QFrame
)
from PySide6.QtCore import Qt, QSize, QThread, Signal
from PySide6.QtGui import QPixmap, QFont, QTextCursor
from pathlib import Path
import os
from media_intelligence import get_video_metadata

class ImageLoaderThread(QThread):
    """Thread for loading images without blocking UI"""
    image_loaded = Signal(str)  # file_path
    
    def __init__(self, file_path, max_size=(300, 300)):
        super().__init__()
        self.file_path = file_path
        self.max_size = max_size
    
    def run(self):
        """Load and resize image"""
        try:
            pixmap = QPixmap(self.file_path)
            if not pixmap.isNull():
                # Scale image to fit preview while maintaining aspect ratio
                scaled_pixmap = pixmap.scaled(
                    *self.max_size, 
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation
                )
                # Save scaled image temporarily for display
                self.image_loaded.emit(self.file_path)
        except Exception:
            pass

class PreviewPanel(QWidget):
    """Panel for previewing file contents"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_file = None
        self.image_loader = None
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the preview panel UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Header with file info
        self.header_group = QGroupBox("File Preview")
        header_layout = QVBoxLayout(self.header_group)
        
        self.file_name_label = QLabel("No file selected")
        self.file_name_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.file_name_label.setWordWrap(True)
        header_layout.addWidget(self.file_name_label)
        
        self.file_info_label = QLabel("")
        self.file_info_label.setStyleSheet("color: gray; font-size: 9pt;")
        header_layout.addWidget(self.file_info_label)
        
        layout.addWidget(self.header_group)
        
        # Scrollable content area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Content widget
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        
        # Image preview label
        self.image_label = QLabel("No preview available")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(200, 150)
        self.image_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #ccc;
                border-radius: 8px;
                background-color: #f9f9f9;
                color: #666;
            }
        """)
        self.content_layout.addWidget(self.image_label)
        
        # Text preview area
        self.text_preview = QTextEdit()
        self.text_preview.setReadOnly(True)
        self.text_preview.setMaximumHeight(200)
        self.text_preview.setVisible(False)
        self.content_layout.addWidget(self.text_preview)
        
        # File properties area
        self.properties_group = QGroupBox("Properties")
        self.properties_layout = QVBoxLayout(self.properties_group)
        self.properties_label = QLabel("Select a file to view properties")
        self.properties_label.setWordWrap(True)
        self.properties_layout.addWidget(self.properties_label)
        self.content_layout.addWidget(self.properties_group)
        
        self.content_layout.addStretch()
        self.scroll_area.setWidget(self.content_widget)
        layout.addWidget(self.scroll_area)
        
        # Action buttons
        button_layout = QHBoxLayout()
        self.open_button = QPushButton("Open File")
        self.open_button.setEnabled(False)
        self.open_button.clicked.connect(self.open_current_file)
        
        self.open_folder_button = QPushButton("Open Folder")
        self.open_folder_button.setEnabled(False)
        self.open_folder_button.clicked.connect(self.open_containing_folder)
        
        button_layout.addWidget(self.open_button)
        button_layout.addWidget(self.open_folder_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Set minimum width
        self.setMinimumWidth(250)
    
    def preview_file(self, file_info):
        """Preview the selected file"""
        if not file_info:
            self.clear_preview()
            return
        
        self.current_file = file_info
        
        # Update header
        self.file_name_label.setText(file_info.name)
        self.file_info_label.setText(
            f"Size: {file_info.get_size_str()}\n"
            f"Modified: {file_info.modified_date.strftime('%Y-%m-%d %H:%M')}"
        )
        
        # Enable buttons
        self.open_button.setEnabled(True)
        self.open_folder_button.setEnabled(True)
        
        # Update properties
        self.update_properties(file_info)
        
        # Clear previous preview
        self.image_label.clear()
        self.text_preview.setVisible(False)
        
        # Determine preview type
        file_path = Path(file_info.path)
        extension = file_info.extension.lower()
        
        if self.is_image_file(extension):
            self.preview_image(file_info.path)
        elif self.is_text_file(extension):
            self.preview_text(file_info.path)
        elif extension in {"mp4", "avi", "mkv", "mov", "wmv", "flv", "webm", "m4v", "3gp"}:
            self.preview_video(file_info.path)
        else:
            self.show_no_preview(extension)
    
    def is_image_file(self, extension):
        """Check if file is a supported image format"""
        image_extensions = {
            'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'tif', 
            'webp', 'svg', 'ico', 'ppm', 'pgm', 'pbm'
        }
        return extension in image_extensions
    
    def is_text_file(self, extension):
        """Check if file is a text file that can be previewed"""
        text_extensions = {
            'txt', 'md', 'py', 'js', 'html', 'css', 'xml', 'json',
            'csv', 'log', 'conf', 'ini', 'cfg', 'yml', 'yaml',
            'sh', 'bat', 'ps1', 'c', 'cpp', 'h', 'java', 'php'
        }
        return extension in text_extensions
    
    def preview_image(self, file_path):
        """Preview image file"""
        try:
            # Stop any existing loader
            if self.image_loader and self.image_loader.isRunning():
                self.image_loader.terminate()
                self.image_loader.wait()
            
            # Show loading message
            self.image_label.setText("Loading image...")
            self.image_label.setStyleSheet("""
                QLabel {
                    border: 2px dashed #ccc;
                    border-radius: 8px;
                    background-color: #f9f9f9;
                    color: #666;
                }
            """)
            
            # Load image in thread
            self.image_loader = ImageLoaderThread(file_path)
            self.image_loader.image_loaded.connect(self.display_image)
            self.image_loader.start()
            
        except Exception as e:
            self.image_label.setText(f"Error loading image:\n{str(e)}")
    
    def display_image(self, file_path):
        """Display the loaded image"""
        try:
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                # Scale to fit preview area
                scaled_pixmap = pixmap.scaled(
                    300, 300,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.image_label.setPixmap(scaled_pixmap)
                self.image_label.setStyleSheet("")
                
                # Update size info
                self.image_label.setToolTip(
                    f"Image size: {pixmap.width()} x {pixmap.height()} pixels"
                )
            else:
                self.image_label.setText("Could not load image")
        except Exception as e:
            self.image_label.setText(f"Error displaying image:\n{str(e)}")
    
    def preview_text(self, file_path):
        """Preview text file content"""
        try:
            # Show text preview area
            self.text_preview.setVisible(True)
            self.image_label.setText("Text file preview below")
            
            # Read file content (limit to first 10KB for performance)
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(10240)  # Read first 10KB
                
                if len(content) >= 10240:
                    content += "\n\n[... Content truncated for preview ...]"
                
                self.text_preview.setPlainText(content)
                
                # Move cursor to top
                cursor = self.text_preview.textCursor()
                cursor.movePosition(QTextCursor.Start)
                self.text_preview.setTextCursor(cursor)
                
        except Exception as e:
            self.text_preview.setPlainText(f"Error reading file:\n{str(e)}")
            self.text_preview.setVisible(True)
    
    def preview_video(self, file_path):
        """Preview video file metadata"""
        self.image_label.setText("🎥 Video file\n\nExtracting metadata...")
        self.text_preview.setVisible(False)
        metadata = get_video_metadata(file_path)
        if metadata:
            info = [
                f"Codec: {metadata['video_codec']}",
                f"Resolution: {metadata['width']} x {metadata['height']}",
                f"Duration: {metadata['duration']:.1f} sec",
                f"Bitrate: {metadata['bit_rate'] // 1000} kbps",
                f"Frame Rate: {metadata['frame_rate']}",
                f"Audio Codec: {metadata['audio_codec']}"
            ]
            self.image_label.setText("🎥 Video file\n\n" + "\n".join(info))
        else:
            self.image_label.setText("🎥 Video file\n\nNo metadata available (ffprobe required)")
    
    def show_no_preview(self, extension):
        """Show message for files that can't be previewed"""
        file_type_info = {
            'mp4': '🎥 Video File',
            'mp3': '🎵 Audio File', 
            'pdf': '📄 PDF Document',
            'zip': '📦 Archive File',
            'exe': '⚙️ Executable File',
        }
        
        icon = file_type_info.get(extension, '📁 File')
        
        self.image_label.setText(f"{icon}\n\nNo preview available\nfor {extension.upper()} files")
        self.image_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #ccc;
                border-radius: 8px;
                background-color: #f9f9f9;
                color: #666;
                font-size: 12pt;
            }
        """)
    
    def update_properties(self, file_info):
        """Update file properties display"""
        try:
            file_path = Path(file_info.path)
            stat = file_path.stat()
            
            properties = [
                f"📄 Name: {file_info.name}",
                f"📁 Location: {file_path.parent}",
                f"📏 Size: {file_info.get_size_str()} ({file_info.size:,} bytes)",
                f"📅 Modified: {file_info.modified_date.strftime('%Y-%m-%d %H:%M:%S')}",
                f"🏷️ Type: {file_info.extension.upper() if file_info.extension else 'No extension'}",
                f"📂 Category: {file_info.category.name if file_info.category else 'Uncategorized'}",
            ]
            
            # Add image-specific properties
            if self.is_image_file(file_info.extension.lower()):
                try:
                    pixmap = QPixmap(file_info.path)
                    if not pixmap.isNull():
                        properties.append(f"🖼️ Dimensions: {pixmap.width()} x {pixmap.height()} pixels")
                        
                        # Calculate megapixels
                        megapixels = (pixmap.width() * pixmap.height()) / 1_000_000
                        if megapixels >= 1:
                            properties.append(f"📷 Resolution: {megapixels:.1f} MP")
                except:
                    pass
            
            self.properties_label.setText("\n".join(properties))
            
        except Exception as e:
            self.properties_label.setText(f"Error reading file properties:\n{str(e)}")
    
    def clear_preview(self):
        """Clear the preview panel"""
        self.current_file = None
        self.file_name_label.setText("No file selected")
        self.file_info_label.setText("")
        self.image_label.clear()
        self.image_label.setText("No preview available")
        self.image_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #ccc;
                border-radius: 8px;
                background-color: #f9f9f9;
                color: #666;
            }
        """)
        self.text_preview.setVisible(False)
        self.text_preview.clear()
        self.properties_label.setText("Select a file to view properties")
        self.open_button.setEnabled(False)
        self.open_folder_button.setEnabled(False)
    
    def open_current_file(self):
        """Open the currently previewed file"""
        if not self.current_file:
            return
        
        # Get the main window by traversing up the widget hierarchy
        main_window = self.get_main_window()
        if main_window and hasattr(main_window, 'open_file_by_path'):
            main_window.open_file_by_path(self.current_file.path)
        else:
            # Fallback: try to open file directly
            self.open_file_fallback(self.current_file.path)
    
    def open_containing_folder(self):
        """Open the folder containing the current file"""
        if not self.current_file:
            return
        
        # Get the main window by traversing up the widget hierarchy
        main_window = self.get_main_window()
        if main_window and hasattr(main_window, 'open_folder_by_path'):
            main_window.open_folder_by_path(self.current_file.path)
        else:
            # Fallback: try to open folder directly
            self.open_folder_fallback(self.current_file.path)
    
    def get_main_window(self):
        """Get the main window by traversing up the widget hierarchy"""
        widget = self
        while widget:
            if hasattr(widget, 'open_file_by_path') and hasattr(widget, 'open_folder_by_path'):
                return widget
            widget = widget.parent()
        return None
    
    def open_file_fallback(self, file_path):
        """Fallback method to open file if main window methods aren't available"""
        try:
            import platform
            import subprocess
            import os
            
            if platform.system() == 'Windows':
                os.startfile(file_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', file_path])
            else:  # Linux
                subprocess.run(['xdg-open', file_path])
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Error Opening File", str(e))
    
    def open_folder_fallback(self, file_path):
        """Fallback method to open folder if main window methods aren't available"""
        try:
            import platform
            import subprocess
            import os
            
            parent_dir = os.path.dirname(file_path)
            
            if platform.system() == 'Windows':
                subprocess.run(['explorer', '/select,', file_path])
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', parent_dir])
            else:  # Linux
                subprocess.run(['xdg-open', parent_dir])
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Error Opening Folder", str(e))
