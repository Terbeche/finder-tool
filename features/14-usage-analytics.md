# Usage Analytics

## Overview
Tracks file usage patterns and provides insights into file access frequency, storage cost, and optimization suggestions.

## Need/Purpose
- Help users understand their file usage patterns.
- Identify infrequently accessed files for potential archiving or deletion.
- Provide insights into storage costs and optimization opportunities.

## Features Implemented
- ✅ File access frequency tracking.
- ✅ Storage cost calculator based on file size and access frequency.
- ✅ Insights into infrequently accessed files for cleanup suggestions.

## How to Test

1. Perform file searches and access files (open, preview, etc.).
2. Open the "Usage Analytics" section in the application.
3. Review:
   - Frequently accessed files.
   - Infrequently accessed files (suggested for cleanup).
   - Storage cost breakdown by file type and category.

## Technical Implementation

- Tracks file access events (open, preview) and stores frequency data.
- Calculates storage cost based on file size and access frequency.
- Provides insights into files that are rarely accessed or consume significant storage.

## Known Limitations

- Does not track file access outside the application.
- Storage cost calculation is based on static assumptions (e.g., cost per GB).

## Future Enhancements

- Integrate with cloud APIs to track access across devices.
- Allow users to customize storage cost assumptions.
- Provide more detailed insights (e.g., access patterns over time).

## Related Features

- File Scanning & Search (provides data for analytics).
- Cloud Integration (suggests files for migration based on usage).
- Security Features (flags suspicious files for review).

## Troubleshooting

- If no data is shown, ensure files have been accessed through the application.
- Verify that the analytics database is not corrupted or missing.
