# Advanced Search Filters

## Overview
Extended search capabilities that allow users to find files using sophisticated filtering criteria including date ranges, filename patterns (regex), and content search within text files. These filters work in combination with basic search options for precise file discovery.

## Need/Purpose
- Users need to find files based on specific time periods or creation dates
- Complex filename patterns require regex-based searching
- Content search helps locate files containing specific text
- Combined filtering provides powerful file discovery capabilities
- Real-time filter application improves search efficiency

## Features Implemented
- ✅ Date range filtering by file modification time
- ✅ Regular expression-based filename pattern matching
- ✅ Content search within text files
- ✅ Collapsible Advanced Filters UI section
- ✅ Real-time filter validation and application
- ✅ Filter combination with basic search criteria
- ✅ Clear filters functionality
- ✅ Intelligent file type detection for content search

## How to Test

### Basic Advanced Filters Access
1. Start the application and navigate to a directory
2. Look for "Advanced Filters" section below basic search options
3. Check the checkbox to expand the advanced filters section
4. **Expected Result**: Advanced filter options become visible and accessible

### Date Range Filtering
1. Enable "Filter by date range" checkbox
2. Set "From" date to 7 days ago
3. Set "To" date to today
4. Run a search
5. **Expected Result**: Only files modified within the last 7 days are shown

#### Date Range Test Cases
- **Recent files**: Set range to last 24 hours
- **Old files**: Set range to >1 year ago
- **Specific period**: Set exact date range (e.g., January 2024)
- **Invalid range**: Set "From" date after "To" date
- **Expected Results**: Appropriate files found, invalid ranges handled gracefully

### Filename Pattern Matching (Regex)
1. Enable "Filename pattern (regex)" checkbox
2. Test various patterns:
   - `IMG_\d{4}` - Find files like IMG_1234.jpg
   - `.*\.backup\..*` - Find backup files
   - `^test.*\.py$` - Find Python test files
   - `[Ss]creenshot.*` - Case-insensitive screenshot files
3. **Expected Result**: Files matching regex patterns are found

#### Pattern Test Cases
- **Simple patterns**: `*.pdf`, `document*`
- **Complex regex**: `^[A-Z]{2,3}_\d{4}_.*\.(jpg|png)$`
- **Case sensitivity**: Test with mixed case patterns
- **Invalid regex**: Enter malformed regex pattern
- **Expected Results**: Valid patterns work, invalid patterns are ignored

### Content Search in Text Files
1. Enable "Content search (text files only)" checkbox
2. Enter search terms:
   - Simple words: "function", "class", "import"
   - Phrases: "def main", "if __name__"
   - Technical terms: "TODO", "FIXME", "Copyright"
3. Search in directory with code/text files
4. **Expected Result**: Only files containing the search term are shown

#### Content Search Test Cases
- **Code files**: Search for "def " in Python files
- **Configuration files**: Search for specific settings
- **Log files**: Search for error messages or timestamps
- **Mixed content**: Search in directory with both text and binary files
- **Large files**: Test content search performance on large text files
- **Expected Results**: Accurate content matching, reasonable performance

### Combined Filter Testing
1. Enable multiple filters simultaneously:
   - Date range: Last 30 days
   - Pattern: `.*\.(py|js|html)$`
   - Content: "function"
2. Run search
3. **Expected Result**: Files must match ALL enabled filters

### Filter Interaction Testing
1. **Basic + Advanced**: Combine file type selection with date range
2. **Size + Pattern**: Combine size filters with filename patterns
3. **All filters**: Enable all basic and advanced filters
4. **Expected Result**: Filters work together logically

### Clear Filters Functionality
1. Set multiple advanced filters
2. Click "Clear Filters" button
3. **Expected Result**: All advanced filters are reset to default state

## Advanced Testing

### Performance Testing
1. **Large directories**: Test advanced filters on 10,000+ files
2. **Complex regex**: Use computationally expensive patterns
3. **Content search**: Search large text files (>10MB)
4. **Combined filters**: Multiple simultaneous filters on large datasets
5. **Expected Result**: Reasonable performance, no UI freezing

### Edge Cases
1. **Empty search terms**: Enable filters with empty input fields
2. **Very long patterns**: Extremely long regex patterns
3. **Binary files**: Content search on non-text files
4. **Permission denied**: Filters on inaccessible files
5. **Network drives**: Advanced filters on slow network storage
6. **Expected Result**: Graceful handling of all edge cases

### Regex Pattern Validation
1. **Valid patterns**: Standard regex constructs
2. **Invalid syntax**: Malformed regex patterns
3. **Performance killers**: Patterns causing excessive backtracking
4. **Special characters**: Regex metacharacters in patterns
5. **Expected Result**: Valid patterns work, invalid ones are ignored safely

### Content Search Limitations
1. **File encoding**: Test with UTF-8, ASCII, other encodings
2. **Binary files**: Ensure binary files are skipped appropriately
3. **Large files**: Test memory usage with very large text files
4. **Special characters**: Search for Unicode characters
5. **Expected Result**: Robust handling of various file types and encodings

## Technical Implementation

### Date Range Filtering
- Uses file modification timestamp (`stat().st_mtime`)
- Converts QDate to Python date objects for comparison
- Applied during file scanning for efficiency

### Regex Pattern Matching
- Compiles regex patterns using Python's `re` module
- Case-insensitive matching by default
- Invalid patterns are silently ignored to prevent crashes
- Applied to filename only, not full path

### Content Search Algorithm
```python
# Text file extensions for content search
text_extensions = {
    'txt', 'md', 'py', 'js', 'html', 'css', 'xml', 'json', 
    'csv', 'log', 'conf', 'ini', 'cfg', 'yml', 'yaml'
}

# Content search implementation
def search_file_content(file_path, search_term):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(1024 * 1024)  # Read first 1MB
            return search_term.lower() in content.lower()
    except (IOError, UnicodeDecodeError):
        return True  # Skip files that can't be read
```

### UI Implementation
- Collapsible QGroupBox for advanced filters section
- Real-time enable/disable of filter controls
- Checkbox-controlled filter activation
- Clear filters resets all advanced filter state

## Configuration and Settings
- Advanced filter preferences persist between sessions
- Default date ranges (last 30 days)
- Regex pattern history (potential future enhancement)
- Content search file type associations

## Known Limitations
- Content search limited to first 1MB of each file
- Regex patterns may impact performance on large datasets
- Binary file detection based on extension, not content analysis
- No preview of how many files match each filter before applying
- Date filtering only uses modification time, not creation time

## Troubleshooting Guide

### Common Issues

**Problem**: Regex pattern not finding expected files
**Solutions**: 
- Verify regex syntax using online regex testers
- Check case sensitivity requirements
- Ensure pattern matches filename, not full path

**Problem**: Content search not finding known text
**Solutions**:
- Verify file is recognized as text file type
- Check file encoding (UTF-8 preferred)
- Ensure search term spelling is correct
- File might be larger than 1MB search limit

**Problem**: Date range filter returning unexpected results
**Solutions**:
- Check system time zone settings
- Verify file modification dates using file manager
- Ensure date range is logically valid (from < to)

**Problem**: Advanced filters slow down search significantly
**Solutions**:
- Use simpler regex patterns
- Limit content search to smaller directories
- Disable unnecessary advanced filters
- Consider using basic filters first to reduce dataset

### Performance Tips
1. Use specific basic filters (file type, size) before applying advanced filters
2. Test regex patterns on small datasets first
3. Content search works best on directories with primarily text files
4. Date range filters are fastest, use them when possible

## Security Considerations
- Regex patterns are compiled safely with error handling
- File content is read with encoding error handling
- No execution of file content, only text searching
- Permission errors are handled gracefully

## Future Enhancements
- **Content search improvements**: Full file content indexing
- **Pattern suggestions**: Common regex pattern templates
- **Filter presets**: Save and reload filter combinations
- **Advanced date options**: Creation date, access date filtering
- **File metadata search**: Search by EXIF data, document properties
- **Search within archives**: Content search inside ZIP/RAR files
- **Performance optimization**: Parallel processing for large datasets

## Integration with Other Features
- **File Scanning**: Advanced filters applied during scan process
- **File Categories**: Works with category-based filtering
- **Export Results**: Filtered results can be exported to CSV
- **Duplicate Detection**: Can find duplicates within filtered results
- **File Operations**: All file operations work on filtered results

## Related Features
- File Scanning (provides base functionality)
- Results Display (shows filtered results)
- Settings Management (stores filter preferences)
- File Operations (acts on filtered files)

## Dependencies
- **re module**: Python regular expressions
- **datetime**: Date handling and comparison
- **pathlib**: File system operations
- **QDate**: Qt date handling for UI
- [ ] Date range filtering works correctly
- [ ] Filename pattern matching functions
- [ ] Content search finds text in files
- [ ] Filters can be enabled/disabled independently
- [ ] Clear filters button resets all filters

### Advanced Scenarios
- [ ] Multiple filters work together (AND logic)
- [ ] Invalid regex patterns handled gracefully
- [ ] Large file content search performs adequately
- [ ] Binary files skipped in content search
- [ ] Date range edge cases handled properly

### Performance Testing
- [ ] 1000+ files with content search completes
- [ ] Large files (>100MB) don't cause memory issues
- [ ] Complex regex patterns don't slow down search significantly
- [ ] UI remains responsive during filtered searches

### Error Handling
- [ ] Permission denied files don't crash search
- [ ] Corrupted text files handled gracefully
- [ ] Invalid date ranges handled appropriately
- [ ] Network disconnection during search handled properly
