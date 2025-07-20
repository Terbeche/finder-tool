# Batch Rename Tool

## Overview
Comprehensive batch renaming tool that allows users to rename multiple files simultaneously using patterns, find/replace operations, case conversion, and sequential numbering with real-time preview.

## Need/Purpose
- Users often need to rename multiple files with consistent patterns
- Manual renaming is time-consuming and error-prone for large file sets
- Common scenarios: organizing photos, standardizing file names, adding prefixes/suffixes
- Need for preview functionality to avoid mistakes
- Support for complex renaming operations beyond simple patterns

## Features Implemented
- ✅ Pattern-based renaming with variables
- ✅ Sequential numbering with customizable start and step
- ✅ Find and replace functionality (literal and regex)
- ✅ Case conversion options
- ✅ Extension preservation control
- ✅ Real-time preview with conflict detection
- ✅ Error validation and prevention
- ✅ Works with selected files or all results

## Pattern Variables Supported
- `{name}` - Original filename without extension
- `{counter}` - Sequential number
- `{counter:03d}` - Zero-padded number (001, 002, etc.)
- `{ext}` - File extension
- `{size}` - File size in human-readable format
- `{date}` - Current date (YYYY-MM-DD)

## How to Test

### Basic Pattern Renaming
1. Search for files to populate results
2. Select some files or use all results
3. Go to Tools menu → "Batch Rename..." OR Actions menu → "Batch Rename..."
4. Enable "Use naming pattern"
5. Enter pattern: `Photo_{counter:03d}`
6. **Expected Result**: Preview shows files renamed as Photo_001, Photo_002, etc.

### Sequential Numbering Options
1. In batch rename dialog, set pattern with counter
2. Change "Start" value to 10
3. Change "Step" value to 5
4. **Expected Result**: Files numbered as 10, 15, 20, 25, etc.

### Find and Replace Testing
1. Enable "Find and replace text"
2. Enter "IMG" in Find field
3. Enter "Image" in Replace field
4. **Expected Result**: All occurrences of "IMG" replaced with "Image"

### Regular Expression Replace
1. Enable "Find and replace text"
2. Check "Use regular expressions"
3. Find: `(\d+)`
4. Replace: `Number_\1`
5. **Expected Result**: Numbers in filenames get "Number_" prefix

### Case Conversion
1. Select different case options:
   - UPPERCASE
   - lowercase  
   - Title Case
   - Sentence case
2. **Expected Result**: Preview shows names in selected case format

### Extension Handling
1. Uncheck "Preserve file extension"
2. Set pattern: `{name}_backup.txt`
3. **Expected Result**: All files get .txt extension regardless of original

### Conflict Detection
1. Create pattern that would generate duplicate names
2. **Expected Result**: Preview shows "⚠️ Duplicate" status, Rename button disabled

### Selected vs All Files
1. **Selected files**: Select some files, open batch rename
2. **All files**: Select no files, confirm to rename all when prompted
3. **Expected Result**: Dialog shows appropriate file count and scope

## Advanced Testing

### Complex Pattern Testing
1. Pattern: `{date}_{name}_{counter:04d}`
2. **Expected Result**: Names like "2025-01-15_document_0001"

### Large File Set Testing
1. Rename 1000+ files
2. **Expected Result**: Preview generates quickly, rename operation completes successfully

### Error Handling
1. **Invalid pattern**: Use malformed format string
2. **Invalid regex**: Use malformed regular expression
3. **Permission denied**: Try to rename read-only files
4. **File conflicts**: Generate pattern creating existing filenames
5. **Expected Result**: Appropriate error messages, operation prevented

### Edge Cases
1. **Empty pattern**: Leave pattern field empty
2. **Files without extensions**: Test with extensionless files
3. **Very long names**: Generate very long filenames
4. **Special characters**: Use Unicode and special characters in patterns
5. **Expected Result**: Graceful handling of all edge cases

### Cross-Platform Testing
1. Test with different file systems (NTFS, ext4, APFS)
2. Test with files containing platform-specific characters
3. **Expected Result**: Consistent behavior across platforms

## Technical Implementation

### Pattern Processing
```python
def generate_new_name(self, file_info, index):
    pattern = self.pattern_edit.text()
    counter = self.start_number.value() + (index * self.step_number.value())
    
    new_name = pattern.format(
        name=name_without_ext,
        counter=counter,
        ext=extension.lstrip('.'),
        size=file_info.get_size_str(),
        date=datetime.now().strftime('%Y-%m-%d')
    )
    return new_name
```

### Real-time Preview
- Updates preview table on every UI change
- Validates patterns and detects conflicts
- Shows status for each file (OK, Duplicate, Error, etc.)
- Enables/disables rename button based on validation

### Conflict Detection
- Checks for duplicate names within the batch
- Checks for existing files in target directory
- Prevents destructive operations

## User Interface Features
- **Splitter layout**: Options on top, preview below
- **Real-time updates**: Preview updates as options change
- **Status indicators**: Visual feedback for conflicts and errors
- **Pattern help**: Built-in documentation for pattern variables
- **Confirmation dialogs**: Final confirmation before renaming

## Configuration Options
- Pattern templates (potential future enhancement)
- Default counter settings
- Case conversion preferences
- Extension handling defaults

## Known Limitations
- No undo functionality for rename operations
- Pattern variables limited to predefined set
- No custom date format options
- Large file sets may slow down preview updates
- No batch rename across multiple directories

## Error Prevention
- Real-time validation of patterns and regex
- Conflict detection before rename
- File permission checking
- Atomic rename operations (success or failure, no partial states)

## Future Enhancements
- **Pattern templates**: Predefined common patterns
- **Custom date formats**: User-defined date formatting
- **File metadata variables**: EXIF data, creation dates, etc.
- **Undo functionality**: Reverse batch rename operations
- **Import/Export patterns**: Save and share rename patterns
- **Directory-based renaming**: Include directory names in patterns
- **Conditional renaming**: Rules based on file properties

## Related Features
- File Operations (provides file list for renaming)
- Results Display (shows renamed files)
- File Scanning (provides files to rename)
- Settings Management (could store rename preferences)

## Dependencies
- **pathlib**: Path handling and manipulation
- **re module**: Regular expression support
- **os module**: File system operations
- **datetime**: Date formatting for patterns

## Performance Considerations
- Preview generation scales with file count
- Real-time updates may be slow with 1000+ files
- Pattern compilation cached for repeated use
- UI updates throttled for large datasets

## Security Considerations
- File permission validation before rename
- Path traversal prevention
- Invalid character filtering for filenames
- Atomic operations to prevent corruption

## Troubleshooting Guide

### Common Issues

**Problem**: Pattern not working as expected
**Solutions**:
- Check pattern syntax against help documentation
- Verify variable names are spelled correctly
- Ensure format specifiers are valid (e.g., :03d for zero-padding)

**Problem**: Regular expression errors
**Solutions**:
- Test regex patterns in online regex testers
- Escape special characters properly
- Use raw strings for complex patterns

**Problem**: Files not renaming
**Solutions**:
- Check file permissions
- Ensure files are not in use by other applications
- Verify target names don't conflict with existing files

**Problem**: Preview shows conflicts
**Solutions**:
- Adjust pattern to ensure unique names
- Modify counter settings
- Use more specific pattern variables

## Testing Checklist
- [ ] Pattern renaming with various variables
- [ ] Counter customization (start, step)
- [ ] Find and replace (literal and regex)
- [ ] Case conversion options
- [ ] Extension preservation toggle
- [ ] Conflict detection accuracy
- [ ] Error handling for invalid patterns
- [ ] Large file set performance
- [ ] Cross-platform compatibility
- [ ] Permission error handling
