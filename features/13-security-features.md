# Security Features

## Overview
Adds file integrity checking and suspicious file detection to help users identify potentially dangerous or corrupted files.

## Need/Purpose
- Detect corrupted or incomplete files before opening or moving them.
- Warn users about files with suspicious extensions, sizes, or locations.
- Improve user safety and data reliability.

## Features Implemented
- ✅ File integrity check (basic hash calculation and file access test)
- ✅ Suspicious file detection (unusual extensions, locations, or sizes)
- ✅ Preview panel integration: warning for suspicious or unreadable files

## How to Test

1. Search for files as usual.
2. Select files in the results table.
3. In the preview panel, observe:
   - If a file is unreadable or hash check fails, a warning is shown.
   - If a file has a suspicious extension or is in a suspicious location, a warning is shown.
4. Try with known corrupted files, files with double extensions (e.g., `.jpg.exe`), or files in system folders.

## Technical Implementation

- Uses SHA-256 hash for integrity check (readable files only).
- Flags files with:
  - Double extensions (e.g., `.jpg.exe`)
  - Executable extensions in non-standard locations
  - Files in system or temp directories
  - Files with zero size or extremely large size
- Preview panel displays warnings and disables "Open" for flagged files.

## Known Limitations

- Does not perform deep malware scanning.
- Integrity check is limited to file readability and hash calculation.
- No automatic repair or quarantine.

## Future Enhancements

- Integrate with antivirus APIs for deeper scanning.
- Add file quarantine and repair suggestions.
- Allow user to configure suspicious patterns and locations.
