# Smart File Manager

A powerful tool for finding and organizing files on your system with advanced search capabilities and intelligent file management features.

## Features

### Core Search & Organization
- **Advanced File Search**: Search by extension, size, date ranges, filename patterns (regex)
- **Content Search**: Find text within files using keyword search
- **Smart File Categorization**: Automatically categorize files based on extensions with customizable categories
- **Duplicate Detection**: Multiple detection methods (size+name, quick hash, full content hash)
- **Batch Operations**: Move, delete, and organize multiple files simultaneously

### File Management
- **File Operations**: Open, rename, delete, and move files with safety confirmations
- **Category-based Organization**: Move files to directories organized by category
- **Export Capabilities**: Export search results to CSV format for external analysis
- **Cross-platform Support**: Works on Windows, macOS, and Linux

### User Interface
- **Intuitive Interface**: Clean, organized layout with collapsible advanced options
- **Real-time Results**: See files as they're found during scanning
- **Progress Tracking**: Visual progress indicators for all operations
- **Customizable Settings**: Configure categories, colors, and default behaviors

## Advanced Search Filters

The application includes powerful advanced filtering options:

- **Date Range Filtering**: Find files modified within specific time periods
- **Regex Pattern Matching**: Use regular expressions to match complex filename patterns
- **Content Search**: Search for specific text within text files (code, documents, logs)
- **Combined Filtering**: Use multiple filters simultaneously for precise file discovery

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

### Advanced Search
1. Expand the "Advanced Filters" section
2. Enable desired filters:
   - **Date Range**: Filter by file modification time
   - **Filename Pattern**: Use regex patterns like `IMG_\d{4}` or `.*\.backup\..*`
   - **Content Search**: Find files containing specific text
3. Combine with basic filters for precise results

### File Operations
- **Right-click** any file for context menu options
- **Select multiple files** for batch operations
- **Use menus** for additional actions (Export, Duplicate Detection, etc.)

### Duplicate Management
1. Search for files first
2. Go to Tools → "Find Duplicates..."
3. Choose detection method (Speed vs. Accuracy)
4. Review duplicate groups and select files to remove
5. Safely delete duplicates to reclaim space

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

## License

MIT
