"""
DaVinci Resolve MCP - ColorGroup Complete

Implements ALL ColorGroup API operations for 100% coverage.

Includes:
- Color group name management
- Pre-clip and post-clip node graph access (for group-level grading)

HIGH PRIORITY: Essential for advanced color grouping workflows
"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger("davinci-resolve-mcp.tools.colorgroup_complete")

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


def _find_color_group_by_name(group_name: str):
    """Helper to find a color group by name."""
    project = get_current_project()

    # Get color groups list
    color_groups_list = project.GetColorGroupsList()
    if not color_groups_list or group_name not in color_groups_list:
        raise ValueError(f"Color group '{group_name}' not found")

    # Note: The actual ColorGroup object retrieval may need additional API calls
    # This is a simplified implementation
    # In practice, we might need to iterate through timeline items to find the group object

    timeline = get_current_timeline()
    if not timeline:
        raise ValueError("No timeline is currently active")

    # Search through timeline items to find one with this color group
    track_count = timeline.GetTrackCount("video")
    for track_idx in range(1, track_count + 1):
        items = timeline.GetItemListInTrack("video", track_idx)
        if items:
            for item in items:
                try:
                    color_group = item.GetColorGroup()
                    if color_group and color_group.GetName() == group_name:
                        return color_group
                except:
                    continue

    raise ValueError(f"Could not access ColorGroup object for '{group_name}'")


# ============================================================================
# ColorGroup Name Management (MEDIUM PRIORITY)
# ============================================================================

def get_color_group_name(group_name: str) -> str:
    """
    Get the name of a color group.

    Args:
        group_name: Name of the color group to query

    Returns:
        Color group name

    Example:
        >>> get_color_group_name("Day Exteriors")
        "Day Exteriors"
    """
    try:
        color_group = _find_color_group_by_name(group_name)

        # GetName()
        name = color_group.GetName()

        return name if name else group_name

    except Exception as e:
        logger.error(f"Error getting color group name: {e}")
        return "Error"


def set_color_group_name(old_name: str, new_name: str) -> Dict[str, Any]:
    """
    Set/rename a color group.

    Args:
        old_name: Current name of the color group
        new_name: New name for the color group

    Returns:
        Rename result

    Example:
        >>> set_color_group_name("Group 1", "Day Exteriors")
        {
            "success": True,
            "old_name": "Group 1",
            "new_name": "Day Exteriors",
            "message": "Color group renamed"
        }
    """
    try:
        color_group = _find_color_group_by_name(old_name)

        # SetName(groupName)
        result = color_group.SetName(new_name)

        return {
            "success": bool(result),
            "old_name": old_name,
            "new_name": new_name,
            "message": f"Color group {'renamed' if result else 'rename failed'}"
        }

    except Exception as e:
        logger.error(f"Error setting color group name: {e}")
        return {
            "success": False,
            "error": str(e),
            "old_name": old_name
        }


# ============================================================================
# ColorGroup Node Graph Access (HIGH PRIORITY)
# ============================================================================

def get_color_group_pre_clip_node_graph(group_name: str) -> Dict[str, Any]:
    """
    Get the pre-clip node graph for a color group.

    Pre-clip nodes apply to all clips in the group before clip-level grading.

    Args:
        group_name: Name of the color group

    Returns:
        Node graph object information

    Example:
        >>> get_color_group_pre_clip_node_graph("Day Exteriors")
        {
            "success": True,
            "group_name": "Day Exteriors",
            "has_graph": True,
            "node_count": 2
        }
    """
    try:
        color_group = _find_color_group_by_name(group_name)

        # GetPreClipNodeGraph()
        graph = color_group.GetPreClipNodeGraph()

        if graph:
            try:
                node_count = graph.GetNumNodes()
            except:
                node_count = None

            return {
                "success": True,
                "group_name": group_name,
                "has_graph": True,
                "node_count": node_count,
                "graph": graph  # Actual graph object
            }
        else:
            return {
                "success": False,
                "group_name": group_name,
                "has_graph": False,
                "message": "No pre-clip node graph available"
            }

    except Exception as e:
        logger.error(f"Error getting pre-clip node graph: {e}")
        return {
            "success": False,
            "error": str(e),
            "group_name": group_name
        }


def get_color_group_post_clip_node_graph(group_name: str) -> Dict[str, Any]:
    """
    Get the post-clip node graph for a color group.

    Post-clip nodes apply to all clips in the group after clip-level grading.

    Args:
        group_name: Name of the color group

    Returns:
        Node graph object information

    Example:
        >>> get_color_group_post_clip_node_graph("Day Exteriors")
        {
            "success": True,
            "group_name": "Day Exteriors",
            "has_graph": True,
            "node_count": 3
        }
    """
    try:
        color_group = _find_color_group_by_name(group_name)

        # GetPostClipNodeGraph()
        graph = color_group.GetPostClipNodeGraph()

        if graph:
            try:
                node_count = graph.GetNumNodes()
            except:
                node_count = None

            return {
                "success": True,
                "group_name": group_name,
                "has_graph": True,
                "node_count": node_count,
                "graph": graph  # Actual graph object
            }
        else:
            return {
                "success": False,
                "group_name": group_name,
                "has_graph": False,
                "message": "No post-clip node graph available"
            }

    except Exception as e:
        logger.error(f"Error getting post-clip node graph: {e}")
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
    Register ColorGroup Complete tools with the MCP server.

    Args:
        mcp: FastMCP server instance

    Returns:
        Number of tools registered
    """
    from ..proxy import get_proxy

    proxy = get_proxy()

    # Register MEDIUM priority name management tools
    proxy.register_tool(
        "get_color_group_name",
        get_color_group_name,
        "color",
        "Get the name of a color group",
        {"group_name": {"type": "string", "description": "Name of the color group to query"}}
    )

    proxy.register_tool(
        "set_color_group_name",
        set_color_group_name,
        "color",
        "Set/rename a color group",
        {
            "old_name": {"type": "string", "description": "Current name of the color group"},
            "new_name": {"type": "string", "description": "New name for the color group"}
        }
    )

    # Register HIGH priority node graph tools
    proxy.register_tool(
        "get_color_group_pre_clip_node_graph",
        get_color_group_pre_clip_node_graph,
        "color",
        "Get the pre-clip node graph for a color group (applied before clip-level grading)",
        {"group_name": {"type": "string", "description": "Name of the color group"}}
    )

    proxy.register_tool(
        "get_color_group_post_clip_node_graph",
        get_color_group_post_clip_node_graph,
        "color",
        "Get the post-clip node graph for a color group (applied after clip-level grading)",
        {"group_name": {"type": "string", "description": "Name of the color group"}}
    )

    logger.info("Registered 4 ColorGroup Complete tools (Phase 6)")
    return 4


# For standalone testing
if __name__ == "__main__":
    print("ColorGroup Complete Tools - Testing")
    print("=" * 60)

    try:
        project = get_current_project()
        if project:
            color_groups = project.GetColorGroupsList()
            print(f"\nColor Groups: {color_groups}")
        else:
            print("\nNo project available")
    except Exception as e:
        print(f"Error: {e}")
