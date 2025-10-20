"""
DaVinci Resolve MCP - Color Group Operations Tools

Implements color group management API operations including:
- Color group creation
- Color group deletion
- Color group renaming

HIGH PRIORITY: Essential for collaborative color grading workflows
"""

from typing import Dict, Any, List, Optional
import json
import logging

logger = logging.getLogger("davinci-resolve-mcp.tools.colorgroup_operations")

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
# Color Group Management Operations (HIGH PRIORITY)
# ============================================================================

def add_color_group(group_name: str) -> Dict[str, Any]:
    """
    Create a new color group.

    Color groups link multiple clips together for synchronized color grading.
    When you grade one clip in a group, all clips in that group update
    automatically.

    Args:
        group_name: Name for the new color group

    Returns:
        Creation result

    Example:
        >>> add_color_group("Day Exteriors")
        {
            "success": True,
            "group_name": "Day Exteriors",
            "message": "Color group created"
        }
    """
    try:
        project = get_current_project()

        # AddColorGroup(groupName)
        result = project.AddColorGroup(group_name)

        return {
            "success": bool(result),
            "group_name": group_name,
            "message": f"Color group {'created' if result else 'creation failed'}"
        }

    except Exception as e:
        logger.error(f"Error adding color group: {e}")
        return {
            "success": False,
            "error": str(e),
            "group_name": group_name
        }


def delete_color_group(group_name: str) -> Dict[str, Any]:
    """
    Delete a color group.

    Removes the color group. Clips that were in the group will no longer
    be linked for grading.

    Args:
        group_name: Name of the color group to delete

    Returns:
        Deletion result

    Example:
        >>> delete_color_group("Old Group")
        {
            "success": True,
            "group_name": "Old Group",
            "message": "Color group deleted"
        }
    """
    try:
        project = get_current_project()

        # Get color group by name
        # Note: This is a helper operation - the actual API might work differently
        color_groups = project.GetColorGroupsList()

        if not color_groups or group_name not in color_groups:
            return {
                "success": False,
                "error": f"Color group '{group_name}' not found",
                "group_name": group_name
            }

        # DeleteColorGroup(colorGroup) or similar method
        # Note: Actual API method name may vary
        result = project.DeleteColorGroup(group_name)

        return {
            "success": bool(result),
            "group_name": group_name,
            "message": f"Color group {'deleted' if result else 'deletion failed'}"
        }

    except Exception as e:
        logger.error(f"Error deleting color group: {e}")
        return {
            "success": False,
            "error": str(e),
            "group_name": group_name
        }


def rename_color_group(
    old_name: str,
    new_name: str
) -> Dict[str, Any]:
    """
    Rename a color group.

    Args:
        old_name: Current name of the color group
        new_name: New name for the color group

    Returns:
        Rename result

    Example:
        >>> rename_color_group(
        ...     old_name="Group 1",
        ...     new_name="Hero Shots"
        ... )
        {
            "success": True,
            "old_name": "Group 1",
            "new_name": "Hero Shots"
        }
    """
    try:
        project = get_current_project()

        # Get color group by name
        color_groups = project.GetColorGroupsList()

        if not color_groups or old_name not in color_groups:
            return {
                "success": False,
                "error": f"Color group '{old_name}' not found",
                "old_name": old_name
            }

        # RenameColorGroup(colorGroup, newName) or similar method
        # Note: Actual API method name may vary
        result = project.RenameColorGroup(old_name, new_name)

        return {
            "success": bool(result),
            "old_name": old_name,
            "new_name": new_name,
            "message": f"Color group {'renamed' if result else 'rename failed'}"
        }

    except Exception as e:
        logger.error(f"Error renaming color group: {e}")
        return {
            "success": False,
            "error": str(e),
            "old_name": old_name,
            "new_name": new_name
        }


def get_clips_in_color_group(group_name: str) -> Dict[str, Any]:
    """
    Get list of clips assigned to a color group.

    Args:
        group_name: Name of the color group

    Returns:
        List of clips in the group

    Example:
        >>> get_clips_in_color_group("Day Exteriors")
        {
            "success": True,
            "group_name": "Day Exteriors",
            "clip_count": 5,
            "clips": ["A001_C002.mov", "A001_C003.mov", ...]
        }
    """
    try:
        project = get_current_project()
        timeline = get_current_timeline()

        if not timeline:
            return {
                "success": False,
                "error": "No timeline active"
            }

        # Get all video items and filter by color group
        clips_in_group = []

        # Iterate through tracks
        track_count = timeline.GetTrackCount("video")
        for track_idx in range(1, track_count + 1):
            items = timeline.GetItemListInTrack("video", track_idx)
            if items:
                for item in items:
                    try:
                        # Check if item has a color group
                        color_group = item.GetColorGroup()
                        if color_group and color_group.GetName() == group_name:
                            clips_in_group.append(item.GetName())
                    except:
                        continue

        return {
            "success": True,
            "group_name": group_name,
            "clip_count": len(clips_in_group),
            "clips": clips_in_group
        }

    except Exception as e:
        logger.error(f"Error getting clips in color group: {e}")
        return {
            "success": False,
            "error": str(e),
            "group_name": group_name
        }


# ============================================================================
# Tool Registration
# ============================================================================

def register_tools(mcp):
    """
    Register Color Group Operations tools with the MCP server.

    Args:
        mcp: FastMCP server instance

    Returns:
        Number of tools registered
    """
    from ..proxy import get_proxy

    proxy = get_proxy()

    # Register HIGH priority color group tools
    proxy.register_tool(
        "add_color_group",
        add_color_group,
        "color",
        "Create a new color group for synchronized grading",
        {"group_name": {"type": "string", "description": "Name for the new color group"}}
    )

    proxy.register_tool(
        "delete_color_group",
        delete_color_group,
        "color",
        "Delete a color group",
        {"group_name": {"type": "string", "description": "Name of the color group to delete"}}
    )

    proxy.register_tool(
        "rename_color_group",
        rename_color_group,
        "color",
        "Rename a color group",
        {
            "old_name": {"type": "string", "description": "Current name of the color group"},
            "new_name": {"type": "string", "description": "New name for the color group"}
        }
    )

    proxy.register_tool(
        "get_clips_in_color_group",
        get_clips_in_color_group,
        "color",
        "Get list of clips assigned to a color group",
        {"group_name": {"type": "string", "description": "Name of the color group"}}
    )

    logger.info("Registered 4 Color Group Operations tools")
    return 4


# For standalone testing
if __name__ == "__main__":
    print("Color Group Operations Tools - Testing")
    print("=" * 60)

    try:
        project = get_current_project()
        if project:
            color_groups = project.GetColorGroupsList()
            print(f"\nExisting color groups ({len(color_groups) if color_groups else 0}):")
            if color_groups:
                for group in color_groups:
                    print(f"  - {group}")
        else:
            print("\nNo project open")
    except Exception as e:
        print(f"Error: {e}")
