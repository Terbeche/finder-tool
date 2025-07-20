# Advanced Search Filters

## Overview
Enhanced search capabilities that allow users to filter files based on multiple criteria including date ranges, filename patterns (regex), and content search within text files, providing precise file discovery beyond basic size and type filters.

## Need/Purpose
- Users need more granular control over file searches
- Find files modified within specific time periods
- Locate files with specific naming patterns
- Search for files containing specific text content
- Combine multiple criteria for precise results
- Reduce result sets to focus on relevant files

## Features Implemented
- ✅ Date range filtering by modification time
- ✅ Filename pattern matching using regular expressions
- ✅ Content search within text files
- ✅ Collapsible advanced filters section
- ✅ Filter combination logic
- ✅ Clear filters functionality
- ✅ Real-time filter application during scan
- ✅ Persistent filter settings per session

## Advanced Filter Types

### 1. Date Range Filter
- **Purpose**: Find files modified within specific time periods
- **Implementation**: Modification date comparison
- **UI**: Calendar date pickers for from/to dates
- **Default Range**: Last 30 days to current date

### 2. Filename Pattern Filter  
- **Purpose**: Match files with specific naming patterns
- **Implementation**: Regular expression matching (case-insensitive)
- **Examples**:
  - `IMG_\d{4}` - Find image files with 4-digit numbers
  - `.*\.backup\..*` - Find backup files
  - `^test.*\.py$` - Find Python test files
  - `\d{4}-\d{2}-\d{2}` - Find files with date patterns

### 3. Content Search Filter
- **Purpose**: Find text files containing specific content
- **Implementation**: Text search within file contents
- **Scope**: Limited to recognized text file extensions
- **Performance**: Reads first 1MB of each file to avoid memory issues
- **Supported Extensions**: txt, md, py, js, html, css, xml, json, csv, log, conf, ini, cfg, yml, yaml, sh, bat, ps1

## How to Test

### Basic Date Range Filtering
1. Expand "Advanced Filters" section
2. Check "Filter by date range"
3. Set "From" date to 1 week ago
4. Set "To" date to today
5. Start a search
6. **Expected Result**: Only files modified within the last week are shown

### Filename Pattern Matching
1. Enable "Filename pattern (regex)" checkbox
2. Test patterns:
   - `\d+` - Files with numbers in the name
   - `^IMG` - Files starting with "IMG"
   - `\.log$` - Files ending with .log
   - `backup` - Files containing "backup"
3. Start search
4. **Expected Result**: Only files matching the pattern are found

### Content Search Testing
1. Enable "Content search (text files only)"
2. Enter search terms:
   - `function` - Find files containing "function"
   - `import` - Find files with import statements
   - `TODO` - Find files with TODO comments
3. Start search
4. **Expected Result**: Only text files containing the search term are shown

### Combined Filters Testing
1. Enable multiple filters simultaneously:
   - Date range: Last 7 days
   - Pattern: `\.py$` (Python files)
   - Content: `class`
2. Start search
3. **Expected Result**: Only Python files from last 7 days containing "class"

### Filter Persistence
1. Set up multiple filters
2. Perform a search
3. Start a new search without changing filters
4. **Expected Result**: Filters remain active until manually cleared

## Advanced Testing Scenarios

### Date Range Edge Cases
1. **Same Date Range**: Set from and to date to same day
2. **Future Dates**: Set range in the future
3. **Reverse Range**: Set 'from' date after 'to' date
4. **Year Boundaries**: Test across year boundaries
5. **Expected Result**: Appropriate handling of edge cases

### Regex Pattern Validation
1. **Invalid Regex**: Enter malformed patterns like `[abc`
2. **Complex Patterns**: Test nested groups `(img|photo)_\d{4}`
3. **Case Sensitivity**: Verify case-insensitive matching
4. **Unicode**: Test with international characters
5. **Expected Result**: Graceful handling of invalid patterns, robust matching

### Content Search Performance
1. **Large Files**: Search in files >100MB
2. **Binary Files**: Search in non-text files (should be skipped)
3. **Many Files**: Search across 1000+ text files
4. **Special Characters**: Search for Unicode/special characters
5. **Expected Result**: Reasonable performance, proper file type handling

### Filter Combinations
1. **All Filters Active**: Enable all three filter types
2. **Conflicting Criteria**: Set impossible combinations
3. **Very Restrictive**: Use filters that match very few files
4. **Progressive Refinement**: Add filters one by one
5. **Expected Result**: Logical AND combination of all filters

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

### Pattern Matching
```python
def _check_filename_pattern(self, filename):
    if not self.filename_pattern:
        return True
    return bool(self.filename_pattern.search(filename))
```

### Content Search
```python
def _check_content_search(self, file_path, extension):
    if extension not in self.text_extensions:
        return True  # Skip non-text files
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read(1024 * 1024).lower()  # Read first 1MB
        return search_term in content
```

### Filter Integration
- Filters applied during scan for efficiency
- Early termination when filters don't match
- Graceful error handling for inaccessible files
- Memory-efficient content reading

## User Interface Features
- **Collapsible Section**: Advanced filters in expandable group box
- **Toggle Controls**: Individual enable/disable for each filter
- **Clear Filters**: One-click reset of all advanced filters
- **Visual Feedback**: Disabled controls when filters not active
- **Helpful Placeholders**: Example patterns and descriptions

## Performance Considerations
- **Date Filtering**: Very fast (metadata only)
- **Pattern Matching**: Fast (filename string operations)
- **Content Search**: Slower (file I/O required)
- **Optimization**: Content search limited to 1MB per file
- **Scaling**: Filters applied during scan to reduce memory usage

## Configuration Options
- Text file extensions list (customizable)
- Content search read limit (default 1MB)
- Regex flags (case sensitivity, multiline)
- Default date ranges

## Known Limitations
- Content search limited to text files only
- Large binary files may slow down content search
- Complex regex patterns may impact performance
- Content search reads file portions only (first 1MB)
- Network files dependent on connection speed

## Error Handling
- **Invalid Regex**: Silently ignore malformed patterns
- **File Access**: Skip files that can't be read
- **Encoding Issues**: Use error-ignore mode for text reading
- **Permission Denied**: Continue scan with other files

## Security Considerations
- Content search respects file permissions
- No sensitive file access outside user permissions
- Safe regex handling prevents ReDoS attacks
- Limited file reading prevents memory exhaustion

## Future Enhancements
- **File Metadata Search**: Search in EXIF, ID3 tags, document properties
- **Advanced Date Options**: Creation date, access date, date arithmetic
- **Content Preview**: Show matching content snippets in results
- **Saved Filter Sets**: Store and recall common filter combinations
- **File Size Patterns**: More granular size filtering options
- **Exclusion Filters**: Negative matching capabilities

## Related Features
- File Scanning (applies filters during scan)
- Results Display (shows filtered results)
- Settings Management (could store default filters)
- Export System (exports filtered results)

## Testing Checklist
- [ ] Date range filtering accuracy
- [ ] Regex pattern validation and matching
- [ ] Content search in various text formats
- [ ] Filter combination logic
- [ ] Performance with large datasets
- [ ] Error handling for edge cases
- [ ] UI responsiveness with filters active
- [ ] Clear filters functionality
- [ ] Cross-platform compatibility
- [ ] Memory usage during content search
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
