# File Operations

## Overview
Core file management operations that can be performed on search results, including opening files, navigating to locations, renaming, moving, and deleting files.

## Need/Purpose
- Users need to act on search results without leaving the application
- Quick access to files and their containing folders
- Safe file operations with confirmation dialogs
- Batch operations for efficiency
- Integration with system file manager and default applications

## Features Implemented
- ✅ Open files with system default applications
- ✅ Open containing folder and highlight file
- ✅ Rename individual files
- ✅ Move files to custom directories with organization options
- ✅ Delete files (with trash support via send2trash)
- ✅ Multi-file selection and batch operations
- ✅ Cross-platform compatibility (Windows, macOS, Linux)
- ✅ Error handling and user feedback
- ✅ Operation confirmation dialogs

## How to Test

### Open File with Default Application
1. Search for files and select a result (e.g., image, document, video)
2. Right-click → "Open" OR go to File menu → "Open"
3. **Expected Result**: File opens in system default application

### Open Containing Folder
1. Select any file from search results
2. Right-click → "Open Containing Folder" OR File menu → "Open Containing Folder"
3. **Expected Result**: 
   - Windows: Explorer opens with file selected
   - macOS: Finder opens to parent directory
   - Linux: File manager opens to parent directory

### Rename File
1. Select a single file from results
2. Right-click → "Rename File" OR Actions menu → "Rename File"
3. Choose new location/name in the file dialog
4. Click Save
5. **Expected Result**: File is renamed, table updates with new name

### Move Files to Directory
1. Select one or more files from results
2. Actions menu → "Move to Directory..." OR right-click → "Move to Directory..."
3. Select target directory
4. Choose organization option:
   - "Yes" = Organize by category (creates subdirectories)
   - "No" = Move directly to target
5. Confirm the operation
6. **Expected Result**: Files are moved, progress dialog shows, results table updates

### Delete Files (with Trash Support)
1. Select one or more files
2. Actions menu → "Delete Selected Files" OR right-click → "Delete Selected Files"
3. Confirm deletion
4. **Expected Result**: 
   - If send2trash installed: Files moved to system trash
   - If not installed: Option to permanently delete or install send2trash

### Batch Operations
1. Select multiple files (Ctrl+click or Shift+click)
2. Perform any operation (move, delete)
3. **Expected Result**: Operation applies to all selected files with progress tracking

## Platform-Specific Testing

### Windows
1. Test file opening with various applications
2. Test "Open Containing Folder" - should open Explorer with file highlighted
3. Test moving files to different drives
4. **Expected Result**: All operations work with Windows conventions

### macOS
1. Test with macOS default applications
2. Test "Open Containing Folder" - should open Finder
3. Test with files containing special characters
4. **Expected Result**: Native macOS behavior

### Linux
1. Test with various desktop environments (GNOME, KDE, XFCE)
2. Test xdg-open functionality
3. Test with different file managers
4. **Expected Result**: Works with standard Linux desktop conventions

## Advanced Testing

### Error Handling
1. **Permission Errors**: Try to delete read-only files
2. **Missing Files**: Delete file externally, then try to operate on it
3. **Full Disk**: Try moving large files to full partition
4. **Network Issues**: Operations on network drives with connectivity problems
5. **Expected Result**: Graceful error messages, no crashes

### File Conflicts
1. **Move Conflicts**: Move file to directory with same-named file
2. **Rename Conflicts**: Rename to existing filename
3. **Expected Result**: Automatic conflict resolution (numbering) or user choice

### Large File Operations
1. Select 1000+ files for deletion
2. Move very large files (several GB)
3. **Expected Result**: Progress dialogs, cancellation options, no UI freezing

### Special File Types
1. **System Files**: Try operations on protected system files
2. **Hidden Files**: Operations on dot-files (Linux/macOS)
3. **Symlinks**: Test with symbolic links
4. **Lock Files**: Files currently in use by other applications
5. **Expected Result**: Appropriate handling for each case

## Technical Implementation

### Cross-Platform File Operations
```python
# Windows
os.startfile(file_path)  # Open file
subprocess.run(['explorer', '/select,', file_path])  # Show in Explorer

# macOS  
subprocess.run(['open', file_path])  # Open file
subprocess.run(['open', parent_dir])  # Show in Finder

# Linux
subprocess.run(['xdg-open', file_path])  # Open file
subprocess.run(['xdg-open', parent_dir])  # Show in file manager
```

### Safe Deletion
- Primary: Uses `send2trash` library for trash functionality
- Fallback: Direct `os.remove()` with user confirmation
- Error handling for permission issues

### Move Operations
- Uses `shutil.move()` for reliable cross-platform moves
- Automatic conflict resolution with numbering
- Progress tracking for large operations
- Category-based organization option

## Configuration
- Trash preference (if send2trash not available)
- Default move behavior (organize vs direct)
- Confirmation dialog settings

## Known Limitations
- Rename operation uses save dialog (not in-place editing)
- No undo functionality for destructive operations
- Move operations don't preserve extended attributes on all platforms
- Large batch operations may be slow
- Network drive operations depend on connectivity

## Dependencies
- **send2trash**: Optional, for safe deletion to trash
- **pathlib**: For cross-platform path handling
- **shutil**: For file operations
- **subprocess**: For system integration

## Security Considerations
- All destructive operations require confirmation
- Permission errors are handled gracefully
- No operations on system-critical directories
- File paths are validated before operations

## Related Features
- Results Display (shows files to operate on)
- Progress Tracking (for long operations)
- Settings Management (operation preferences)
- Duplicate Detection (provides files for bulk operations)
