# Advanced Search Filters

## Overview
Enhanced search capabilities that allow users to filter files by date ranges, filename patterns (regex), and content search within text files, providing more precise and powerful file discovery options.

## Need/Purpose
- Users need more granular control over search criteria
- Find files modified within specific time periods
- Locate files with specific naming patterns
- Search for files containing specific text content
- Reduce search noise by applying multiple filter criteria
- Support complex file discovery workflows

## Features Implemented
- ✅ Date range filtering (modification date)
- ✅ Filename pattern matching with regex support
- ✅ Content search within text files
- ✅ Collapsible advanced filters UI
- ✅ Filter combination capabilities
- ✅ Clear filters functionality
- ✅ Real-time filter validation
- ✅ Performance optimized content search

## How to Test

### Date Range Filtering
1. Search for files in a directory with files from different time periods
2. Expand "Advanced Filters" section
3. Check "Filter by date range"
4. Set "From" date to one week ago, "To" date to today
5. Start search
6. **Expected Result**: Only files modified within the date range are shown

### Filename Pattern Matching
1. Search in a directory with various file names
2. Enable "Filename pattern (regex)"
3. Test patterns:
   - `IMG_\d{4}` - finds files like IMG_1234.jpg
   - `.*\.backup\..*` - finds files containing ".backup."
   - `^test.*\.py$` - finds Python files starting with "test"
4. **Expected Result**: Only files matching the regex pattern are displayed

### Content Search
1. Search in a directory containing text files
2. Enable "Content search (text files only)"
3. Enter search terms like "TODO", "import", or "function"
4. Start search
5. **Expected Result**: Only text files containing the search term are found

### Combined Filters
1. Enable multiple filters simultaneously:
   - Date range: Last 7 days
   - Pattern: `.*\.py$` (Python files)
   - Content: "class"
2. **Expected Result**: Only Python files from last 7 days containing "class" are shown

### Filter Management
1. Set up multiple advanced filters
2. Click "Clear Filters" button
3. **Expected Result**: All advanced filters are reset to default state

## Advanced Testing

### Regex Pattern Validation
1. **Valid patterns**: Test with various regex patterns
2. **Invalid patterns**: Enter malformed regex (e.g., `[unclosed`)
3. **Case sensitivity**: Test patterns with different cases
4. **Expected Result**: Invalid regex gracefully ignored, case-insensitive matching

### Date Range Edge Cases
1. **Future dates**: Set date range in the future
2. **Inverted range**: Set "From" date after "To" date
3. **Single day**: Set both dates to same day
4. **Expected Result**: Appropriate handling of edge cases

### Content Search Performance
1. **Large text files**: Search in files >10MB
2. **Binary files**: Verify binary files are skipped appropriately
3. **Many files**: Search content in 1000+ text files
4. **Special characters**: Search for Unicode and special characters
5. **Expected Result**: Reasonable performance, no crashes

### Filter Combinations
1. Test all possible combinations of filters
2. Verify filters work independently and together
3. Test with empty result sets
4. **Expected Result**: Logical AND operation between all filters

## Technical Implementation

### Date Filtering
```python
def _check_date_filter(self, file_mtime):
    file_date = file_mtime.date()
    if 'date_from' in filters and file_date < filters['date_from']:
        return False
    if 'date_to' in filters and file_date > filters['date_to']:
        return False
    return True
```

### Regex Pattern Matching
```python
try:
    pattern = re.compile(regex_pattern, re.IGNORECASE)
    return bool(pattern.search(filename))
except re.error:
    return True  # Skip invalid patterns
```

### Content Search
```python
# Only search in text files, read first 1MB
with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read(1024 * 1024).lower()
    return search_term in content
```

## User Interface Design

### Collapsible Advanced Filters
- Default: Collapsed to keep UI clean
- Expandable: Shows additional filter options
- Clear visual hierarchy
- Responsive layout

### Filter Controls
- **Date Range**: Calendar popup selectors
- **Pattern**: Text input with regex hint
- **Content**: Text input with placeholder
- **Enable/Disable**: Checkboxes for each filter type

### Visual Feedback
- Disabled state for inactive filters
- Clear button for easy reset
- Status messages during search

## Performance Considerations

### Content Search Optimization
- Limited to text file extensions only
- Reads maximum 1MB per file
- Graceful error handling for unreadable files
- Skip binary files automatically

### Memory Management
- Streaming file processing
- No loading entire file content into memory
- Efficient regex compilation and reuse

### Search Speed
- Filters applied during scan (not post-processing)
- Early termination on filter failures
- Progress tracking includes filter overhead

## Configuration Settings

### Default Values
- Date range: Last 30 days when enabled
- Content search: Case-insensitive
- Pattern matching: Case-insensitive regex
- Text file extensions: Configurable list

### Persistence
- Advanced filter states not persisted (reset each session)
- Last used patterns could be saved (future enhancement)
- Filter preferences in settings (future enhancement)

## Error Handling

### Regex Patterns
- Invalid regex patterns silently ignored
- Error messages in status bar (future enhancement)
- Pattern validation hints (future enhancement)

### File Access Errors
- Permission denied files skipped gracefully
- Binary files handled appropriately
- Corrupted files don't crash search

### Large Files
- Content search limited to prevent memory issues
- Timeout protection for very large files
- Progress indication for long operations

## Known Limitations

### Content Search
- Text files only (no PDF, DOC content search)
- Limited to first 1MB of file content
- No multi-language encoding detection
- No fuzzy or stemming search

### Pattern Matching
- Filename only (not full path regex)
- No glob pattern support (only regex)
- No pattern suggestions or validation UI

### Date Filtering
- Modification date only (not creation or access date)
- No relative date expressions ("last week", "yesterday")
- No time-of-day filtering (date only)

## Future Enhancements

### Enhanced Content Search
- PDF and Office document content search
- Multi-language encoding detection
- Fuzzy search and stemming
- Search result highlighting

### Advanced Pattern Support
- Glob pattern support alongside regex
- Path-based pattern matching
- Pattern builder UI with common patterns
- Pattern history and favorites

### Extended Date Filtering
- Creation and access date options
- Relative date expressions
- Time-based filtering (hour, minute)
- Date range presets (last week, last month)

### Performance Improvements
- Indexed content search for faster repeat searches
- Parallel file processing
- Smart caching of filter results
- Background indexing option

## Related Features
- File Scanning (applies filters during scan)
- File Categorization (works with category filtering)
- Results Display (shows filtered results)
- Export Functionality (exports filtered results)
- Settings Management (filter preferences)

## Dependencies
- **re module**: For regex pattern matching
- **datetime**: For date range processing
- **QDateEdit**: For date selection UI
- **QCheckBox**: For filter enable/disable
- **file_scanner_thread**: Enhanced with filter support

## Testing Checklist

### Basic Functionality
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
