# File Scanning & Search

## Overview
Core functionality that recursively scans directories to find files based on various criteria including file type, size, and directory depth.

## Need/Purpose
- Users need to efficiently scan large directory structures
- Find files matching specific criteria without manually browsing folders
- Handle large file systems without UI freezing
- Provide real-time feedback during long scanning operations

## Features Implemented
- ✅ Recursive directory scanning with configurable depth control
- ✅ Multi-threaded scanning to prevent UI blocking
- ✅ Real-time progress tracking with pause/resume/stop controls
- ✅ File filtering by extension/category
- ✅ Size-based filtering (min/max file size)
- ✅ Live results display as files are found
- ✅ Permission handling (graceful skip of inaccessible files)

## How to Test

### Basic Scanning
1. Launch the application
2. Select a directory using the "Browse..." button or type a path
3. Click "Search Files" to start scanning
4. **Expected Result**: Progress bar appears, files are displayed in real-time

### Category Filtering
1. Set up a scan directory
2. Select a specific category from the "File Type" dropdown (e.g., "Video")
3. Start the scan
4. **Expected Result**: Only files matching the selected category are shown

### Size Filtering
1. Set minimum size (e.g., 100 MB)
2. Optionally set maximum size (e.g., 1000 MB)
3. Start the scan
4. **Expected Result**: Only files within the size range are displayed

### Depth Control
1. Set "Max Depth" to a low value (e.g., 2)
2. Scan a directory with deep nested folders
3. **Expected Result**: Scanning stops at the specified depth level

### Scan Controls
1. Start a scan on a large directory
2. Test "Pause" button - scan should pause with option to resume
3. Test "Stop" button - scan should halt completely
4. **Expected Result**: Controls work as expected without crashing

### Performance Test
1. Scan a directory with 10,000+ files
2. Monitor memory usage and responsiveness
3. **Expected Result**: UI remains responsive, memory usage reasonable

## Technical Implementation
- **Thread**: `FileScannerThread` handles scanning in background
- **Progress**: Real-time updates via Qt signals
- **Filtering**: Applied during scan for efficiency
- **UI Updates**: Non-blocking updates to results table

## Configuration
- Default scan depth: 15 levels
- Default minimum size: 0 MB
- Scan settings persist between sessions
- Last scanned directory is remembered

## Known Limitations
- Very deep directory structures may cause stack overflow
- Network drives may be slow
- Some system directories may be inaccessible
- Large numbers of files (100k+) may slow down UI updates

## Related Features
- File Categorization (handles file type detection)
- Results Display (shows scan results)
- Settings Management (stores scan preferences)
