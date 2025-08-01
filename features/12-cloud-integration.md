# Cloud Integration

## Overview
Compares local files with cloud storage, suggests files for migration, and identifies redundancy across storage locations.

## Need/Purpose
- Help users migrate large or rarely used files to cloud storage
- Identify files present locally but missing in cloud
- Optimize storage usage across devices

## Features Implemented
- ✅ Local vs cloud file comparison
- ✅ Migration suggestions based on size/usage
- ✅ Cloud migration dialog with configuration options
- ✅ Redundancy detection

## How to Test

### Migration Suggestions
1. Open Cloud Migration dialog from preview panel
2. Select local and cloud directories
3. Set migration thresholds and options
4. View suggested files for migration

### Redundancy Detection
1. Compare files in local and cloud directories
2. Check for files present in both locations

## Configuration

- **Minimum File Size**: Only files larger than this value are considered (in MB).
- **Maximum File Size**: Only files smaller than this value are considered (in MB, or "No Limit").
- **Migration Threshold**: Only files larger than this value are suggested for migration (in MB).

These options are set in the configuration dialog that appears before running the migration suggestion.

## Technical Implementation

- Simulated cloud file listing and comparison
- Migration suggestions based on file size and thresholds
- Dialog for configuring migration parameters

## Known Limitations

- Cloud integration is simulated (no real cloud API calls)
- Migration suggestions based on file size only

## Future Enhancements

- Integrate with real cloud storage APIs (Google Drive, Dropbox, etc.)
- Support for cloud file upload/download
- More advanced redundancy detection

## Related Features

- Usage Analytics (can suggest files for migration)
- Performance Optimization (can optimize migration process)

## Troubleshooting

- If no files are suggested, ensure your test folders contain files that are only present locally and match the size criteria.
- Adjust the minimum, maximum, and threshold values in the configuration dialog to broaden or narrow the suggestion list.
