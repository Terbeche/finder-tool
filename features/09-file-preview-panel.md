# File Preview Panel

## Overview
Interactive file preview panel that provides instant thumbnails for images, content preview for text files, and detailed file properties without requiring external applications. Enhances user productivity by allowing quick file inspection before opening or processing.

## Need/Purpose
- Users need to quickly identify file contents without opening multiple applications
- Image files require thumbnail previews for visual identification
- Text files need content preview to verify contents before editing
- File properties should be easily accessible for decision making
- Reduce time spent opening/closing files just to check their contents
- Improve workflow efficiency for file management tasks

## Features Implemented
- ✅ **Image Preview with Thumbnails**
  - Automatic image scaling to fit preview area
  - Support for common formats (JPG, PNG, GIF, BMP, TIFF, WebP, SVG)
  - Maintains aspect ratio during scaling
  - Shows image dimensions and resolution information
  - Threaded image loading to prevent UI blocking

- ✅ **Text File Content Preview**
  - First 10KB content preview for performance
  - Support for multiple text formats (TXT, MD, Python, JS, HTML, CSS, XML, JSON, CSV, logs, config files)
  - Syntax-aware file type detection
  - Content truncation indicator for large files
  - Error-safe reading with encoding fallback

- ✅ **Comprehensive File Properties**
  - File name, location, size (bytes and human-readable)
  - Modification date and time
  - File type and category information
  - Image-specific metadata (dimensions, megapixels)
  - Extension and categorization details

- ✅ **Interactive Panel Controls**
  - Toggle panel visibility via View menu
  - Resizable splitter layout (70% table, 30% preview)
  - Quick access buttons (Open File, Open Folder)
  - Scrollable content area for large previews
  - Collapsible panel support

- ✅ **Smart File Type Recognition**
  - Automatic detection of previewable content
  - Fallback display for unsupported file types
  - File type icons and descriptions
  - Category-based styling and information

## Components

### PreviewPanel Class
**Location**: `preview_panel.py`
**Purpose**: Main widget containing all preview functionality

#### UI Components
- **Header Section**: File name and basic info display
- **Content Area**: Scrollable area for previews and properties
- **Image Label**: Displays scaled image thumbnails
- **Text Preview**: QTextEdit for file content display
- **Properties Panel**: Detailed file metadata
- **Action Buttons**: Open file and folder operations

#### Threading Support
- **ImageLoaderThread**: Background image loading and scaling
- **Non-blocking Operations**: Prevents UI freezing during file processing
- **Safe Threading**: Proper cleanup and termination handling

### Integration Points
- **Main Window**: Splitter layout with results table
- **File Selection**: Automatic preview updates on selection change
- **Menu System**: Toggle visibility via View menu
- **File Operations**: Direct integration with open/folder actions

## How to Test

### Basic Preview Functionality
1. **Start Application** and search for files in a directory with mixed content
2. **Select an image file** in the results table
3. **Expected Result**: Image thumbnail appears in preview panel with properties
4. **Select a text file** (Python, log, config, etc.)
5. **Expected Result**: File content appears in text preview area

### Image Preview Testing
1. **Test Multiple Formats**: Select JPG, PNG, GIF, SVG files
2. **Check Scaling**: Verify images scale to fit preview area
3. **Verify Aspect Ratio**: Ensure images maintain correct proportions
4. **Test Large Images**: Check performance with high-resolution images
5. **Expected Result**: All formats display correctly with proper scaling

### Text File Preview Testing
1. **Test Different Extensions**: Python (.py), JavaScript (.js), HTML, CSS, XML, JSON
2. **Test Configuration Files**: .conf, .ini, .cfg, .yml files
3. **Test Large Files**: Verify 10KB limit and truncation indicator
4. **Test Binary Files**: Ensure graceful handling of non-text files
5. **Expected Result**: Text content displays correctly with proper truncation

### Properties Display Testing
1. **Verify Basic Properties**: Name, path, size, modification date
2. **Check Image Metadata**: Dimensions, megapixels for image files
3. **Test Category Display**: Verify correct category assignment
4. **Check Size Formatting**: Ensure proper B/KB/MB/GB display
5. **Expected Result**: All properties display accurately

### Panel Controls Testing
1. **Toggle Visibility**: Use View → Toggle Preview Panel
2. **Test Splitter**: Resize panel by dragging splitter
3. **Test Buttons**: Use "Open File" and "Open Folder" buttons
4. **Test Scrolling**: Verify scrollable content for large previews
5. **Expected Result**: All controls function correctly

### Performance Testing
1. **Rapid Selection**: Quickly select multiple files in sequence
2. **Large Image Files**: Test with high-resolution images (>10MB)
3. **Large Text Files**: Test with files exceeding 10KB limit
4. **Memory Usage**: Monitor for memory leaks during extended use
5. **Expected Result**: Smooth performance without freezing or crashes

## Technical Implementation

### File Type Detection
```python
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
```

### Threading Architecture
```python
class ImageLoaderThread(QThread):
    """Thread for loading images without blocking UI"""
    image_loaded = Signal(str)  # file_path
    
    def run(self):
        # Load and scale image in background
        pixmap = QPixmap(self.file_path)
        scaled_pixmap = pixmap.scaled(300, 300, Qt.KeepAspectRatio)
        self.image_loaded.emit(self.file_path)
```

### Integration with Main Window
```python
def on_file_selection_changed(self, selected, deselected):
    """Handle file selection change to update preview"""
    selected_indexes = self.results_table.selectionModel().selectedRows()
    
    if selected_indexes:
        row = selected_indexes[0].row()
        if row < len(self.files):
            file_info = self.files[row]
            self.preview_panel.preview_file(file_info)
    else:
        self.preview_panel.clear_preview()
```

## Configuration Options
- **Preview Panel Visibility**: Default enabled, toggleable via View menu
- **Image Scaling Size**: Maximum 300x300 pixels for performance
- **Text Preview Limit**: 10KB maximum for memory efficiency
- **Supported File Types**: Configurable extension lists
- **Splitter Proportions**: 70% table, 30% preview (user adjustable)

## Known Limitations
- **Text Preview Size**: Limited to first 10KB of file content
- **Image Formats**: Limited to Qt-supported formats (no RAW camera files)
- **Video Preview**: No video thumbnail generation (shows file type icon)
- **Audio Preview**: No waveform or metadata display
- **PDF Preview**: No PDF content rendering (treated as binary file)
- **Archive Preview**: No archive content listing
- **Performance**: Large images may take time to load and scale

## Future Enhancements
- **Video Thumbnails**: Generate preview frames for video files
- **PDF Preview**: Render first page of PDF documents
- **Audio Metadata**: Display duration, bitrate, codec information
- **Code Syntax Highlighting**: Syntax coloring for programming files
- **Archive Content**: List contents of ZIP/RAR files
- **Hex Preview**: Hex dump view for binary files
- **Image EXIF Data**: Camera settings, GPS location, creation date
- **Configurable Limits**: User-adjustable preview size limits
- **Preview Cache**: Cache generated thumbnails for faster access

## Error Handling
- **File Access Errors**: Graceful handling of permission denied
- **Corrupted Files**: Safe fallback for damaged image/text files
- **Memory Errors**: Protection against excessive memory usage
- **Thread Safety**: Proper cleanup of background threads
- **Encoding Issues**: UTF-8 fallback with error ignoring

## Performance Considerations
- **Lazy Loading**: Images loaded only when selected
- **Memory Management**: Automatic cleanup of large images
- **Thread Pooling**: Reuse of image loader threads
- **Content Limits**: Strict limits on preview content size
- **UI Responsiveness**: Non-blocking operations for all previews

## Integration with Other Features
- **File Operations**: Direct integration with open/folder actions
- **Bookmark System**: Preview updates when using bookmarked locations
- **Search Results**: Automatic preview for any search results
- **Duplicate Detection**: Preview comparison for duplicate files
- **Batch Operations**: Preview context for file selection decisions

## Testing Checklist
- [ ] Image preview for all supported formats
- [ ] Text preview for programming and config files
- [ ] Properties display accuracy and formatting
- [ ] Panel toggle and splitter resize functionality
- [ ] Open File and Open Folder button operations
- [ ] Performance with large files and rapid selection
- [ ] Error handling for corrupted or inaccessible files
- [ ] Thread cleanup and memory management
- [ ] Cross-platform file path and operation compatibility
- [ ] Integration with main window selection and menu actions

## Troubleshooting Guide

### Common Issues

**Problem**: Images not loading or displaying
**Solutions**:
- Check file permissions and accessibility
- Verify file format is supported by Qt
- Monitor console for threading errors
- Restart application if image loader thread is stuck

**Problem**: Text preview showing garbled content
**Solutions**:
- Check file encoding (non-UTF8 files may display incorrectly)
- Verify file is actually text-based, not binary
- Check for very long lines that may cause display issues

**Problem**: Preview panel not updating on selection
**Solutions**:
- Verify file selection signals are connected properly
- Check if files list and table indices are synchronized
- Restart application if selection tracking is broken

**Problem**: Performance issues with large files
**Solutions**:
- Check if files exceed the 10KB text preview limit
- Monitor memory usage for large image files
- Verify thread cleanup is working properly
- Consider reducing preview size limits

**Problem**: Open File/Folder buttons not working
**Solutions**:
- Check file paths are valid and accessible
- Verify platform-specific open commands are working
- Test with different file types and locations
- Check for permission issues with target files/folders

## Dependencies
- **PySide6.QtGui.QPixmap**: Image loading and scaling
- **PySide6.QtCore.QThread**: Background image processing
- **PySide6.QtWidgets**: UI components and layouts
- **pathlib.Path**: Cross-platform path handling
- **os.path**: File system operations
- **Built-in Python**: File I/O and text processing

## Security Considerations
- **File Access Validation**: Check permissions before opening files
- **Safe Text Reading**: Use error-ignoring encoding fallback
- **Path Traversal Protection**: Validate file paths before operations
- **Memory Limits**: Prevent excessive memory usage with large files
- **Thread Safety**: Proper synchronization of UI updates
