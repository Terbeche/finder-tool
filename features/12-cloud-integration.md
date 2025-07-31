# Cloud Integration

## Overview
Compares local files with cloud storage (simulated for now), identifies files only present locally or in the cloud, and suggests large files for migration.

## Features Implemented
- ✅ Compare local vs cloud files by name and size
- ✅ Identify files only present locally or in cloud
- ✅ Suggest large files for migration to cloud
- ✅ Preview panel integration for migration suggestions

## How to Test

1. Prepare two directories: one as "local", one as "cloud" (simulate cloud with a local folder).
2. Add files to both directories, with some overlap and some unique files.
3. Use the preview panel's cloud migration method to compare and get suggestions.
4. Review the migration candidates (files >= 10MB only present locally).

## Technical Implementation
- Uses file name and size for comparison.
- Migration suggestion based on size threshold.
- Real cloud integration can be added via SDKs in future.

## Requirements
- No external dependencies for simulation.
- For real cloud integration, SDKs (Google Drive, Dropbox, etc.) would be required.

## Known Limitations
- No real cloud API integration yet.
- Only compares by name and size.
- No file upload or sync functionality.

## Future Enhancements
- Integrate with actual cloud APIs.
- Support file upload and sync.
- Add more advanced comparison (hash, metadata).
