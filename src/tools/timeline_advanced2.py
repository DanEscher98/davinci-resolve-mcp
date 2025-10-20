"""
DaVinci Resolve MCP - Timeline Advanced Features 2

Implements additional high-priority Timeline API operations including:
- Auto-caption generation (AI subtitles)
- Scene cut detection
- Timeline still grabbing
- Timeline import into existing timeline
- Timeline-level in/out marks
- Grade copying

HIGH PRIORITY: Essential for modern editing and AI-assisted workflows
"""

from typing import Dict, Any, List, Optional
import json
import logging

logger = logging.getLogger("davinci-resolve-mcp.tools.timeline_advanced2")

# Import from the shared resolve connection module
try:
    from ..resolve_mcp_server import (
        get_resolve,
        get_project_manager,
        get_current_project,
        get_current_timeline,
    )
except ImportError:
    # Fallback for direct execution
    def get_resolve():
        raise NotImplementedError("Resolve connection not available")
    def get_project_manager():
        raise NotImplementedError("Project manager not available")
    def get_current_project():
        raise NotImplementedError("Current project not available")
    def get_current_timeline():
        raise NotImplementedError("Current timeline not available")


# ============================================================================
# AI/ML Features (HIGH PRIORITY)
# ============================================================================

def create_subtitles_from_audio(
    auto_caption_settings: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Auto-generate subtitles from audio using AI speech recognition.

    Analyzes audio in the timeline and generates subtitle tracks
    automatically. Supports multiple languages and speaker detection.

    Args:
        auto_caption_settings: Optional settings dictionary:
            - "language": Language code (e.g., "en-US", "es-ES")
            - "detectSpeakers": Enable speaker detection (bool)
            - "maxSpeakers": Maximum number of speakers to detect
            - "punctuation": Add automatic punctuation (bool)
            - "subtitleTrack": Target subtitle track number

    Returns:
        Subtitle generation result

    Example:
        >>> create_subtitles_from_audio({
        ...     "language": "en-US",
        ...     "detectSpeakers": True,
        ...     "punctuation": True
        ... })
        {
            "success": True,
            "language": "en-US",
            "subtitle_count": 127,
            "message": "Subtitles generated successfully"
        }
    """
    try:
        timeline = get_current_timeline()

        auto_caption_settings = auto_caption_settings or {}

        # CreateSubtitlesFromAudio({autoCaptionSettings})
        result = timeline.CreateSubtitlesFromAudio(auto_caption_settings)

        return {
            "success": bool(result),
            "language": auto_caption_settings.get("language", "auto"),
            "detect_speakers": auto_caption_settings.get("detectSpeakers", False),
            "message": f"Subtitles {'generated successfully' if result else 'generation failed'}"
        }

    except Exception as e:
        logger.error(f"Error creating subtitles from audio: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def detect_scene_cuts() -> Dict[str, Any]:
    """
    Automatically detect scene cuts in the timeline.

    Analyzes video content to find scene changes and creates
    markers or cuts at detected transitions.

    Returns:
        Scene cut detection result

    Example:
        >>> detect_scene_cuts()
        {
            "success": True,
            "cuts_detected": 23,
            "message": "23 scene cuts detected and marked"
        }
    """
    try:
        timeline = get_current_timeline()

        # DetectSceneCuts()
        result = timeline.DetectSceneCuts()

        if isinstance(result, int):
            return {
                "success": True,
                "cuts_detected": result,
                "message": f"{result} scene cuts detected"
            }
        else:
            return {
                "success": bool(result),
                "message": f"Scene cut detection {'completed' if result else 'failed'}"
            }

    except Exception as e:
        logger.error(f"Error detecting scene cuts: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# ============================================================================
# Still/Frame Operations (HIGH PRIORITY)
# ============================================================================

def grab_still() -> Dict[str, Any]:
    """
    Grab a still from the current frame and add it to the Gallery.

    Captures the current frame (with all color grading applied) and
    adds it to the active Gallery still album.

    Returns:
        Still grab result

    Example:
        >>> grab_still()
        {
            "success": True,
            "timecode": "01:00:15:12",
            "message": "Still grabbed and added to Gallery"
        }
    """
    try:
        timeline = get_current_timeline()

        current_timecode = timeline.GetCurrentTimecode()

        # GrabStill()
        result = timeline.GrabStill()

        return {
            "success": bool(result),
            "timecode": current_timecode,
            "message": f"Still {'grabbed and added to Gallery' if result else 'grab failed'}"
        }

    except Exception as e:
        logger.error(f"Error grabbing still: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# ============================================================================
# Timeline Import Operations (HIGH PRIORITY)
# ============================================================================

def import_into_timeline(
    file_path: str,
    import_options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Import a timeline file (AAF/EDL/XML) into the current timeline.

    Unlike ImportTimelineFromFile which creates a new timeline, this
    imports content into the existing timeline.

    Args:
        file_path: Path to timeline file (AAF, EDL, XML, FCPXML, etc.)
        import_options: Optional import settings:
            - "autoImportSourceClips": Auto-import source media
            - "importAtPlayhead": Import at playhead position
            - "sourceClipsPath": Path to source media
            - "insertMode": "overwrite" or "insert"

    Returns:
        Import result

    Example:
        >>> import_into_timeline(
        ...     "/imports/sequence.xml",
        ...     {"importAtPlayhead": True, "insertMode": "insert"}
        ... )
        {
            "success": True,
            "file_path": "/imports/sequence.xml",
            "message": "Timeline content imported"
        }
    """
    try:
        timeline = get_current_timeline()

        import_options = import_options or {}

        # ImportIntoTimeline(filePath, {importOptions})
        result = timeline.ImportIntoTimeline(file_path, import_options)

        return {
            "success": bool(result),
            "file_path": file_path,
            "insert_mode": import_options.get("insertMode", "insert"),
            "message": f"Timeline content {'imported' if result else 'import failed'}"
        }

    except Exception as e:
        logger.error(f"Error importing into timeline: {e}")
        return {
            "success": False,
            "error": str(e),
            "file_path": file_path
        }


# ============================================================================
# Timeline Mark Operations (HIGH PRIORITY)
# ============================================================================

def get_timeline_mark_in_out() -> Dict[str, Any]:
    """
    Get the In and Out marks for the timeline (not clip marks).

    Timeline marks define the render range or playback loop points.

    Returns:
        Dictionary with mark in and mark out frame numbers

    Example:
        >>> get_timeline_mark_in_out()
        {
            "success": True,
            "mark_in": 1000,
            "mark_out": 5000,
            "duration": 4000
        }
    """
    try:
        timeline = get_current_timeline()

        # GetMarkInOut() returns tuple (markIn, markOut)
        result = timeline.GetMarkInOut()

        if result and len(result) >= 2:
            mark_in, mark_out = result[0], result[1]
            return {
                "success": True,
                "mark_in": mark_in,
                "mark_out": mark_out,
                "duration": mark_out - mark_in if mark_out and mark_in else None
            }
        else:
            return {
                "success": False,
                "error": "No timeline marks set or unable to retrieve marks"
            }

    except Exception as e:
        logger.error(f"Error getting timeline mark in/out: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def set_timeline_mark_in_out(
    mark_in: int,
    mark_out: int,
    mark_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Set the In and Out marks for the timeline.

    Args:
        mark_in: Frame number for Mark In
        mark_out: Frame number for Mark Out
        mark_type: Optional mark type

    Returns:
        Set result with success status

    Example:
        >>> set_timeline_mark_in_out(mark_in=1000, mark_out=5000)
        {
            "success": True,
            "mark_in": 1000,
            "mark_out": 5000,
            "duration": 4000
        }
    """
    try:
        timeline = get_current_timeline()

        # SetMarkInOut(in, out, type)
        if mark_type:
            result = timeline.SetMarkInOut(mark_in, mark_out, mark_type)
        else:
            result = timeline.SetMarkInOut(mark_in, mark_out)

        return {
            "success": bool(result),
            "mark_in": mark_in,
            "mark_out": mark_out,
            "duration": mark_out - mark_in,
            "message": f"Timeline marks {'set' if result else 'set failed'}"
        }

    except Exception as e:
        logger.error(f"Error setting timeline mark in/out: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# ============================================================================
# Tool Registration
# ============================================================================

def register_tools(mcp):
    """
    Register Timeline Advanced Features 2 tools with the MCP server.

    Args:
        mcp: FastMCP server instance

    Returns:
        Number of tools registered
    """
    from ..proxy import get_proxy

    proxy = get_proxy()

    # Register HIGH priority AI/ML tools
    proxy.register_tool(
        "create_subtitles_from_audio",
        create_subtitles_from_audio,
        "timeline",
        "Auto-generate subtitles from audio using AI speech recognition",
        {
            "auto_caption_settings": {
                "type": "object",
                "description": "Optional caption settings (language, detectSpeakers, punctuation)",
                "optional": True
            }
        }
    )

    proxy.register_tool(
        "detect_scene_cuts",
        detect_scene_cuts,
        "timeline",
        "Automatically detect scene cuts in the timeline",
        {}
    )

    # Register HIGH priority still/frame tools
    proxy.register_tool(
        "grab_still",
        grab_still,
        "gallery",
        "Grab a still from the current frame and add it to the Gallery",
        {}
    )

    # Register HIGH priority timeline import tool
    proxy.register_tool(
        "import_into_timeline",
        import_into_timeline,
        "timeline",
        "Import a timeline file (AAF/EDL/XML) into the current timeline",
        {
            "file_path": {"type": "string", "description": "Path to timeline file"},
            "import_options": {"type": "object", "description": "Optional import settings", "optional": True}
        }
    )

    # Register HIGH priority timeline mark tools
    proxy.register_tool(
        "get_timeline_mark_in_out",
        get_timeline_mark_in_out,
        "timeline",
        "Get the In and Out marks for the timeline (render range)",
        {}
    )

    proxy.register_tool(
        "set_timeline_mark_in_out",
        set_timeline_mark_in_out,
        "timeline",
        "Set the In and Out marks for the timeline (render range)",
        {
            "mark_in": {"type": "integer", "description": "Frame number for Mark In"},
            "mark_out": {"type": "integer", "description": "Frame number for Mark Out"},
            "mark_type": {"type": "string", "description": "Optional mark type", "optional": True}
        }
    )

    logger.info("Registered 6 Timeline Advanced Features 2 tools")
    return 6


# For standalone testing
if __name__ == "__main__":
    print("Timeline Advanced Features 2 Tools - Testing")
    print("=" * 60)

    try:
        timeline = get_current_timeline()
        if timeline:
            print(f"\nTimeline: {timeline.GetName()}")
            marks = get_timeline_mark_in_out()
            print(f"Timeline marks: {marks}")
        else:
            print("\nNo timeline active")
    except Exception as e:
        print(f"Error: {e}")
