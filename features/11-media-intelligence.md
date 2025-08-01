# Media Intelligence

## Overview
Automatically extracts and displays video and audio metadata (codec, resolution, bitrate, duration, frame rate, channels, sample rate) for supported media files using FFmpeg's ffprobe utility.

## Need/Purpose
- Help users understand media file properties
- Identify low-quality or duplicate media files
- Provide quick preview of media details

## Features Implemented
- ✅ Video metadata extraction (codec, resolution, duration, bitrate)
- ✅ Audio metadata extraction (codec, channels, sample rate, duration)
- ✅ Media preview in file preview panel
- ✅ Integration with ffprobe (requires ffmpeg installed)

## How to Test

1. **Ensure ffprobe is installed**  
   - On Linux: `sudo apt install ffmpeg`
   - On macOS: `brew install ffmpeg`
   - On Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH.

2. **Open Smart File Manager and perform a file search**  
   - Search in a directory containing video and audio files (e.g., MP4, MKV, MP3, FLAC).

3. **Select a video or audio file in the results table**  
   - Click on a media file row.

4. **View the preview panel**  
   - The panel should display extracted metadata:
     - **Video**: codec, resolution, duration, bitrate, frame rate, audio codec
     - **Audio**: codec, channels, sample rate, duration, bitrate

5. **Try different formats**  
   - Test with MP4, MKV, AVI, MOV, FLV, MP3, WAV, FLAC, AAC, etc.

6. **Check for error handling**  
   - If ffprobe is not installed or the file is not a supported media type, the panel should show "No metadata available (ffprobe required)".

7. **Edge Cases**  
   - Try with corrupted or unsupported media files.
   - Try with non-media files (should show standard preview).

### Video Metadata
1. Select a video file in the results table
2. View metadata in the preview panel

### Audio Metadata
1. Select an audio file in the results table
2. View metadata in the preview panel

## Troubleshooting

- If metadata is missing, verify ffprobe is installed and accessible from the command line.
- If you see "No metadata available", check your system PATH and ffprobe installation.

## Technical Implementation
- Uses `ffprobe` via subprocess for cross-platform metadata extraction.
- Parses JSON output for relevant fields.
- Displays info in preview panel for video and audio files.

## Requirements
- **FFmpeg/ffprobe** must be installed and available in system PATH.

## Known Limitations
- No thumbnail preview for videos yet.
- Only metadata extraction, not playback.
- Requires ffprobe to be installed.

## Future Enhancements
- Add video thumbnail extraction.
- Integrate waveform or spectrum preview for audio.
- Integrate with duplicate detection for media files.
- Support for more media formats and metadata fields.

## Related Features

- File Preview Panel (displays media metadata)
- Duplicate Detection (can use media metadata for comparison)
