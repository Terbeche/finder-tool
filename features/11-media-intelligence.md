# Media Intelligence

## Overview
Automatically extracts and displays video metadata (codec, resolution, bitrate, duration, frame rate, audio codec) for supported video files using FFmpeg's ffprobe utility.

## Features Implemented
- ✅ Video quality analysis (resolution, bitrate, duration)
- ✅ Codec identification (video/audio)
- ✅ Metadata extraction (frame rate, audio codec)
- ✅ Preview panel integration for instant display

## How to Test

1. **Ensure ffprobe is installed**  
   - On Linux: `sudo apt install ffmpeg`
   - On macOS: `brew install ffmpeg`
   - On Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH.

2. **Open Smart File Manager and perform a file search**  
   - Search in a directory containing video files (e.g., MP4, MKV, AVI, MOV).

3. **Select a video file in the results table**  
   - Click on a video file row.

4. **View the preview panel**  
   - The panel should display extracted metadata:
     - Video codec
     - Resolution (width x height)
     - Duration (seconds)
     - Bitrate (kbps)
     - Frame rate
     - Audio codec

5. **Try different video formats**  
   - Test with MP4, MKV, AVI, MOV, FLV, etc.

6. **Check for error handling**  
   - If ffprobe is not installed or the file is not a video, the panel should show "No metadata available (ffprobe required)".

7. **Edge Cases**  
   - Try with corrupted or unsupported video files.
   - Try with non-video files (should show standard preview).

## Troubleshooting

- If metadata is missing, verify ffprobe is installed and accessible from the command line.
- If you see "No metadata available", check your system PATH and ffprobe installation.

## Technical Implementation
- Uses `ffprobe` via subprocess for cross-platform metadata extraction.
- Parses JSON output for relevant fields.
- Displays info in preview panel for video files.

## Requirements
- **FFmpeg/ffprobe** must be installed and available in system PATH.

## Known Limitations
- No thumbnail preview for videos yet.
- Only metadata extraction, not playback.
- Requires ffprobe to be installed.

## Future Enhancements
- Add video thumbnail extraction.
- Support for audio files (bitrate, codec).
- Integrate with duplicate detection for media files.
