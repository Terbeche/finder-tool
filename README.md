# Smart File Manager

A powerful tool for finding and organizing files on your system with advanced search capabilities, intelligent file management features, and comprehensive file preview functionality.

## Features

### Core Search & Organization
- **Advanced File Search**: Search by extension, size, date ranges, filename patterns (regex)
- **Content Search**: Find text within files using keyword search
- **Smart File Categorization**: Automatically categorize files based on extensions with customizable categories
- **Duplicate Detection**: Multiple detection methods (size+name, quick hash, full content hash)
- **Batch Operations**: Move, delete, and organize multiple files simultaneously

### File Management & Preview
- **File Preview Panel**: Instant image thumbnails and text file content preview
- **File Operations**: Open, rename, delete, and move files with safety confirmations
- **Batch Rename Tool**: Pattern-based file renaming with real-time preview
- **Category-based Organization**: Move files to directories organized by category
- **Export Capabilities**: Export search results to CSV format for external analysis

### Productivity Features
- **Bookmark System**: Save frequently used directories and complex search configurations
- **Search Presets**: Store and recall complex search filter combinations
- **Quick Access Panel**: One-click access to most-used locations
- **Search History**: Track and replay previous searches with timestamps and results summary
- **Cross-platform Support**: Works on Windows, macOS, and Linux

### User Interface
- **Intuitive Interface**: Clean, organized layout with collapsible advanced options
- **Real-time Results**: See files as they're found during scanning
- **Progress Tracking**: Visual progress indicators for all operations
- **Customizable Settings**: Configure categories, colors, themes, and default behaviors
- **Theme Support**: Light, Dark, and Nature themes with immediate preview

## File Preview Capabilities

The application includes a comprehensive file preview system:

### Image Preview
- **Thumbnail Display**: Automatic scaling while maintaining aspect ratio
- **Format Support**: JPG, PNG, GIF, BMP, TIFF, WebP, SVG, and more
- **Metadata Display**: Image dimensions, resolution, and megapixel information
- **Performance Optimized**: Threaded loading prevents UI blocking

### Text File Preview
- **Content Display**: First 10KB of text files for quick inspection
- **Format Support**: Programming files (Python, JS, HTML, CSS), config files, logs, documents
- **Safe Reading**: Handles various encodings with fallback protection
- **Truncation Indicator**: Clear indication when content is truncated

### File Properties
- **Comprehensive Details**: Name, path, size, modification date, file type, category
- **Smart Formatting**: Human-readable sizes and dates
- **Category Integration**: Shows file categorization and color coding
- **Quick Actions**: Direct file and folder opening from preview panel

## Advanced Search Filters

The application includes powerful advanced filtering options:

- **Date Range Filtering**: Find files modified within specific time periods
- **Regex Pattern Matching**: Use regular expressions to match complex filename patterns
- **Content Search**: Search for specific text within text files (code, documents, logs)
- **Combined Filtering**: Use multiple filters simultaneously for precise file discovery

## Bookmark & Preset System

Enhance productivity with saved locations and searches:

### Directory Bookmarks
- **Quick Access**: Save frequently used directories with custom names and descriptions
- **Usage Tracking**: Automatically sort bookmarks by frequency of use
- **One-Click Navigation**: Instant directory switching from quick access panel

### Search Presets
- **Configuration Saving**: Store complete search settings including all filters
- **Quick Recall**: Load complex search configurations with one click
- **Smart Organization**: Presets sorted by last used for easy access

## Requirements

### Python Dependencies
- PySide6 (Qt for Python)
- send2trash (for safely moving files to trash)

### System Dependencies
For Linux systems:
```
sudo apt-get install libxcb-cursor0
```

## Installation

1. Clone this repository
2. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```
3. Install system dependencies as mentioned above

## Usage

Run the application:
```
python main.py
```

## How to Use

### Basic Search
1. Click "Browse" to select a directory to search
2. Set any basic filters (file type, size range, depth limit)
3. Click "Search Files" to find files
4. Use the results table to view and manage found files
5. Select files to see instant preview in the preview panel

### Advanced Search
1. Expand the "Advanced Filters" section
2. Enable desired filters:
   - **Date Range**: Filter by file modification time
   - **Filename Pattern**: Use regex patterns like `IMG_\d{4}` or `.*\.backup\..*`
   - **Content Search**: Find files containing specific text
3. Combine with basic filters for precise results

### File Preview
1. **Select any file** in the results table
2. **View instant preview** in the preview panel:
   - **Images**: Thumbnail with dimensions and metadata
   - **Text files**: Content preview with syntax detection
   - **All files**: Comprehensive properties and quick actions
3. **Use preview buttons** to open files or containing folders directly

### Bookmark Management
1. **Save Current Location**: Use "📍 Save Location" for quick directory bookmarks
2. **Save Search Settings**: Use "💾 Save Search" to store complex filter configurations
3. **Quick Access**: Use bookmark buttons for instant navigation
4. **Full Management**: Use "Manage Bookmarks..." for complete bookmark organization

### File Operations
- **Right-click** any file for context menu options
- **Select multiple files** for batch operations
- **Use menus** for additional actions (Export, Duplicate Detection, Batch Rename)

### Duplicate Management
1. Search for files first
2. Go to Tools → "Find Duplicates..."
3. Choose detection method (Speed vs. Accuracy)
4. Review duplicate groups and select files to remove
5. Safely delete duplicates to reclaim space

### Search History
1. **Perform searches** as usual
2. **Open Search History**: Go to Tools → "Search History..."
3. **Review previous searches**: See parameters, results, and timestamps
4. **Replay searches**: Select an entry and click "Replay Search" to repeat with the same filters

## Examples

### Finding Recent Large Videos
```
Directory: /home/user/Downloads
File Type: Video
Size: 100 MB to No Limit
Advanced Filters:
  ✓ Date Range: Last 30 days
```

### Finding Configuration Files
```
Directory: /etc
Advanced Filters:
  ✓ Filename Pattern: .*\.conf$|.*\.cfg$
  ✓ Content Search: server_name
```

### Finding Old Backup Files
```
Directory: /home/user
Advanced Filters:
  ✓ Filename Pattern: .*\.backup\..*|.*~$
  ✓ Date Range: Older than 6 months
```

## Performance Tips

- Use specific file type filters to reduce search scope
- Test regex patterns on small directories first
- Content search works best on text-heavy directories
- Combine basic size/type filters before applying advanced filters
- Use bookmarks to avoid repetitive directory navigation

## Development Process

### Feature Implementation Workflow
When implementing new features, always follow this complete process:

1. **Implement the Feature**
   - Code the core functionality
   - Integrate with existing systems
   - Add proper error handling

2. **Test Thoroughly**
   - Unit test individual components
   - Integration test with existing features
   - User acceptance testing

3. **Update Documentation** (Critical - Never Skip)
   - Create feature documentation in `features/XX-feature-name.md`
   - Update `features/README.md` with new feature status
   - Update this main `README.md` with feature overview
   - Update `plan.md` to mark feature as complete

4. **Code Review and Merge**
   - Review implementation and tests
   - Ensure documentation is complete
   - Merge to main branch

### Documentation Standards
Every feature must include comprehensive documentation covering purpose, implementation, testing, limitations, and future enhancements. See the `features/` directory for examples.

## License

MIT

---

*Complete feature documentation is available in the `features/` directory. The documentation update process is a critical part of the development workflow and ensures all features are properly documented and maintainable.*
