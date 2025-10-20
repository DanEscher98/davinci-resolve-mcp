"""
DaVinci Resolve MCP - Advanced MediaPoolItem Tools

Implements advanced MediaPoolItem API operations including:
- Proxy media management
- Clip replacement
- In/Out mark management
- Audio transcription
- Audio channel mapping

HIGH PRIORITY: Essential for professional media management workflows
"""

from typing import Dict, Any, List, Optional, Tuple
import json
import logging

logger = logging.getLogger("davinci-resolve-mcp.tools.mediapoolitem_advanced")

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


def get_media_pool():
    """Helper to get MediaPool from current project."""
    project = get_current_project()
    if not project:
        raise ValueError("No project is currently open")

    media_pool = project.GetMediaPool()
    if not media_pool:
        raise ValueError("Could not access Media Pool")

    return media_pool


def get_media_pool_item_by_name(clip_name: str):
    """Helper to get MediaPoolItem by name."""
    media_pool = get_media_pool()
    root_folder = media_pool.GetRootFolder()

    # Search for clip in root folder
    clips = root_folder.GetClipList()
    if clips:
        for clip in clips:
            if clip.GetName() == clip_name:
                return clip

    raise ValueError(f"Clip '{clip_name}' not found in Media Pool")


# ============================================================================
# Proxy Media Management (HIGH PRIORITY)
# ============================================================================

def link_proxy_media(
    clip_name: str,
    proxy_media_file_path: str
) -> Dict[str, Any]:
    """
    Link proxy media to a Media Pool clip.

    Proxy media allows you to work with lower-resolution versions of clips
    for better performance, while maintaining the connection to full-resolution
    originals for final output.

    Args:
        clip_name: Name of the clip in Media Pool
        proxy_media_file_path: Path to the proxy media file

    Returns:
        Link result with success status

    Example:
        >>> link_proxy_media(
        ...     clip_name="A001_C002_0712AB.mov",
        ...     proxy_media_file_path="/proxies/A001_C002_0712AB_proxy.mp4"
        ... )
        {
            "success": True,
            "clip_name": "A001_C002_0712AB.mov",
            "proxy_path": "/proxies/A001_C002_0712AB_proxy.mp4",
            "message": "Proxy media linked"
        }
    """
    try:
        clip = get_media_pool_item_by_name(clip_name)

        # LinkProxyMedia(proxyMediaFilePath)
        result = clip.LinkProxyMedia(proxy_media_file_path)

        return {
            "success": bool(result),
            "clip_name": clip_name,
            "proxy_path": proxy_media_file_path,
            "message": f"Proxy media {'linked' if result else 'link failed'}"
        }

    except Exception as e:
        logger.error(f"Error linking proxy media: {e}")
        return {
            "success": False,
            "error": str(e),
            "clip_name": clip_name
        }


def unlink_proxy_media(clip_name: str) -> Dict[str, Any]:
    """
    Unlink proxy media from a Media Pool clip.

    This removes the proxy association and reverts to using the original media.

    Args:
        clip_name: Name of the clip in Media Pool

    Returns:
        Unlink result with success status

    Example:
        >>> unlink_proxy_media("A001_C002_0712AB.mov")
        {
            "success": True,
            "clip_name": "A001_C002_0712AB.mov",
            "message": "Proxy media unlinked"
        }
    """
    try:
        clip = get_media_pool_item_by_name(clip_name)

        # UnlinkProxyMedia()
        result = clip.UnlinkProxyMedia()

        return {
            "success": bool(result),
            "clip_name": clip_name,
            "message": f"Proxy media {'unlinked' if result else 'unlink failed'}"
        }

    except Exception as e:
        logger.error(f"Error unlinking proxy media: {e}")
        return {
            "success": False,
            "error": str(e),
            "clip_name": clip_name
        }


# ============================================================================
# Clip Replacement (HIGH PRIORITY)
# ============================================================================

def replace_clip(
    clip_name: str,
    new_file_path: str
) -> Dict[str, Any]:
    """
    Replace the source file of a Media Pool clip.

    This maintains all metadata, in/out points, and timeline usage while
    swapping the underlying media file.

    Args:
        clip_name: Name of the clip in Media Pool
        new_file_path: Path to the new media file

    Returns:
        Replacement result with success status

    Example:
        >>> replace_clip(
        ...     clip_name="Interview_Take1.mov",
        ...     new_file_path="/media/Interview_Take1_v2.mov"
        ... )
        {
            "success": True,
            "clip_name": "Interview_Take1.mov",
            "new_file_path": "/media/Interview_Take1_v2.mov",
            "message": "Clip replaced - maintaining all metadata and timeline usage"
        }
    """
    try:
        clip = get_media_pool_item_by_name(clip_name)

        # ReplaceClip(filePath)
        result = clip.ReplaceClip(new_file_path)

        return {
            "success": bool(result),
            "clip_name": clip_name,
            "old_file_path": clip.GetClipProperty("File Path"),
            "new_file_path": new_file_path,
            "message": f"Clip {'replaced' if result else 'replacement failed'}"
        }

    except Exception as e:
        logger.error(f"Error replacing clip: {e}")
        return {
            "success": False,
            "error": str(e),
            "clip_name": clip_name
        }


# ============================================================================
# In/Out Mark Management (HIGH PRIORITY)
# ============================================================================

def get_mark_in_out(clip_name: str) -> Dict[str, Any]:
    """
    Get the In and Out marks for a Media Pool clip.

    In/Out marks define the usable portion of a clip in the Media Pool,
    before it's added to the timeline.

    Args:
        clip_name: Name of the clip in Media Pool

    Returns:
        Dictionary with mark in and mark out frame numbers

    Example:
        >>> get_mark_in_out("Interview_Take1.mov")
        {
            "success": True,
            "clip_name": "Interview_Take1.mov",
            "mark_in": 100,
            "mark_out": 500,
            "duration": 400
        }
    """
    try:
        clip = get_media_pool_item_by_name(clip_name)

        # GetMarkInOut() returns tuple (markIn, markOut)
        result = clip.GetMarkInOut()

        if result and len(result) >= 2:
            mark_in, mark_out = result[0], result[1]
            return {
                "success": True,
                "clip_name": clip_name,
                "mark_in": mark_in,
                "mark_out": mark_out,
                "duration": mark_out - mark_in if mark_out and mark_in else None
            }
        else:
            return {
                "success": False,
                "clip_name": clip_name,
                "error": "No marks set or unable to retrieve marks"
            }

    except Exception as e:
        logger.error(f"Error getting mark in/out: {e}")
        return {
            "success": False,
            "error": str(e),
            "clip_name": clip_name
        }


def set_mark_in_out(
    clip_name: str,
    mark_in: int,
    mark_out: int,
    mark_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Set the In and Out marks for a Media Pool clip.

    Args:
        clip_name: Name of the clip in Media Pool
        mark_in: Frame number for Mark In
        mark_out: Frame number for Mark Out
        mark_type: Optional mark type (if supported by API)

    Returns:
        Set result with success status

    Example:
        >>> set_mark_in_out(
        ...     clip_name="Interview_Take1.mov",
        ...     mark_in=100,
        ...     mark_out=500
        ... )
        {
            "success": True,
            "clip_name": "Interview_Take1.mov",
            "mark_in": 100,
            "mark_out": 500,
            "duration": 400
        }
    """
    try:
        clip = get_media_pool_item_by_name(clip_name)

        # SetMarkInOut(in, out, type)
        if mark_type:
            result = clip.SetMarkInOut(mark_in, mark_out, mark_type)
        else:
            result = clip.SetMarkInOut(mark_in, mark_out)

        return {
            "success": bool(result),
            "clip_name": clip_name,
            "mark_in": mark_in,
            "mark_out": mark_out,
            "duration": mark_out - mark_in,
            "message": f"Marks {'set' if result else 'set failed'}"
        }

    except Exception as e:
        logger.error(f"Error setting mark in/out: {e}")
        return {
            "success": False,
            "error": str(e),
            "clip_name": clip_name
        }


def clear_mark_in_out(
    clip_name: str,
    mark_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Clear the In and Out marks for a Media Pool clip.

    Args:
        clip_name: Name of the clip in Media Pool
        mark_type: Optional mark type (if supported by API)

    Returns:
        Clear result with success status

    Example:
        >>> clear_mark_in_out("Interview_Take1.mov")
        {
            "success": True,
            "clip_name": "Interview_Take1.mov",
            "message": "Marks cleared"
        }
    """
    try:
        clip = get_media_pool_item_by_name(clip_name)

        # ClearMarkInOut(type)
        if mark_type:
            result = clip.ClearMarkInOut(mark_type)
        else:
            result = clip.ClearMarkInOut()

        return {
            "success": bool(result),
            "clip_name": clip_name,
            "message": f"Marks {'cleared' if result else 'clear failed'}"
        }

    except Exception as e:
        logger.error(f"Error clearing mark in/out: {e}")
        return {
            "success": False,
            "error": str(e),
            "clip_name": clip_name
        }


# ============================================================================
# Audio Transcription (MEDIUM PRIORITY)
# ============================================================================

def transcribe_audio(clip_name: str) -> Dict[str, Any]:
    """
    Transcribe the audio of a Media Pool clip.

    Uses AI/ML to generate text transcription of spoken audio in the clip.
    This can be used for subtitles, searchability, and accessibility.

    Args:
        clip_name: Name of the clip in Media Pool

    Returns:
        Transcription initiation result

    Example:
        >>> transcribe_audio("Interview_Take1.mov")
        {
            "success": True,
            "clip_name": "Interview_Take1.mov",
            "message": "Audio transcription started"
        }
    """
    try:
        clip = get_media_pool_item_by_name(clip_name)

        # TranscribeAudio()
        result = clip.TranscribeAudio()

        return {
            "success": bool(result),
            "clip_name": clip_name,
            "message": f"Audio transcription {'started' if result else 'failed'}"
        }

    except Exception as e:
        logger.error(f"Error transcribing audio: {e}")
        return {
            "success": False,
            "error": str(e),
            "clip_name": clip_name
        }


# ============================================================================
# Audio Mapping (MEDIUM PRIORITY)
# ============================================================================

def get_audio_mapping(clip_name: str) -> Dict[str, Any]:
    """
    Get the audio channel mapping for a Media Pool clip.

    Returns information about how audio channels from the source file
    are mapped to timeline tracks.

    Args:
        clip_name: Name of the clip in Media Pool

    Returns:
        Audio mapping information

    Example:
        >>> get_audio_mapping("Interview_Take1.mov")
        {
            "success": True,
            "clip_name": "Interview_Take1.mov",
            "audio_mapping": {...}
        }
    """
    try:
        clip = get_media_pool_item_by_name(clip_name)

        # GetAudioMapping()
        mapping = clip.GetAudioMapping()

        return {
            "success": True,
            "clip_name": clip_name,
            "audio_mapping": mapping
        }

    except Exception as e:
        logger.error(f"Error getting audio mapping: {e}")
        return {
            "success": False,
            "error": str(e),
            "clip_name": clip_name
        }


# ============================================================================
# Tool Registration
# ============================================================================

def register_tools(mcp):
    """
    Register advanced MediaPoolItem tools with the MCP server.

    Args:
        mcp: FastMCP server instance

    Returns:
        Number of tools registered
    """
    from ..proxy import get_proxy

    proxy = get_proxy()

    # Register HIGH priority proxy management tools
    proxy.register_tool(
        "link_proxy_media",
        link_proxy_media,
        "media",
        "Link proxy media to a Media Pool clip for better performance",
        {
            "clip_name": {"type": "string", "description": "Name of the clip in Media Pool"},
            "proxy_media_file_path": {"type": "string", "description": "Path to the proxy media file"}
        }
    )

    proxy.register_tool(
        "unlink_proxy_media",
        unlink_proxy_media,
        "media",
        "Unlink proxy media and revert to original media",
        {"clip_name": {"type": "string", "description": "Name of the clip in Media Pool"}}
    )

    # Register HIGH priority clip replacement tool
    proxy.register_tool(
        "replace_clip",
        replace_clip,
        "media",
        "Replace the source file of a clip while maintaining metadata and timeline usage",
        {
            "clip_name": {"type": "string", "description": "Name of the clip in Media Pool"},
            "new_file_path": {"type": "string", "description": "Path to the new media file"}
        }
    )

    # Register HIGH priority mark management tools
    proxy.register_tool(
        "get_mark_in_out",
        get_mark_in_out,
        "media",
        "Get the In and Out marks for a Media Pool clip",
        {"clip_name": {"type": "string", "description": "Name of the clip in Media Pool"}}
    )

    proxy.register_tool(
        "set_mark_in_out",
        set_mark_in_out,
        "media",
        "Set the In and Out marks for a Media Pool clip",
        {
            "clip_name": {"type": "string", "description": "Name of the clip in Media Pool"},
            "mark_in": {"type": "integer", "description": "Frame number for Mark In"},
            "mark_out": {"type": "integer", "description": "Frame number for Mark Out"},
            "mark_type": {"type": "string", "description": "Optional mark type", "optional": True}
        }
    )

    proxy.register_tool(
        "clear_mark_in_out",
        clear_mark_in_out,
        "media",
        "Clear the In and Out marks for a Media Pool clip",
        {
            "clip_name": {"type": "string", "description": "Name of the clip in Media Pool"},
            "mark_type": {"type": "string", "description": "Optional mark type", "optional": True}
        }
    )

    # Register MEDIUM priority transcription tool
    proxy.register_tool(
        "transcribe_audio",
        transcribe_audio,
        "media",
        "Transcribe the audio of a clip using AI/ML",
        {"clip_name": {"type": "string", "description": "Name of the clip in Media Pool"}}
    )

    # Register MEDIUM priority audio mapping tool
    proxy.register_tool(
        "get_audio_mapping",
        get_audio_mapping,
        "media",
        "Get the audio channel mapping for a clip",
        {"clip_name": {"type": "string", "description": "Name of the clip in Media Pool"}}
    )

    logger.info("Registered 8 advanced MediaPoolItem tools")
    return 8


# For standalone testing
if __name__ == "__main__":
    print("Advanced MediaPoolItem Tools - Testing")
    print("=" * 60)

    try:
        media_pool = get_media_pool()
        root = media_pool.GetRootFolder()
        clips = root.GetClipList()
        print(f"\nFound {len(clips) if clips else 0} clips in Media Pool")
    except Exception as e:
        print(f"Error: {e}")
