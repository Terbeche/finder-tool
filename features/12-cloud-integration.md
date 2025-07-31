# Cloud Integration

## Overview
Compares local files with cloud storage (simulated as a local folder), identifies files only present locally or in the cloud, and suggests files for migration based on configurable size thresholds.

## Need/Purpose
- Help users identify files that are not yet backed up to the cloud.
- Suggest large files for migration to optimize local storage.
- Provide an automated, bulk comparison instead of manual file selection.

## Features Implemented
- ✅ Compare local vs cloud files by name and size.
- ✅ Identify files only present locally or in the cloud.
- ✅ Suggest files for migration based on configurable minimum/maximum size and threshold.
- ✅ Preview panel integration with configuration dialog for migration suggestions.

## How to Test

1. Prepare two directories: one as "local", one as "cloud" (simulate cloud with a local folder).
2. Add files to both directories, with some overlap and some unique files.
3. In the preview panel, click the "Cloud Migration Suggestions" button.
4. Select the local and cloud directories when prompted.
5. Set minimum size, maximum size, and migration threshold in the configuration dialog.
6. Review the migration candidates (files only present locally and matching the size criteria).

## Configuration

- **Minimum File Size**: Only files larger than this value are considered (in MB).
- **Maximum File Size**: Only files smaller than this value are considered (in MB, or "No Limit").
- **Migration Threshold**: Only files larger than this value are suggested for migration (in MB).

These options are set in the configuration dialog that appears before running the migration suggestion.

## Technical Implementation

- Uses file name and size for comparison.
- Migration suggestion based on user-configurable thresholds.
- Real cloud integration can be added via SDKs in the future.
- All logic is implemented in `cloud_integration.py` and integrated into the preview panel.

## Known Limitations

- No real cloud API integration yet (simulation only).
- Only compares by name and size.
- No file upload or sync functionality.
- Does not show files for manual selection before running the suggestion.

## Future Enhancements

- Integrate with actual cloud APIs (Google Drive, Dropbox, etc.).
- Support file upload and sync.
- Add more advanced comparison (hash, metadata).
- Allow manual file selection for migration.
- Show file previews before migration.

## Related Features

- File Preview Panel (integration point for migration suggestions).
- Export & Archive (for moving files off local storage).
- Usage Analytics (future: track migration statistics).

## Troubleshooting

- If no files are suggested, ensure your test folders contain files that are only present locally and match the size criteria.
- Adjust the minimum, maximum, and threshold values in the configuration dialog to broaden or narrow the suggestion list.
