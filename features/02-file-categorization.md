# File Categorization System

## Overview
Automatic classification of files into predefined categories (Video, Audio, Images, Documents, etc.) based on file extensions, with user-configurable category management.

## Need/Purpose
- Users need to quickly identify file types in large search results
- Visual organization helps with file management decisions
- Customizable categories accommodate different user workflows
- Color-coded display improves visual scanning of results

## Features Implemented
- ✅ Pre-defined categories with common file extensions
- ✅ Color-coded category display in results table
- ✅ User-configurable categories via Settings dialog
- ✅ Add/Edit/Remove custom categories
- ✅ Extension-to-category mapping
- ✅ Auto-discovery of unknown file extensions
- ✅ Category-based filtering during search
- ✅ Persistent category settings

## Default Categories
1. **Video** (Red #e74c3c): mp4, avi, mkv, mov, wmv, flv, webm, m4v, 3gp
2. **Audio** (Purple #9b59b6): mp3, wav, ogg, flac, aac, wma, m4a
3. **Images** (Green #2ecc71): jpg, jpeg, png, gif, bmp, tiff, webp, svg
4. **Documents** (Orange #f39c12): pdf, doc, docx, xls, xlsx, ppt, pptx, txt, csv, rtf
5. **Archives** (Gray #34495e): zip, rar, 7z, tar, gz, bz2
6. **Executables** (Orange #e67e22): exe, msi, app, dmg, deb, rpm

## How to Test

### Basic Categorization
1. Scan a directory with mixed file types
2. Check the "Category" column in results
3. **Expected Result**: Files are automatically categorized with appropriate colors

### Category-Based Search
1. Select "Video" from the File Type dropdown
2. Start a scan
3. **Expected Result**: Only video files are found and displayed

### Add Custom Category
1. Go to Edit → Settings → File Categories tab
2. Click "Add Category"
3. Enter name: "Development", extensions: "py,js,html,css", color: Blue
4. Click OK to save
5. Rescan a directory with code files
6. **Expected Result**: Code files are now categorized as "Development"

### Edit Existing Category
1. Open Settings → File Categories
2. Select an existing category and click "Edit Selected"
3. Add new extensions (e.g., add "webm" to Video category)
4. Save changes and rescan
5. **Expected Result**: Files with new extensions are now categorized correctly

### Remove Category
1. Open Settings → File Categories
2. Select a category and click "Remove Selected"
3. Confirm deletion
4. Rescan files
5. **Expected Result**: Files previously in that category show as "Uncategorized"

### Unknown Extension Discovery
1. Scan a directory with uncommon file types (e.g., .blend, .psd, .dwg)
2. Complete the scan
3. **Expected Result**: Dialog appears asking if you want to categorize new extensions

### Category Color Display
1. Scan mixed files and view results
2. Check that each category has a distinct color in the Category column
3. **Expected Result**: Colors match the category settings and improve visual distinction

### Settings Persistence
1. Add/modify categories
2. Restart the application
3. Check Settings → File Categories
4. **Expected Result**: Changes are preserved between sessions

## Technical Implementation
- **Storage**: Categories saved in JSON configuration file
- **Matching**: Case-insensitive extension matching
- **UI**: Color-coded table items with QColor
- **Management**: Full CRUD operations for categories
- **Discovery**: Post-scan analysis for unknown extensions

## Configuration Files
- Categories stored in: `~/.config/smartfilemanager/settings.json` (Linux)
- Auto-backup of settings before changes
- Graceful handling of corrupted config files

## Advanced Testing

### Edge Cases
1. **Empty Extensions**: Create category with no extensions
2. **Duplicate Extensions**: Try to add same extension to multiple categories
3. **Invalid Colors**: Test with malformed color codes
4. **Long Names**: Use very long category names
5. **Special Characters**: Test category names with Unicode/special chars

### Performance Testing
1. Create 50+ categories with 1000+ total extensions
2. Scan large directory
3. **Expected Result**: No significant performance impact

### Data Integrity
1. Manually edit config file with invalid JSON
2. Restart application
3. **Expected Result**: App loads with default categories, no crash

## Known Limitations
- Extension conflicts: One extension can only belong to one category
- No nested/hierarchical categories
- Color selection limited to predefined palette
- No regex-based pattern matching for extensions

## Related Features
- File Scanning (uses categories for filtering)
- Settings Management (stores category configuration)
- Results Display (shows category colors and names)
