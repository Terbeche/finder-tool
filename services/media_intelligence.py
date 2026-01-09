import subprocess
import json
from pathlib import Path

def get_video_metadata(file_path):
    """Extract video metadata using ffprobe (requires ffmpeg installed)"""
    try:
        cmd = [
            "ffprobe", "-v", "error", "-show_entries",
            "format:stream", "-of", "json", str(file_path)
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            return None
        info = json.loads(result.stdout)
        video_streams = [s for s in info.get("streams", []) if s.get("codec_type") == "video"]
        audio_streams = [s for s in info.get("streams", []) if s.get("codec_type") == "audio"]
        format_info = info.get("format", {})
        metadata = {
            "duration": float(format_info.get("duration", 0)),
            "size": int(format_info.get("size", 0)),
            "bit_rate": int(format_info.get("bit_rate", 0)),
            "video_codec": video_streams[0].get("codec_name") if video_streams else "N/A",
            "width": video_streams[0].get("width") if video_streams else "N/A",
            "height": video_streams[0].get("height") if video_streams else "N/A",
            "frame_rate": video_streams[0].get("r_frame_rate") if video_streams else "N/A",
            "audio_codec": audio_streams[0].get("codec_name") if audio_streams else "N/A",
        }
        return metadata
    except Exception:
        return None

def get_audio_metadata(file_path):
    """Extract audio metadata using ffprobe (requires ffmpeg installed)"""
    try:
        cmd = [
            "ffprobe", "-v", "error", "-show_entries",
            "format:stream", "-of", "json", str(file_path)
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            return None
        info = json.loads(result.stdout)
        audio_streams = [s for s in info.get("streams", []) if s.get("codec_type") == "audio"]
        format_info = info.get("format", {})
        if not audio_streams:
            return None
        stream = audio_streams[0]
        metadata = {
            "duration": float(format_info.get("duration", 0)),
            "size": int(format_info.get("size", 0)),
            "bit_rate": int(format_info.get("bit_rate", 0)),
            "audio_codec": stream.get("codec_name", "N/A"),
            "channels": stream.get("channels", "N/A"),
            "sample_rate": stream.get("sample_rate", "N/A"),
        }
        return metadata
    except Exception:
        return None
