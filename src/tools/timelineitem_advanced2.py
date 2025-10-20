"""
DaVinci Resolve MCP - TimelineItem Advanced Features 2

Implements additional high-priority TimelineItem API operations including:
- Grade copying between clips
- LUT export from clips
- Node graph retrieval (pre-clip and post-clip)

HIGH PRIORITY: Essential for advanced color grading workflows
"""

from typing import Dict, Any, List, Optional
import json
import logging

logger = logging.getLogger("davinci-resolve-mcp.tools.timelineitem_advanced2")

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
# Grade Copying Operations (HIGH PRIORITY)
# ============================================================================

def copy_grades_to_clips(
    source_track_type: str,
    source_track_index: int,
    source_item_index: int,
    target_track_type: str,
    target_track_index: int,
    target_item_indices: List[int]
) -> Dict[str, Any]:
    """
    Copy color grades from a source clip to target clips.

    Copies all color grading (nodes, settings, LUTs) from one clip
    to multiple target clips.

    Args:
        source_track_type: Source track type ("video" or "audio")
        source_track_index: Source track number (1-based)
        source_item_index: Source item index (1-based)
        target_track_type: Target track type ("video" or "audio")
        target_track_index: Target track number (1-based)
        target_item_indices: List of target item indices (1-based)

    Returns:
        Copy result with count of successful copies

    Example:
        >>> copy_grades_to_clips(
        ...     source_track_type="video",
        ...     source_track_index=1,
        ...     source_item_index=1,
        ...     target_track_type="video",
        ...     target_track_index=1,
        ...     target_item_indices=[2, 3, 4, 5]
        ... )
        {
            "success": True,
            "source_index": 1,
            "target_count": 4,
            "message": "Grades copied to 4 clips"
        }
    """
    try:
        timeline = get_current_timeline()

        # Get source item
        source_items = timeline.GetItemListInTrack(source_track_type, source_track_index)
        if not source_items or source_item_index < 1 or source_item_index > len(source_items):
            return {
                "success": False,
                "error": f"Source item not found at index {source_item_index}"
            }

        source_item = source_items[source_item_index - 1]

        # Get target items
        target_items_in_track = timeline.GetItemListInTrack(target_track_type, target_track_index)
        if not target_items_in_track:
            return {
                "success": False,
                "error": f"No items in target track {target_track_index}"
            }

        target_items = []
        for idx in target_item_indices:
            if 1 <= idx <= len(target_items_in_track):
                target_items.append(target_items_in_track[idx - 1])

        if not target_items:
            return {
                "success": False,
                "error": "No valid target items found"
            }

        # CopyGrades([tgtTimelineItems])
        result = source_item.CopyGrades(target_items)

        return {
            "success": bool(result),
            "source_index": source_item_index,
            "target_count": len(target_items) if result else 0,
            "message": f"Grades {'copied to' if result else 'copy failed for'} {len(target_items)} clips"
        }

    except Exception as e:
        logger.error(f"Error copying grades: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# ============================================================================
# LUT Export Operations (HIGH PRIORITY)
# ============================================================================

def export_lut(
    export_type: str,
    path: str,
    track_type: str = "video",
    track_index: int = 1,
    item_index: Optional[int] = None
) -> Dict[str, Any]:
    """
    Export a LUT from a timeline item.

    Exports the color grading as a LUT file that can be used in
    other applications or shared with other colorists.

    Args:
        export_type: LUT format:
            - "17pt" - 17-point cube LUT
            - "33pt" - 33-point cube LUT
            - "65pt" - 65-point cube LUT
            - "cdl" - ASC CDL format
        path: Destination file path
        track_type: Track type ("video" or "audio")
        track_index: Track number (1-based)
        item_index: Item index (uses current if None)

    Returns:
        Export result

    Example:
        >>> export_lut(
        ...     export_type="33pt",
        ...     path="/exports/my_grade.cube"
        ... )
        {
            "success": True,
            "export_type": "33pt",
            "path": "/exports/my_grade.cube",
            "message": "LUT exported successfully"
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

        # ExportLUT(exportType, path)
        result = item.ExportLUT(export_type, path)

        return {
            "success": bool(result),
            "export_type": export_type,
            "path": path,
            "message": f"LUT {'exported successfully' if result else 'export failed'}"
        }

    except Exception as e:
        logger.error(f"Error exporting LUT: {e}")
        return {
            "success": False,
            "error": str(e),
            "export_type": export_type,
            "path": path
        }


# ============================================================================
# Node Graph Operations (HIGH PRIORITY)
# ============================================================================

def get_pre_clip_node_graph(
    track_type: str = "video",
    track_index: int = 1,
    item_index: Optional[int] = None,
    layer_index: Optional[int] = None
) -> Dict[str, Any]:
    """
    Get the pre-clip node graph for a timeline item.

    Pre-clip nodes are applied before clip-level color grading.
    Useful for camera LUTs, technical corrections, etc.

    Args:
        track_type: Track type ("video" or "audio")
        track_index: Track number (1-based)
        item_index: Item index (uses current if None)
        layer_index: Layer index for Dolby Vision (optional)

    Returns:
        Node graph object information

    Example:
        >>> get_pre_clip_node_graph()
        {
            "success": True,
            "has_graph": True,
            "node_count": 2
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

        # GetPreClipNodeGraph()
        if layer_index is not None:
            graph = item.GetPreClipNodeGraph(layer_index)
        else:
            graph = item.GetPreClipNodeGraph()

        if graph:
            try:
                node_count = graph.GetNumNodes()
            except:
                node_count = None

            return {
                "success": True,
                "has_graph": True,
                "node_count": node_count,
                "graph": graph  # Actual graph object (for further operations)
            }
        else:
            return {
                "success": False,
                "has_graph": False,
                "message": "No pre-clip node graph available"
            }

    except Exception as e:
        logger.error(f"Error getting pre-clip node graph: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def get_post_clip_node_graph(
    track_type: str = "video",
    track_index: int = 1,
    item_index: Optional[int] = None,
    layer_index: Optional[int] = None
) -> Dict[str, Any]:
    """
    Get the post-clip node graph for a timeline item.

    Post-clip nodes are applied after clip-level color grading.
    Useful for final look adjustments, creative grades, etc.

    Args:
        track_type: Track type ("video" or "audio")
        track_index: Track number (1-based)
        item_index: Item index (uses current if None)
        layer_index: Layer index for Dolby Vision (optional)

    Returns:
        Node graph object information

    Example:
        >>> get_post_clip_node_graph()
        {
            "success": True,
            "has_graph": True,
            "node_count": 4
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

        # GetPostClipNodeGraph()
        if layer_index is not None:
            graph = item.GetPostClipNodeGraph(layer_index)
        else:
            graph = item.GetPostClipNodeGraph()

        if graph:
            try:
                node_count = graph.GetNumNodes()
            except:
                node_count = None

            return {
                "success": True,
                "has_graph": True,
                "node_count": node_count,
                "graph": graph  # Actual graph object (for further operations)
            }
        else:
            return {
                "success": False,
                "has_graph": False,
                "message": "No post-clip node graph available"
            }

    except Exception as e:
        logger.error(f"Error getting post-clip node graph: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# ============================================================================
# Tool Registration
# ============================================================================

def register_tools(mcp):
    """
    Register TimelineItem Advanced Features 2 tools with the MCP server.

    Args:
        mcp: FastMCP server instance

    Returns:
        Number of tools registered
    """
    from ..proxy import get_proxy

    proxy = get_proxy()

    # Register HIGH priority grade copying tool
    proxy.register_tool(
        "copy_grades_to_clips",
        copy_grades_to_clips,
        "color",
        "Copy color grades from a source clip to multiple target clips",
        {
            "source_track_type": {"type": "string", "description": "Source track type (video/audio)"},
            "source_track_index": {"type": "integer", "description": "Source track number (1-based)"},
            "source_item_index": {"type": "integer", "description": "Source item index (1-based)"},
            "target_track_type": {"type": "string", "description": "Target track type (video/audio)"},
            "target_track_index": {"type": "integer", "description": "Target track number (1-based)"},
            "target_item_indices": {"type": "array", "description": "List of target item indices (1-based)"}
        }
    )

    # Register HIGH priority LUT export tool
    proxy.register_tool(
        "export_lut",
        export_lut,
        "color",
        "Export a LUT from a timeline item's color grading",
        {
            "export_type": {"type": "string", "description": "LUT format (17pt, 33pt, 65pt, cdl)"},
            "path": {"type": "string", "description": "Destination file path"},
            "track_type": {"type": "string", "description": "Track type (video/audio)", "default": "video"},
            "track_index": {"type": "integer", "description": "Track number (1-based)", "default": 1},
            "item_index": {"type": "integer", "description": "Item index (uses current if None)", "optional": True}
        }
    )

    # Register HIGH priority node graph tools
    proxy.register_tool(
        "get_pre_clip_node_graph",
        get_pre_clip_node_graph,
        "color",
        "Get the pre-clip node graph (applied before clip-level grading)",
        {
            "track_type": {"type": "string", "description": "Track type (video/audio)", "default": "video"},
            "track_index": {"type": "integer", "description": "Track number (1-based)", "default": 1},
            "item_index": {"type": "integer", "description": "Item index (uses current if None)", "optional": True},
            "layer_index": {"type": "integer", "description": "Layer index for Dolby Vision", "optional": True}
        }
    )

    proxy.register_tool(
        "get_post_clip_node_graph",
        get_post_clip_node_graph,
        "color",
        "Get the post-clip node graph (applied after clip-level grading)",
        {
            "track_type": {"type": "string", "description": "Track type (video/audio)", "default": "video"},
            "track_index": {"type": "integer", "description": "Track number (1-based)", "default": 1},
            "item_index": {"type": "integer", "description": "Item index (uses current if None)", "optional": True},
            "layer_index": {"type": "integer", "description": "Layer index for Dolby Vision", "optional": True}
        }
    )

    logger.info("Registered 4 TimelineItem Advanced Features 2 tools")
    return 4


# For standalone testing
if __name__ == "__main__":
    print("TimelineItem Advanced Features 2 Tools - Testing")
    print("=" * 60)

    try:
        item = get_current_timeline_item()
        if item:
            print(f"\nCurrent item: {item.GetName()}")
        else:
            print("\nNo item at playhead")
    except Exception as e:
        print(f"Error: {e}")
