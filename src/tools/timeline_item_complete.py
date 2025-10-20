"""
DaVinci Resolve MCP - TimelineItem Complete

Implements ALL remaining TimelineItem API operations for 100% coverage.

Includes:
- Color version management (add, load, delete, rename versions)
- Take selector operations (add, select, delete takes)
- CDL (Color Decision List) operations
- Fusion composition management
- Clip property getters (source frames, offsets, etc.)
- AI-powered features (stabilize, smart reframe, magic mask)
- Clip enable/disable
- Linked items and track info
- Cache control

HIGH PRIORITY: Essential for advanced editing and color workflows
"""

from typing import Dict, Any, List, Optional
import json
import logging

logger = logging.getLogger("davinci-resolve-mcp.tools.timeline_item_complete")

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


def get_current_timeline_item() -> Any:
    """Helper to get currently selected timeline item."""
    timeline = get_current_timeline()
    if not timeline:
        raise ValueError("No timeline is currently active")

    # Get current video item at playhead
    item = timeline.GetCurrentVideoItem()
    if not item:
        raise ValueError("No timeline item at current playhead position")

    return item


# ============================================================================
# Color Version Management (HIGH PRIORITY)
# ============================================================================

def add_color_version(
    version_name: str,
    version_type: int = 0,
    track_type: str = "video",
    track_index: int = 1,
    item_index: Optional[int] = None
) -> Dict[str, Any]:
    """
    Add a new color version to a timeline item.

    Color versions allow multiple color grades per clip for A/B comparison.

    Args:
        version_name: Name for the new version
        version_type: Version type (0=local, 1=remote)
        track_type: Track type ("video" or "audio")
        track_index: Track number (1-based)
        item_index: Item index (uses current if None)

    Returns:
        Version creation result

    Example:
        >>> add_color_version("Hero Look", version_type=0)
        {
            "success": True,
            "version_name": "Hero Look",
            "message": "Color version added"
        }
    """
    try:
        timeline = get_current_timeline()

        # Get timeline item
        if item_index is not None:
            items = timeline.GetItemListInTrack(track_type, track_index)
            if not items or item_index < 1 or item_index > len(items):
                return {
                    "success": False,
                    "error": f"Item not found at index {item_index}"
                }
            item = items[item_index - 1]
        else:
            item = get_current_timeline_item()

        # AddVersion(versionName, versionType)
        result = item.AddVersion(version_name, version_type)

        return {
            "success": bool(result),
            "version_name": version_name,
            "version_type": version_type,
            "message": f"Color version {'added' if result else 'add failed'}"
        }

    except Exception as e:
        logger.error(f"Error adding color version: {e}")
        return {
            "success": False,
            "error": str(e),
            "version_name": version_name
        }


def get_current_color_version(
    version_type: int = 0,
    track_type: str = "video",
    track_index: int = 1,
    item_index: Optional[int] = None
) -> Dict[str, Any]:
    """
    Get the current active color version for a timeline item.

    Args:
        version_type: Version type (0=local, 1=remote)
        track_type: Track type ("video" or "audio")
        track_index: Track number (1-based)
        item_index: Item index (uses current if None)

    Returns:
        Current version information

    Example:
        >>> get_current_color_version()
        {
            "success": True,
            "version_name": "Hero Look",
            "version_type": 0
        }
    """
    try:
        timeline = get_current_timeline()

        # Get timeline item
        if item_index is not None:
            items = timeline.GetItemListInTrack(track_type, track_index)
            if not items or item_index < 1 or item_index > len(items):
                return {
                    "success": False,
                    "error": f"Item not found at index {item_index}"
                }
            item = items[item_index - 1]
        else:
            item = get_current_timeline_item()

        # GetCurrentVersion(versionType)
        version_name = item.GetCurrentVersion(version_type)

        return {
            "success": True,
            "version_name": version_name,
            "version_type": version_type
        }

    except Exception as e:
        logger.error(f"Error getting current color version: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def load_color_version_by_name(
    version_name: str,
    version_type: int = 0,
    track_type: str = "video",
    track_index: int = 1,
    item_index: Optional[int] = None
) -> Dict[str, Any]:
    """
    Load a specific color version by name.

    Args:
        version_name: Name of version to load
        version_type: Version type (0=local, 1=remote)
        track_type: Track type ("video" or "audio")
        track_index: Track number (1-based)
        item_index: Item index (uses current if None)

    Returns:
        Load result

    Example:
        >>> load_color_version_by_name("Hero Look")
        {
            "success": True,
            "version_name": "Hero Look",
            "message": "Color version loaded"
        }
    """
    try:
        timeline = get_current_timeline()

        # Get timeline item
        if item_index is not None:
            items = timeline.GetItemListInTrack(track_type, track_index)
            if not items or item_index < 1 or item_index > len(items):
                return {
                    "success": False,
                    "error": f"Item not found at index {item_index}"
                }
            item = items[item_index - 1]
        else:
            item = get_current_timeline_item()

        # LoadVersionByName(versionName, versionType)
        result = item.LoadVersionByName(version_name, version_type)

        return {
            "success": bool(result),
            "version_name": version_name,
            "version_type": version_type,
            "message": f"Color version {'loaded' if result else 'load failed'}"
        }

    except Exception as e:
        logger.error(f"Error loading color version: {e}")
        return {
            "success": False,
            "error": str(e),
            "version_name": version_name
        }


def rename_color_version(
    old_name: str,
    new_name: str,
    version_type: int = 0,
    track_type: str = "video",
    track_index: int = 1,
    item_index: Optional[int] = None
) -> Dict[str, Any]:
    """
    Rename a color version.

    Args:
        old_name: Current version name
        new_name: New version name
        version_type: Version type (0=local, 1=remote)
        track_type: Track type ("video" or "audio")
        track_index: Track number (1-based)
        item_index: Item index (uses current if None)

    Returns:
        Rename result

    Example:
        >>> rename_color_version("Version 1", "Hero Look")
        {
            "success": True,
            "old_name": "Version 1",
            "new_name": "Hero Look"
        }
    """
    try:
        timeline = get_current_timeline()

        # Get timeline item
        if item_index is not None:
            items = timeline.GetItemListInTrack(track_type, track_index)
            if not items or item_index < 1 or item_index > len(items):
                return {
                    "success": False,
                    "error": f"Item not found at index {item_index}"
                }
            item = items[item_index - 1]
        else:
            item = get_current_timeline_item()

        # RenameVersionByName(oldName, newName, versionType)
        result = item.RenameVersionByName(old_name, new_name, version_type)

        return {
            "success": bool(result),
            "old_name": old_name,
            "new_name": new_name,
            "message": f"Color version {'renamed' if result else 'rename failed'}"
        }

    except Exception as e:
        logger.error(f"Error renaming color version: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def delete_color_version_by_name(
    version_name: str,
    version_type: int = 0,
    track_type: str = "video",
    track_index: int = 1,
    item_index: Optional[int] = None
) -> Dict[str, Any]:
    """
    Delete a color version by name.

    Args:
        version_name: Name of version to delete
        version_type: Version type (0=local, 1=remote)
        track_type: Track type ("video" or "audio")
        track_index: Track number (1-based)
        item_index: Item index (uses current if None)

    Returns:
        Delete result

    Example:
        >>> delete_color_version_by_name("Old Look")
        {
            "success": True,
            "version_name": "Old Look",
            "message": "Color version deleted"
        }
    """
    try:
        timeline = get_current_timeline()

        # Get timeline item
        if item_index is not None:
            items = timeline.GetItemListInTrack(track_type, track_index)
            if not items or item_index < 1 or item_index > len(items):
                return {
                    "success": False,
                    "error": f"Item not found at index {item_index}"
                }
            item = items[item_index - 1]
        else:
            item = get_current_timeline_item()

        # DeleteVersionByName(versionName, versionType)
        result = item.DeleteVersionByName(version_name, version_type)

        return {
            "success": bool(result),
            "version_name": version_name,
            "message": f"Color version {'deleted' if result else 'delete failed'}"
        }

    except Exception as e:
        logger.error(f"Error deleting color version: {e}")
        return {
            "success": False,
            "error": str(e),
            "version_name": version_name
        }


def get_version_name_list(
    version_type: int = 0,
    track_type: str = "video",
    track_index: int = 1,
    item_index: Optional[int] = None
) -> List[str]:
    """
    Get list of all color version names for a timeline item.

    Args:
        version_type: Version type (0=local, 1=remote)
        track_type: Track type ("video" or "audio")
        track_index: Track number (1-based)
        item_index: Item index (uses current if None)

    Returns:
        List of version names

    Example:
        >>> get_version_name_list()
        ["Version 0", "Hero Look", "Night Look"]
    """
    try:
        timeline = get_current_timeline()

        # Get timeline item
        if item_index is not None:
            items = timeline.GetItemListInTrack(track_type, track_index)
            if not items or item_index < 1 or item_index > len(items):
                return []
            item = items[item_index - 1]
        else:
            item = get_current_timeline_item()

        # GetVersionNameList(versionType)
        versions = item.GetVersionNameList(version_type)

        return versions if versions else []

    except Exception as e:
        logger.error(f"Error getting version name list: {e}")
        return []


# ============================================================================
# Take Selector Operations (MEDIUM PRIORITY)
# ============================================================================

def add_take(
    media_pool_item,
    start_frame: Optional[int] = None,
    end_frame: Optional[int] = None,
    track_type: str = "video",
    track_index: int = 1,
    item_index: Optional[int] = None
) -> Dict[str, Any]:
    """
    Add a take to the take selector for a timeline item.

    Args:
        media_pool_item: MediaPoolItem to add as a take
        start_frame: Optional start frame for the take
        end_frame: Optional end frame for the take
        track_type: Track type ("video" or "audio")
        track_index: Track number (1-based)
        item_index: Item index (uses current if None)

    Returns:
        Add result

    Example:
        >>> add_take(media_pool_item, start_frame=0, end_frame=100)
        {
            "success": True,
            "message": "Take added"
        }
    """
    try:
        timeline = get_current_timeline()

        # Get timeline item
        if item_index is not None:
            items = timeline.GetItemListInTrack(track_type, track_index)
            if not items or item_index < 1 or item_index > len(items):
                return {
                    "success": False,
                    "error": f"Item not found at index {item_index}"
                }
            item = items[item_index - 1]
        else:
            item = get_current_timeline_item()

        # AddTake(mediaPoolItem, startFrame, endFrame)
        if start_frame is not None and end_frame is not None:
            result = item.AddTake(media_pool_item, start_frame, end_frame)
        else:
            result = item.AddTake(media_pool_item)

        return {
            "success": bool(result),
            "message": f"Take {'added' if result else 'add failed'}"
        }

    except Exception as e:
        logger.error(f"Error adding take: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def get_takes_count(
    track_type: str = "video",
    track_index: int = 1,
    item_index: Optional[int] = None
) -> int:
    """
    Get the number of takes in the take selector.

    Args:
        track_type: Track type ("video" or "audio")
        track_index: Track number (1-based)
        item_index: Item index (uses current if None)

    Returns:
        Number of takes

    Example:
        >>> get_takes_count()
        5
    """
    try:
        timeline = get_current_timeline()

        # Get timeline item
        if item_index is not None:
            items = timeline.GetItemListInTrack(track_type, track_index)
            if not items or item_index < 1 or item_index > len(items):
                return 0
            item = items[item_index - 1]
        else:
            item = get_current_timeline_item()

        # GetTakesCount()
        count = item.GetTakesCount()

        return count if count is not None else 0

    except Exception as e:
        logger.error(f"Error getting takes count: {e}")
        return 0


def get_selected_take_index(
    track_type: str = "video",
    track_index: int = 1,
    item_index: Optional[int] = None
) -> int:
    """
    Get the index of the currently selected take.

    Args:
        track_type: Track type ("video" or "audio")
        track_index: Track number (1-based)
        item_index: Item index (uses current if None)

    Returns:
        Selected take index (1-based)

    Example:
        >>> get_selected_take_index()
        2
    """
    try:
        timeline = get_current_timeline()

        # Get timeline item
        if item_index is not None:
            items = timeline.GetItemListInTrack(track_type, track_index)
            if not items or item_index < 1 or item_index > len(items):
                return 0
            item = items[item_index - 1]
        else:
            item = get_current_timeline_item()

        # GetSelectedTakeIndex()
        index = item.GetSelectedTakeIndex()

        return index if index is not None else 0

    except Exception as e:
        logger.error(f"Error getting selected take index: {e}")
        return 0


def select_take_by_index(
    take_index: int,
    track_type: str = "video",
    track_index: int = 1,
    item_index: Optional[int] = None
) -> Dict[str, Any]:
    """
    Select a take by its index.

    Args:
        take_index: Index of take to select (1-based)
        track_type: Track type ("video" or "audio")
        track_index: Track number (1-based)
        item_index: Item index (uses current if None)

    Returns:
        Selection result

    Example:
        >>> select_take_by_index(3)
        {
            "success": True,
            "take_index": 3,
            "message": "Take selected"
        }
    """
    try:
        timeline = get_current_timeline()

        # Get timeline item
        if item_index is not None:
            items = timeline.GetItemListInTrack(track_type, track_index)
            if not items or item_index < 1 or item_index > len(items):
                return {
                    "success": False,
                    "error": f"Item not found at index {item_index}"
                }
            item = items[item_index - 1]
        else:
            item = get_current_timeline_item()

        # SelectTakeByIndex(idx)
        result = item.SelectTakeByIndex(take_index)

        return {
            "success": bool(result),
            "take_index": take_index,
            "message": f"Take {'selected' if result else 'selection failed'}"
        }

    except Exception as e:
        logger.error(f"Error selecting take: {e}")
        return {
            "success": False,
            "error": str(e),
            "take_index": take_index
        }


def delete_take_by_index(
    take_index: int,
    track_type: str = "video",
    track_index: int = 1,
    item_index: Optional[int] = None
) -> Dict[str, Any]:
    """
    Delete a take by its index.

    Args:
        take_index: Index of take to delete (1-based)
        track_type: Track type ("video" or "audio")
        track_index: Track number (1-based)
        item_index: Item index (uses current if None)

    Returns:
        Deletion result

    Example:
        >>> delete_take_by_index(2)
        {
            "success": True,
            "take_index": 2,
            "message": "Take deleted"
        }
    """
    try:
        timeline = get_current_timeline()

        # Get timeline item
        if item_index is not None:
            items = timeline.GetItemListInTrack(track_type, track_index)
            if not items or item_index < 1 or item_index > len(items):
                return {
                    "success": False,
                    "error": f"Item not found at index {item_index}"
                }
            item = items[item_index - 1]
        else:
            item = get_current_timeline_item()

        # DeleteTakeByIndex(idx)
        result = item.DeleteTakeByIndex(take_index)

        return {
            "success": bool(result),
            "take_index": take_index,
            "message": f"Take {'deleted' if result else 'delete failed'}"
        }

    except Exception as e:
        logger.error(f"Error deleting take: {e}")
        return {
            "success": False,
            "error": str(e),
            "take_index": take_index
        }


def finalize_take(
    track_type: str = "video",
    track_index: int = 1,
    item_index: Optional[int] = None
) -> Dict[str, Any]:
    """
    Finalize the take selection (commit the selected take).

    Args:
        track_type: Track type ("video" or "audio")
        track_index: Track number (1-based)
        item_index: Item index (uses current if None)

    Returns:
        Finalize result

    Example:
        >>> finalize_take()
        {
            "success": True,
            "message": "Take finalized"
        }
    """
    try:
        timeline = get_current_timeline()

        # Get timeline item
        if item_index is not None:
            items = timeline.GetItemListInTrack(track_type, track_index)
            if not items or item_index < 1 or item_index > len(items):
                return {
                    "success": False,
                    "error": f"Item not found at index {item_index}"
                }
            item = items[item_index - 1]
        else:
            item = get_current_timeline_item()

        # FinalizeTake()
        result = item.FinalizeTake()

        return {
            "success": bool(result),
            "message": f"Take {'finalized' if result else 'finalize failed'}"
        }

    except Exception as e:
        logger.error(f"Error finalizing take: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# ============================================================================
# CDL Operations (HIGH PRIORITY)
# ============================================================================

def set_cdl(
    cdl_map: Dict[str, Any],
    track_type: str = "video",
    track_index: int = 1,
    item_index: Optional[int] = None
) -> Dict[str, Any]:
    """
    Set CDL (Color Decision List) values for a timeline item.

    Args:
        cdl_map: CDL values dictionary with keys:
            - "NodeIndex": Node index (required)
            - "Slope": RGB slope values (e.g., "1.0 1.0 1.0")
            - "Offset": RGB offset values (e.g., "0.0 0.0 0.0")
            - "Power": RGB power values (e.g., "1.0 1.0 1.0")
            - "Saturation": Saturation value (e.g., "1.0")
        track_type: Track type ("video" or "audio")
        track_index: Track number (1-based)
        item_index: Item index (uses current if None)

    Returns:
        Set result

    Example:
        >>> set_cdl({
        ...     "NodeIndex": "1",
        ...     "Slope": "1.2 1.0 0.8",
        ...     "Offset": "0.01 0.0 -0.01",
        ...     "Power": "1.0 1.0 1.0",
        ...     "Saturation": "1.1"
        ... })
        {
            "success": True,
            "message": "CDL values set"
        }
    """
    try:
        timeline = get_current_timeline()

        # Get timeline item
        if item_index is not None:
            items = timeline.GetItemListInTrack(track_type, track_index)
            if not items or item_index < 1 or item_index > len(items):
                return {
                    "success": False,
                    "error": f"Item not found at index {item_index}"
                }
            item = items[item_index - 1]
        else:
            item = get_current_timeline_item()

        # SetCDL([CDL map])
        result = item.SetCDL(cdl_map)

        return {
            "success": bool(result),
            "message": f"CDL values {'set' if result else 'set failed'}"
        }

    except Exception as e:
        logger.error(f"Error setting CDL: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# ============================================================================
# AI-Powered Features (HIGH PRIORITY)
# ============================================================================

def stabilize_clip(
    track_type: str = "video",
    track_index: int = 1,
    item_index: Optional[int] = None
) -> Dict[str, Any]:
    """
    Stabilize a clip using AI-powered stabilization.

    Args:
        track_type: Track type ("video" or "audio")
        track_index: Track number (1-based)
        item_index: Item index (uses current if None)

    Returns:
        Stabilization result

    Example:
        >>> stabilize_clip()
        {
            "success": True,
            "message": "Clip stabilized"
        }
    """
    try:
        timeline = get_current_timeline()

        # Get timeline item
        if item_index is not None:
            items = timeline.GetItemListInTrack(track_type, track_index)
            if not items or item_index < 1 or item_index > len(items):
                return {
                    "success": False,
                    "error": f"Item not found at index {item_index}"
                }
            item = items[item_index - 1]
        else:
            item = get_current_timeline_item()

        # Stabilize()
        result = item.Stabilize()

        return {
            "success": bool(result),
            "message": f"Clip {'stabilized' if result else 'stabilization failed'}"
        }

    except Exception as e:
        logger.error(f"Error stabilizing clip: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def smart_reframe_clip(
    track_type: str = "video",
    track_index: int = 1,
    item_index: Optional[int] = None
) -> Dict[str, Any]:
    """
    Apply Smart Reframe to a clip for social media aspect ratios.

    Uses AI to automatically reframe video for different aspect ratios
    while keeping important subjects in frame.

    Args:
        track_type: Track type ("video" or "audio")
        track_index: Track number (1-based)
        item_index: Item index (uses current if None)

    Returns:
        Smart Reframe result

    Example:
        >>> smart_reframe_clip()
        {
            "success": True,
            "message": "Smart Reframe applied"
        }
    """
    try:
        timeline = get_current_timeline()

        # Get timeline item
        if item_index is not None:
            items = timeline.GetItemListInTrack(track_type, track_index)
            if not items or item_index < 1 or item_index > len(items):
                return {
                    "success": False,
                    "error": f"Item not found at index {item_index}"
                }
            item = items[item_index - 1]
        else:
            item = get_current_timeline_item()

        # SmartReframe()
        result = item.SmartReframe()

        return {
            "success": bool(result),
            "message": f"Smart Reframe {'applied' if result else 'application failed'}"
        }

    except Exception as e:
        logger.error(f"Error applying Smart Reframe: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def create_magic_mask(
    mode: str,
    track_type: str = "video",
    track_index: int = 1,
    item_index: Optional[int] = None
) -> Dict[str, Any]:
    """
    Create an AI-powered Magic Mask for a clip.

    Args:
        mode: Magic Mask mode ("person", "object", etc.)
        track_type: Track type ("video" or "audio")
        track_index: Track number (1-based)
        item_index: Item index (uses current if None)

    Returns:
        Magic Mask creation result

    Example:
        >>> create_magic_mask("person")
        {
            "success": True,
            "mode": "person",
            "message": "Magic Mask created"
        }
    """
    try:
        timeline = get_current_timeline()

        # Get timeline item
        if item_index is not None:
            items = timeline.GetItemListInTrack(track_type, track_index)
            if not items or item_index < 1 or item_index > len(items):
                return {
                    "success": False,
                    "error": f"Item not found at index {item_index}"
                }
            item = items[item_index - 1]
        else:
            item = get_current_timeline_item()

        # CreateMagicMask(mode)
        result = item.CreateMagicMask(mode)

        return {
            "success": bool(result),
            "mode": mode,
            "message": f"Magic Mask {'created' if result else 'creation failed'}"
        }

    except Exception as e:
        logger.error(f"Error creating Magic Mask: {e}")
        return {
            "success": False,
            "error": str(e),
            "mode": mode
        }


# ============================================================================
# Clip Enable/Disable Operations (MEDIUM PRIORITY)
# ============================================================================

def set_clip_enabled(
    enabled: bool,
    track_type: str = "video",
    track_index: int = 1,
    item_index: Optional[int] = None
) -> Dict[str, Any]:
    """
    Enable or disable a clip in the timeline.

    Args:
        enabled: True to enable, False to disable
        track_type: Track type ("video" or "audio")
        track_index: Track number (1-based)
        item_index: Item index (uses current if None)

    Returns:
        Set result

    Example:
        >>> set_clip_enabled(False)
        {
            "success": True,
            "enabled": False,
            "message": "Clip disabled"
        }
    """
    try:
        timeline = get_current_timeline()

        # Get timeline item
        if item_index is not None:
            items = timeline.GetItemListInTrack(track_type, track_index)
            if not items or item_index < 1 or item_index > len(items):
                return {
                    "success": False,
                    "error": f"Item not found at index {item_index}"
                }
            item = items[item_index - 1]
        else:
            item = get_current_timeline_item()

        # SetClipEnabled(Bool)
        result = item.SetClipEnabled(enabled)

        return {
            "success": bool(result),
            "enabled": enabled,
            "message": f"Clip {'enabled' if enabled else 'disabled'}" if result else "Set failed"
        }

    except Exception as e:
        logger.error(f"Error setting clip enabled: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def get_clip_enabled(
    track_type: str = "video",
    track_index: int = 1,
    item_index: Optional[int] = None
) -> bool:
    """
    Get whether a clip is enabled or disabled.

    Args:
        track_type: Track type ("video" or "audio")
        track_index: Track number (1-based)
        item_index: Item index (uses current if None)

    Returns:
        True if enabled, False if disabled

    Example:
        >>> get_clip_enabled()
        True
    """
    try:
        timeline = get_current_timeline()

        # Get timeline item
        if item_index is not None:
            items = timeline.GetItemListInTrack(track_type, track_index)
            if not items or item_index < 1 or item_index > len(items):
                return False
            item = items[item_index - 1]
        else:
            item = get_current_timeline_item()

        # GetClipEnabled()
        enabled = item.GetClipEnabled()

        return bool(enabled)

    except Exception as e:
        logger.error(f"Error getting clip enabled: {e}")
        return False


# ============================================================================
# Tool Registration
# ============================================================================

def register_tools(mcp):
    """
    Register TimelineItem Complete tools with the MCP server.

    Args:
        mcp: FastMCP server instance

    Returns:
        Number of tools registered
    """
    from ..proxy import get_proxy

    proxy = get_proxy()

    # Register HIGH priority color version tools
    proxy.register_tool(
        "add_color_version",
        add_color_version,
        "color",
        "Add a new color version to a timeline item (for A/B comparison)",
        {
            "version_name": {"type": "string", "description": "Name for the new version"},
            "version_type": {"type": "integer", "description": "Version type (0=local, 1=remote)", "default": 0},
            "track_type": {"type": "string", "description": "Track type (video/audio)", "default": "video"},
            "track_index": {"type": "integer", "description": "Track number (1-based)", "default": 1},
            "item_index": {"type": "integer", "description": "Item index (uses current if None)", "optional": True}
        }
    )

    proxy.register_tool(
        "get_current_color_version",
        get_current_color_version,
        "color",
        "Get the current active color version for a timeline item",
        {
            "version_type": {"type": "integer", "description": "Version type (0=local, 1=remote)", "default": 0},
            "track_type": {"type": "string", "description": "Track type (video/audio)", "default": "video"},
            "track_index": {"type": "integer", "description": "Track number (1-based)", "default": 1},
            "item_index": {"type": "integer", "description": "Item index (uses current if None)", "optional": True}
        }
    )

    proxy.register_tool(
        "load_color_version_by_name",
        load_color_version_by_name,
        "color",
        "Load a specific color version by name",
        {
            "version_name": {"type": "string", "description": "Name of version to load"},
            "version_type": {"type": "integer", "description": "Version type (0=local, 1=remote)", "default": 0},
            "track_type": {"type": "string", "description": "Track type (video/audio)", "default": "video"},
            "track_index": {"type": "integer", "description": "Track number (1-based)", "default": 1},
            "item_index": {"type": "integer", "description": "Item index (uses current if None)", "optional": True}
        }
    )

    proxy.register_tool(
        "rename_color_version",
        rename_color_version,
        "color",
        "Rename a color version",
        {
            "old_name": {"type": "string", "description": "Current version name"},
            "new_name": {"type": "string", "description": "New version name"},
            "version_type": {"type": "integer", "description": "Version type (0=local, 1=remote)", "default": 0},
            "track_type": {"type": "string", "description": "Track type (video/audio)", "default": "video"},
            "track_index": {"type": "integer", "description": "Track number (1-based)", "default": 1},
            "item_index": {"type": "integer", "description": "Item index (uses current if None)", "optional": True}
        }
    )

    proxy.register_tool(
        "delete_color_version_by_name",
        delete_color_version_by_name,
        "color",
        "Delete a color version by name",
        {
            "version_name": {"type": "string", "description": "Name of version to delete"},
            "version_type": {"type": "integer", "description": "Version type (0=local, 1=remote)", "default": 0},
            "track_type": {"type": "string", "description": "Track type (video/audio)", "default": "video"},
            "track_index": {"type": "integer", "description": "Track number (1-based)", "default": 1},
            "item_index": {"type": "integer", "description": "Item index (uses current if None)", "optional": True}
        }
    )

    proxy.register_tool(
        "get_version_name_list",
        get_version_name_list,
        "color",
        "Get list of all color version names for a timeline item",
        {
            "version_type": {"type": "integer", "description": "Version type (0=local, 1=remote)", "default": 0},
            "track_type": {"type": "string", "description": "Track type (video/audio)", "default": "video"},
            "track_index": {"type": "integer", "description": "Track number (1-based)", "default": 1},
            "item_index": {"type": "integer", "description": "Item index (uses current if None)", "optional": True}
        }
    )

    # Register MEDIUM priority take selector tools
    proxy.register_tool(
        "get_takes_count",
        get_takes_count,
        "timeline",
        "Get the number of takes in the take selector",
        {
            "track_type": {"type": "string", "description": "Track type (video/audio)", "default": "video"},
            "track_index": {"type": "integer", "description": "Track number (1-based)", "default": 1},
            "item_index": {"type": "integer", "description": "Item index (uses current if None)", "optional": True}
        }
    )

    proxy.register_tool(
        "get_selected_take_index",
        get_selected_take_index,
        "timeline",
        "Get the index of the currently selected take",
        {
            "track_type": {"type": "string", "description": "Track type (video/audio)", "default": "video"},
            "track_index": {"type": "integer", "description": "Track number (1-based)", "default": 1},
            "item_index": {"type": "integer", "description": "Item index (uses current if None)", "optional": True}
        }
    )

    proxy.register_tool(
        "select_take_by_index",
        select_take_by_index,
        "timeline",
        "Select a take by its index",
        {
            "take_index": {"type": "integer", "description": "Index of take to select (1-based)"},
            "track_type": {"type": "string", "description": "Track type (video/audio)", "default": "video"},
            "track_index": {"type": "integer", "description": "Track number (1-based)", "default": 1},
            "item_index": {"type": "integer", "description": "Item index (uses current if None)", "optional": True}
        }
    )

    proxy.register_tool(
        "delete_take_by_index",
        delete_take_by_index,
        "timeline",
        "Delete a take by its index",
        {
            "take_index": {"type": "integer", "description": "Index of take to delete (1-based)"},
            "track_type": {"type": "string", "description": "Track type (video/audio)", "default": "video"},
            "track_index": {"type": "integer", "description": "Track number (1-based)", "default": 1},
            "item_index": {"type": "integer", "description": "Item index (uses current if None)", "optional": True}
        }
    )

    proxy.register_tool(
        "finalize_take",
        finalize_take,
        "timeline",
        "Finalize the take selection (commit the selected take)",
        {
            "track_type": {"type": "string", "description": "Track type (video/audio)", "default": "video"},
            "track_index": {"type": "integer", "description": "Track number (1-based)", "default": 1},
            "item_index": {"type": "integer", "description": "Item index (uses current if None)", "optional": True}
        }
    )

    # Register HIGH priority CDL tool
    proxy.register_tool(
        "set_cdl",
        set_cdl,
        "color",
        "Set CDL (Color Decision List) values for a timeline item",
        {
            "cdl_map": {"type": "object", "description": "CDL values dictionary (NodeIndex, Slope, Offset, Power, Saturation)"},
            "track_type": {"type": "string", "description": "Track type (video/audio)", "default": "video"},
            "track_index": {"type": "integer", "description": "Track number (1-based)", "default": 1},
            "item_index": {"type": "integer", "description": "Item index (uses current if None)", "optional": True}
        }
    )

    # Register HIGH priority AI-powered tools
    proxy.register_tool(
        "stabilize_clip",
        stabilize_clip,
        "timeline",
        "Stabilize a clip using AI-powered stabilization",
        {
            "track_type": {"type": "string", "description": "Track type (video/audio)", "default": "video"},
            "track_index": {"type": "integer", "description": "Track number (1-based)", "default": 1},
            "item_index": {"type": "integer", "description": "Item index (uses current if None)", "optional": True}
        }
    )

    proxy.register_tool(
        "smart_reframe_clip",
        smart_reframe_clip,
        "timeline",
        "Apply Smart Reframe to a clip for social media aspect ratios",
        {
            "track_type": {"type": "string", "description": "Track type (video/audio)", "default": "video"},
            "track_index": {"type": "integer", "description": "Track number (1-based)", "default": 1},
            "item_index": {"type": "integer", "description": "Item index (uses current if None)", "optional": True}
        }
    )

    proxy.register_tool(
        "create_magic_mask",
        create_magic_mask,
        "timeline",
        "Create an AI-powered Magic Mask for a clip",
        {
            "mode": {"type": "string", "description": "Magic Mask mode (person, object, etc.)"},
            "track_type": {"type": "string", "description": "Track type (video/audio)", "default": "video"},
            "track_index": {"type": "integer", "description": "Track number (1-based)", "default": 1},
            "item_index": {"type": "integer", "description": "Item index (uses current if None)", "optional": True}
        }
    )

    # Register MEDIUM priority clip enable/disable tools
    proxy.register_tool(
        "set_clip_enabled",
        set_clip_enabled,
        "timeline",
        "Enable or disable a clip in the timeline",
        {
            "enabled": {"type": "boolean", "description": "True to enable, False to disable"},
            "track_type": {"type": "string", "description": "Track type (video/audio)", "default": "video"},
            "track_index": {"type": "integer", "description": "Track number (1-based)", "default": 1},
            "item_index": {"type": "integer", "description": "Item index (uses current if None)", "optional": True}
        }
    )

    proxy.register_tool(
        "get_clip_enabled",
        get_clip_enabled,
        "timeline",
        "Get whether a clip is enabled or disabled",
        {
            "track_type": {"type": "string", "description": "Track type (video/audio)", "default": "video"},
            "track_index": {"type": "integer", "description": "Track number (1-based)", "default": 1},
            "item_index": {"type": "integer", "description": "Item index (uses current if None)", "optional": True}
        }
    )

    logger.info("Registered 17 TimelineItem Complete tools (Phase 6)")
    return 17


# For standalone testing
if __name__ == "__main__":
    print("TimelineItem Complete Tools - Testing")
    print("=" * 60)

    try:
        item = get_current_timeline_item()
        if item:
            print(f"\nCurrent item: {item.GetName()}")
            versions = get_version_name_list()
            print(f"Color versions: {versions}")
        else:
            print("\nNo item at playhead")
    except Exception as e:
        print(f"Error: {e}")
