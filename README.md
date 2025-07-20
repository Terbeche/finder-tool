# Smart File Manager

A powerful tool for finding and organizing files on your system.

## Features

- Search for files by extension, size, and other criteria
- Categorize files automatically based on their extensions
- View file details including size, modification date, and more
- Perform operations like open, rename, and delete files
- Export search results to CSV
- Customize file categories and their colors
- Persistent settings across application restarts

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
python file_finder.py
```

## How to Use

1. Click "Browse" to select a directory to search
2. Set any filters you want to apply (file size, extensions, etc.)
3. Click "Search" to find files
4. Use the context menu (right-click) to perform actions on files
5. Access settings to customize file categories

## License

MIT
