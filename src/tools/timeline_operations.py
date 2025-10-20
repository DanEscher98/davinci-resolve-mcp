"""
DaVinci Resolve MCP - Timeline Operations Tools

Implements timeline manipulation API operations including:
- Clip deletion with ripple
- Clip linking/unlinking
- Timecode management
- Playhead positioning

HIGH PRIORITY: Essential for timeline editing workflows
"""

from typing import Dict, Any, List, Optional
import json
import logging

logger = logging.getLogger("davinci-resolve-mcp.tools.timeline_operations")

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
# Clip Deletion Operations (HIGH PRIORITY)
# ============================================================================

def delete_clips(
    track_type: str,
    track_index: int,
    item_indices: List[int],
    ripple_delete: bool = True
) -> Dict[str, Any]:
    """
    Delete clips from timeline with optional ripple.

    Args:
        track_type: Track type ("video" or "audio")
        track_index: Track number (1-based)
        item_indices: List of item indices to delete (1-based)
        ripple_delete: If True, close gaps after deletion (default: True)

    Returns:
        Deletion result

    Example:
        >>> delete_clips(
        ...     track_type="video",
        ...     track_index=1,
        ...     item_indices=[3, 4, 5],
        ...     ripple_delete=True
        ... )
        {
            "success": True,
            "track_type": "video",
            "track_index": 1,
            "deleted_count": 3,
            "ripple_delete": True
        }
    """
    try:
        timeline = get_current_timeline()

        # Get items from track
        items_in_track = timeline.GetItemListInTrack(track_type, track_index)

        if not items_in_track:
            return {
                "success": False,
                "error": f"No items found in {track_type} track {track_index}"
            }

        # Get specific items by index
        items_to_delete = []
        for idx in item_indices:
            if 1 <= idx <= len(items_in_track):
                items_to_delete.append(items_in_track[idx - 1])  # Convert to 0-based

        if not items_to_delete:
            return {
                "success": False,
                "error": "No valid items at specified indices",
                "item_indices": item_indices
            }

        # DeleteClips([timelineItems], Bool)
        result = timeline.DeleteClips(items_to_delete, ripple_delete)

        return {
            "success": bool(result),
            "track_type": track_type,
            "track_index": track_index,
            "deleted_count": len(items_to_delete) if result else 0,
            "ripple_delete": ripple_delete,
            "message": f"Deleted {len(items_to_delete) if result else 0} clips{' with ripple' if ripple_delete else ''}"
        }

    except Exception as e:
        logger.error(f"Error deleting clips: {e}")
        return {
            "success": False,
            "error": str(e),
            "track_type": track_type,
            "track_index": track_index
        }


# ============================================================================
# Clip Linking Operations (HIGH PRIORITY)
# ============================================================================

def set_clips_linked(
    track_type: str,
    track_index: int,
    item_indices: List[int],
    linked: bool = True
) -> Dict[str, Any]:
    """
    Link or unlink clips in the timeline.

    Linked clips move together when repositioned. Typically used to
    keep video and audio in sync.

    Args:
        track_type: Track type ("video" or "audio")
        track_index: Track number (1-based)
        item_indices: List of item indices to link/unlink (1-based)
        linked: True to link, False to unlink (default: True)

    Returns:
        Link result

    Example:
        >>> set_clips_linked(
        ...     track_type="video",
        ...     track_index=1,
        ...     item_indices=[1, 2, 3],
        ...     linked=True
        ... )
        {
            "success": True,
            "track_type": "video",
            "track_index": 1,
            "affected_count": 3,
            "linked": True
        }
    """
    try:
        timeline = get_current_timeline()

        # Get items from track
        items_in_track = timeline.GetItemListInTrack(track_type, track_index)

        if not items_in_track:
            return {
                "success": False,
                "error": f"No items found in {track_type} track {track_index}"
            }

        # Get specific items by index
        items = []
        for idx in item_indices:
            if 1 <= idx <= len(items_in_track):
                items.append(items_in_track[idx - 1])  # Convert to 0-based

        if not items:
            return {
                "success": False,
                "error": "No valid items at specified indices",
                "item_indices": item_indices
            }

        # SetClipsLinked([timelineItems], Bool)
        result = timeline.SetClipsLinked(items, linked)

        return {
            "success": bool(result),
            "track_type": track_type,
            "track_index": track_index,
            "affected_count": len(items) if result else 0,
            "linked": linked,
            "message": f"Clips {'linked' if linked else 'unlinked'}"
        }

    except Exception as e:
        logger.error(f"Error setting clips linked: {e}")
        return {
            "success": False,
            "error": str(e),
            "track_type": track_type,
            "track_index": track_index
        }


# ============================================================================
# Timecode Operations (HIGH PRIORITY)
# ============================================================================

def set_start_timecode(timecode: str) -> Dict[str, Any]:
    """
    Set the start timecode for the timeline.

    The start timecode is the timecode value at the first frame
    of the timeline (e.g., "01:00:00:00").

    Args:
        timecode: Timecode string (format: "HH:MM:SS:FF")

    Returns:
        Set result

    Example:
        >>> set_start_timecode("01:00:00:00")
        {
            "success": True,
            "timecode": "01:00:00:00",
            "message": "Start timecode set to 01:00:00:00"
        }
    """
    try:
        timeline = get_current_timeline()

        # SetStartTimecode(timecode)
        result = timeline.SetStartTimecode(timecode)

        return {
            "success": bool(result),
            "timecode": timecode,
            "message": f"Start timecode {'set to' if result else 'set failed for'} {timecode}"
        }

    except Exception as e:
        logger.error(f"Error setting start timecode: {e}")
        return {
            "success": False,
            "error": str(e),
            "timecode": timecode
        }


def get_start_timecode() -> str:
    """
    Get the start timecode for the timeline.

    Returns:
        Timecode string (format: "HH:MM:SS:FF")

    Example:
        >>> get_start_timecode()
        "01:00:00:00"
    """
    try:
        timeline = get_current_timeline()

        # GetStartTimecode()
        timecode = timeline.GetStartTimecode()

        return timecode

    except Exception as e:
        logger.error(f"Error getting start timecode: {e}")
        return "00:00:00:00"


def set_current_timecode(timecode: str) -> Dict[str, Any]:
    """
    Set the playhead position by timecode.

    Moves the playhead to the specified timecode position.

    Args:
        timecode: Timecode string (format: "HH:MM:SS:FF")

    Returns:
        Set result

    Example:
        >>> set_current_timecode("01:00:15:12")
        {
            "success": True,
            "timecode": "01:00:15:12",
            "message": "Playhead moved to 01:00:15:12"
        }
    """
    try:
        timeline = get_current_timeline()

        # SetCurrentTimecode(timecode)
        result = timeline.SetCurrentTimecode(timecode)

        return {
            "success": bool(result),
            "timecode": timecode,
            "message": f"Playhead {'moved to' if result else 'move failed for'} {timecode}"
        }

    except Exception as e:
        logger.error(f"Error setting current timecode: {e}")
        return {
            "success": False,
            "error": str(e),
            "timecode": timecode
        }


def get_current_timecode() -> str:
    """
    Get the current playhead position as timecode.

    Returns:
        Timecode string (format: "HH:MM:SS:FF")

    Example:
        >>> get_current_timecode()
        "01:00:15:12"
    """
    try:
        timeline = get_current_timeline()

        # GetCurrentTimecode()
        timecode = timeline.GetCurrentTimecode()

        return timecode

    except Exception as e:
        logger.error(f"Error getting current timecode: {e}")
        return "00:00:00:00"


def get_current_video_item() -> Dict[str, Any]:
    """
    Get the current video item at the playhead position.

    Returns:
        Current video item information

    Example:
        >>> get_current_video_item()
        {
            "name": "A001_C002.mov",
            "start_frame": 1000,
            "end_frame": 1500,
            "duration": 500
        }
    """
    try:
        timeline = get_current_timeline()

        # GetCurrentVideoItem()
        item = timeline.GetCurrentVideoItem()

        if not item:
            return {
                "exists": False,
                "message": "No video item at current position"
            }

        return {
            "exists": True,
            "name": item.GetName(),
            "start_frame": item.GetStart(),
            "end_frame": item.GetEnd(),
            "duration": item.GetDuration()
        }

    except Exception as e:
        logger.error(f"Error getting current video item: {e}")
        return {
            "exists": False,
            "error": str(e)
        }


def get_current_clip_thumbnail_image() -> Dict[str, Any]:
    """
    Get the current clip thumbnail.

    Returns:
        Thumbnail information

    Example:
        >>> get_current_clip_thumbnail_image()
        {
            "success": True,
            "format": "PNG",
            "data": "base64_encoded_image..."
        }
    """
    try:
        timeline = get_current_timeline()

        # GetCurrentClipThumbnailImage()
        # Returns thumbnail data - exact format depends on API implementation
        thumbnail = timeline.GetCurrentClipThumbnailImage()

        if thumbnail:
            return {
                "success": True,
                "has_thumbnail": True,
                "thumbnail": thumbnail
            }
        else:
            return {
                "success": False,
                "has_thumbnail": False,
                "message": "No thumbnail available"
            }

    except Exception as e:
        logger.error(f"Error getting current clip thumbnail: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# ============================================================================
# Tool Registration
# ============================================================================

def register_tools(mcp):
    """
    Register Timeline Operations tools with the MCP server.

    Args:
        mcp: FastMCP server instance

    Returns:
        Number of tools registered
    """
    from ..proxy import get_proxy

    proxy = get_proxy()

    # Register HIGH priority clip deletion tool
    proxy.register_tool(
        "delete_clips",
        delete_clips,
        "timeline",
        "Delete clips from timeline with optional ripple",
        {
            "track_type": {"type": "string", "description": "Track type (video or audio)"},
            "track_index": {"type": "integer", "description": "Track number (1-based)"},
            "item_indices": {"type": "array", "description": "List of item indices to delete (1-based)"},
            "ripple_delete": {"type": "boolean", "description": "Close gaps after deletion", "default": True}
        }
    )

    # Register HIGH priority clip linking tool
    proxy.register_tool(
        "set_clips_linked",
        set_clips_linked,
        "timeline",
        "Link or unlink clips in the timeline",
        {
            "track_type": {"type": "string", "description": "Track type (video or audio)"},
            "track_index": {"type": "integer", "description": "Track number (1-based)"},
            "item_indices": {"type": "array", "description": "List of item indices (1-based)"},
            "linked": {"type": "boolean", "description": "True to link, False to unlink", "default": True}
        }
    )

    # Register HIGH priority timecode tools
    proxy.register_tool(
        "set_start_timecode",
        set_start_timecode,
        "timeline",
        "Set the start timecode for the timeline",
        {"timecode": {"type": "string", "description": "Timecode string (HH:MM:SS:FF)"}}
    )

    proxy.register_tool(
        "get_start_timecode",
        get_start_timecode,
        "timeline",
        "Get the start timecode for the timeline",
        {}
    )

    proxy.register_tool(
        "set_current_timecode",
        set_current_timecode,
        "timeline",
        "Set the playhead position by timecode",
        {"timecode": {"type": "string", "description": "Timecode string (HH:MM:SS:FF)"}}
    )

    proxy.register_tool(
        "get_current_timecode",
        get_current_timecode,
        "timeline",
        "Get the current playhead position as timecode",
        {}
    )

    proxy.register_tool(
        "get_current_video_item",
        get_current_video_item,
        "timeline",
        "Get the current video item at the playhead position",
        {}
    )

    proxy.register_tool(
        "get_current_clip_thumbnail_image",
        get_current_clip_thumbnail_image,
        "timeline",
        "Get the current clip thumbnail image",
        {}
    )

    logger.info("Registered 8 Timeline Operations tools")
    return 8


# For standalone testing
if __name__ == "__main__":
    print("Timeline Operations Tools - Testing")
    print("=" * 60)

    try:
        timeline = get_current_timeline()
        if timeline:
            print(f"\nTimeline: {timeline.GetName()}")
            print(f"Current timecode: {get_current_timecode()}")
            print(f"Start timecode: {get_start_timecode()}")
        else:
            print("\nNo timeline active")
    except Exception as e:
        print(f"Error: {e}")
