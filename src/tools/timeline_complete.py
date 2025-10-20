"""
DaVinci Resolve MCP - Timeline Complete

Implements ALL remaining Timeline API operations for 100% coverage.

Includes:
- Timecode operations (set start timecode, set current timecode)
- Clip manipulation (delete with ripple, link/unlink clips)
- Timeline duplication and compound clips
- Generator and title insertion
- Still grabbing (batch operations)
- Track information and node graph access

HIGH PRIORITY: Essential for advanced timeline editing workflows
"""

from typing import Dict, Any, List, Optional
import json
import logging

logger = logging.getLogger("davinci-resolve-mcp.tools.timeline_complete")

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
# Timecode Operations (HIGH PRIORITY)
# ============================================================================

def set_start_timecode(timecode: str) -> Dict[str, Any]:
    """
    Set the start timecode for the timeline.

    Args:
        timecode: Start timecode (format: "HH:MM:SS:FF")

    Returns:
        Set result

    Example:
        >>> set_start_timecode("01:00:00:00")
        {
            "success": True,
            "timecode": "01:00:00:00",
            "message": "Start timecode set"
        }
    """
    try:
        timeline = get_current_timeline()

        # SetStartTimecode(timecode)
        result = timeline.SetStartTimecode(timecode)

        return {
            "success": bool(result),
            "timecode": timecode,
            "message": f"Start timecode {'set' if result else 'set failed'}"
        }

    except Exception as e:
        logger.error(f"Error setting start timecode: {e}")
        return {
            "success": False,
            "error": str(e),
            "timecode": timecode
        }


def set_current_timecode(timecode: str) -> Dict[str, Any]:
    """
    Set the playhead position by timecode.

    Args:
        timecode: Target timecode (format: "HH:MM:SS:FF")

    Returns:
        Set result

    Example:
        >>> set_current_timecode("01:00:15:10")
        {
            "success": True,
            "timecode": "01:00:15:10",
            "message": "Playhead moved"
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


# ============================================================================
# Clip Manipulation Operations (HIGH PRIORITY)
# ============================================================================

def duplicate_timeline(timeline_name: str) -> Dict[str, Any]:
    """
    Duplicate the current timeline with a new name.

    Args:
        timeline_name: Name for the duplicated timeline

    Returns:
        Duplication result with new timeline info

    Example:
        >>> duplicate_timeline("Main Timeline - Copy")
        {
            "success": True,
            "timeline_name": "Main Timeline - Copy",
            "message": "Timeline duplicated"
        }
    """
    try:
        timeline = get_current_timeline()

        # DuplicateTimeline(timelineName)
        new_timeline = timeline.DuplicateTimeline(timeline_name)

        if new_timeline:
            return {
                "success": True,
                "timeline_name": timeline_name,
                "message": "Timeline duplicated successfully"
            }
        else:
            return {
                "success": False,
                "timeline_name": timeline_name,
                "message": "Timeline duplication failed"
            }

    except Exception as e:
        logger.error(f"Error duplicating timeline: {e}")
        return {
            "success": False,
            "error": str(e),
            "timeline_name": timeline_name
        }


def create_fusion_clip(
    track_type: str,
    track_index: int,
    item_indices: List[int]
) -> Dict[str, Any]:
    """
    Create a Fusion clip from timeline items.

    Args:
        track_type: Track type ("video" or "audio")
        track_index: Track number (1-based)
        item_indices: List of item indices to include (1-based)

    Returns:
        Fusion clip creation result

    Example:
        >>> create_fusion_clip("video", 1, [1, 2, 3])
        {
            "success": True,
            "item_count": 3,
            "message": "Fusion clip created"
        }
    """
    try:
        timeline = get_current_timeline()

        # Get timeline items
        all_items = timeline.GetItemListInTrack(track_type, track_index)
        if not all_items:
            return {
                "success": False,
                "error": f"No items in track {track_index}"
            }

        items_to_convert = []
        for idx in item_indices:
            if 1 <= idx <= len(all_items):
                items_to_convert.append(all_items[idx - 1])

        if not items_to_convert:
            return {
                "success": False,
                "error": "No valid items found at specified indices"
            }

        # CreateFusionClip([timelineItems])
        result = timeline.CreateFusionClip(items_to_convert)

        return {
            "success": bool(result),
            "item_count": len(items_to_convert),
            "message": f"Fusion clip {'created from' if result else 'creation failed for'} {len(items_to_convert)} items"
        }

    except Exception as e:
        logger.error(f"Error creating Fusion clip: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# ============================================================================
# Generator and Title Insertion (MEDIUM PRIORITY)
# ============================================================================

def insert_generator_into_timeline(generator_name: str) -> Dict[str, Any]:
    """
    Insert a generator at the playhead position.

    Args:
        generator_name: Name of the generator to insert

    Returns:
        Insertion result

    Example:
        >>> insert_generator_into_timeline("Solid Color")
        {
            "success": True,
            "generator_name": "Solid Color",
            "message": "Generator inserted"
        }
    """
    try:
        timeline = get_current_timeline()

        # InsertGeneratorIntoTimeline(generatorName)
        result = timeline.InsertGeneratorIntoTimeline(generator_name)

        return {
            "success": bool(result),
            "generator_name": generator_name,
            "message": f"Generator {'inserted' if result else 'insertion failed'}"
        }

    except Exception as e:
        logger.error(f"Error inserting generator: {e}")
        return {
            "success": False,
            "error": str(e),
            "generator_name": generator_name
        }


def insert_fusion_generator_into_timeline(generator_name: str) -> Dict[str, Any]:
    """
    Insert a Fusion generator at the playhead position.

    Args:
        generator_name: Name of the Fusion generator to insert

    Returns:
        Insertion result

    Example:
        >>> insert_fusion_generator_into_timeline("3D Text")
        {
            "success": True,
            "generator_name": "3D Text",
            "message": "Fusion generator inserted"
        }
    """
    try:
        timeline = get_current_timeline()

        # InsertFusionGeneratorIntoTimeline(generatorName)
        result = timeline.InsertFusionGeneratorIntoTimeline(generator_name)

        return {
            "success": bool(result),
            "generator_name": generator_name,
            "message": f"Fusion generator {'inserted' if result else 'insertion failed'}"
        }

    except Exception as e:
        logger.error(f"Error inserting Fusion generator: {e}")
        return {
            "success": False,
            "error": str(e),
            "generator_name": generator_name
        }


def insert_title_into_timeline(title_name: str) -> Dict[str, Any]:
    """
    Insert a title at the playhead position.

    Args:
        title_name: Name of the title to insert

    Returns:
        Insertion result

    Example:
        >>> insert_title_into_timeline("Basic Title")
        {
            "success": True,
            "title_name": "Basic Title",
            "message": "Title inserted"
        }
    """
    try:
        timeline = get_current_timeline()

        # InsertTitleIntoTimeline(titleName)
        result = timeline.InsertTitleIntoTimeline(title_name)

        return {
            "success": bool(result),
            "title_name": title_name,
            "message": f"Title {'inserted' if result else 'insertion failed'}"
        }

    except Exception as e:
        logger.error(f"Error inserting title: {e}")
        return {
            "success": False,
            "error": str(e),
            "title_name": title_name
        }


def insert_fusion_title_into_timeline(title_name: str) -> Dict[str, Any]:
    """
    Insert a Fusion title at the playhead position.

    Args:
        title_name: Name of the Fusion title to insert

    Returns:
        Insertion result

    Example:
        >>> insert_fusion_title_into_timeline("Lower Third")
        {
            "success": True,
            "title_name": "Lower Third",
            "message": "Fusion title inserted"
        }
    """
    try:
        timeline = get_current_timeline()

        # InsertFusionTitleIntoTimeline(titleName)
        result = timeline.InsertFusionTitleIntoTimeline(title_name)

        return {
            "success": bool(result),
            "title_name": title_name,
            "message": f"Fusion title {'inserted' if result else 'insertion failed'}"
        }

    except Exception as e:
        logger.error(f"Error inserting Fusion title: {e}")
        return {
            "success": False,
            "error": str(e),
            "title_name": title_name
        }


def insert_ofx_generator_into_timeline(generator_name: str) -> Dict[str, Any]:
    """
    Insert an OFX generator at the playhead position.

    Args:
        generator_name: Name of the OFX generator to insert

    Returns:
        Insertion result

    Example:
        >>> insert_ofx_generator_into_timeline("Sapphire Gradient")
        {
            "success": True,
            "generator_name": "Sapphire Gradient",
            "message": "OFX generator inserted"
        }
    """
    try:
        timeline = get_current_timeline()

        # InsertOFXGeneratorIntoTimeline(generatorName)
        result = timeline.InsertOFXGeneratorIntoTimeline(generator_name)

        return {
            "success": bool(result),
            "generator_name": generator_name,
            "message": f"OFX generator {'inserted' if result else 'insertion failed'}"
        }

    except Exception as e:
        logger.error(f"Error inserting OFX generator: {e}")
        return {
            "success": False,
            "error": str(e),
            "generator_name": generator_name
        }


def insert_fusion_composition_into_timeline() -> Dict[str, Any]:
    """
    Insert a new Fusion composition at the playhead position.

    Returns:
        Insertion result

    Example:
        >>> insert_fusion_composition_into_timeline()
        {
            "success": True,
            "message": "Fusion composition inserted"
        }
    """
    try:
        timeline = get_current_timeline()

        # InsertFusionCompositionIntoTimeline()
        result = timeline.InsertFusionCompositionIntoTimeline()

        return {
            "success": bool(result),
            "message": f"Fusion composition {'inserted' if result else 'insertion failed'}"
        }

    except Exception as e:
        logger.error(f"Error inserting Fusion composition: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# ============================================================================
# Still Grabbing Operations (MEDIUM PRIORITY)
# ============================================================================

def grab_all_stills(still_frame_source: int = 1) -> Dict[str, Any]:
    """
    Grab stills from all clips in the timeline.

    Args:
        still_frame_source: Source for still frames:
            - 1: First frame
            - 2: Middle frame
            - 3: Last frame

    Returns:
        Grab result with count of stills grabbed

    Example:
        >>> grab_all_stills(still_frame_source=2)
        {
            "success": True,
            "still_frame_source": 2,
            "message": "Stills grabbed from all clips"
        }
    """
    try:
        timeline = get_current_timeline()

        # GrabAllStills(stillFrameSource)
        result = timeline.GrabAllStills(still_frame_source)

        if isinstance(result, int):
            return {
                "success": True,
                "still_count": result,
                "still_frame_source": still_frame_source,
                "message": f"{result} stills grabbed"
            }
        else:
            return {
                "success": bool(result),
                "still_frame_source": still_frame_source,
                "message": f"Stills {'grabbed from all clips' if result else 'grab failed'}"
            }

    except Exception as e:
        logger.error(f"Error grabbing all stills: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# ============================================================================
# Track Information (MEDIUM PRIORITY)
# ============================================================================

def get_track_sub_type(track_type: str, track_index: int) -> str:
    """
    Get the sub-type of an audio track (e.g., "Mono", "Stereo", "5.1").

    Args:
        track_type: Track type ("audio" only)
        track_index: Track number (1-based)

    Returns:
        Track sub-type string

    Example:
        >>> get_track_sub_type("audio", 1)
        "Stereo"
    """
    try:
        timeline = get_current_timeline()

        # GetTrackSubType(trackType, trackIndex)
        sub_type = timeline.GetTrackSubType(track_type, track_index)

        return sub_type if sub_type else "Unknown"

    except Exception as e:
        logger.error(f"Error getting track sub-type: {e}")
        return "Error"


# ============================================================================
# Node Graph and Media Pool Item Access (MEDIUM PRIORITY)
# ============================================================================

def get_timeline_node_graph() -> Dict[str, Any]:
    """
    Get the timeline-level node graph.

    Returns:
        Node graph object information

    Example:
        >>> get_timeline_node_graph()
        {
            "success": True,
            "has_graph": True,
            "node_count": 3
        }
    """
    try:
        timeline = get_current_timeline()

        # GetNodeGraph()
        graph = timeline.GetNodeGraph()

        if graph:
            try:
                node_count = graph.GetNumNodes()
            except:
                node_count = None

            return {
                "success": True,
                "has_graph": True,
                "node_count": node_count,
                "graph": graph  # Actual graph object
            }
        else:
            return {
                "success": False,
                "has_graph": False,
                "message": "No timeline node graph available"
            }

    except Exception as e:
        logger.error(f"Error getting timeline node graph: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def get_timeline_media_pool_item() -> Dict[str, Any]:
    """
    Get the MediaPoolItem associated with the timeline.

    For timelines that were imported or created from a single source.

    Returns:
        MediaPoolItem information

    Example:
        >>> get_timeline_media_pool_item()
        {
            "success": True,
            "has_item": True,
            "item_name": "Interview A"
        }
    """
    try:
        timeline = get_current_timeline()

        # GetMediaPoolItem()
        item = timeline.GetMediaPoolItem()

        if item:
            try:
                item_name = item.GetName()
            except:
                item_name = None

            return {
                "success": True,
                "has_item": True,
                "item_name": item_name,
                "item": item  # Actual MediaPoolItem object
            }
        else:
            return {
                "success": False,
                "has_item": False,
                "message": "No MediaPoolItem associated with timeline"
            }

    except Exception as e:
        logger.error(f"Error getting timeline MediaPoolItem: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# ============================================================================
# Compound Clip and Clip Manipulation (HIGH PRIORITY)
# ============================================================================

def create_compound_clip(
    track_type: str,
    track_index: int,
    item_indices: List[int],
    clip_info: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a compound clip from timeline items.

    Args:
        track_type: Track type ("video" or "audio")
        track_index: Track number (1-based)
        item_indices: List of item indices to include (1-based)
        clip_info: Optional clip information dictionary

    Returns:
        Compound clip creation result

    Example:
        >>> create_compound_clip("video", 1, [1, 2, 3], {"name": "Compound 1"})
        {
            "success": True,
            "item_count": 3,
            "message": "Compound clip created"
        }
    """
    try:
        timeline = get_current_timeline()

        # Get timeline items
        all_items = timeline.GetItemListInTrack(track_type, track_index)
        if not all_items:
            return {
                "success": False,
                "error": f"No items in track {track_index}"
            }

        items_to_compound = []
        for idx in item_indices:
            if 1 <= idx <= len(all_items):
                items_to_compound.append(all_items[idx - 1])

        if not items_to_compound:
            return {
                "success": False,
                "error": "No valid items found at specified indices"
            }

        clip_info = clip_info or {}

        # CreateCompoundClip([timelineItems], {clipInfo})
        result = timeline.CreateCompoundClip(items_to_compound, clip_info)

        return {
            "success": bool(result),
            "item_count": len(items_to_compound),
            "message": f"Compound clip {'created from' if result else 'creation failed for'} {len(items_to_compound)} items"
        }

    except Exception as e:
        logger.error(f"Error creating compound clip: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def delete_clips_with_ripple(
    track_type: str,
    track_index: int,
    item_indices: List[int],
    ripple: bool = True
) -> Dict[str, Any]:
    """
    Delete clips from timeline with optional ripple delete.

    Args:
        track_type: Track type ("video" or "audio")
        track_index: Track number (1-based)
        item_indices: List of item indices to delete (1-based)
        ripple: True for ripple delete (close gaps), False to leave gaps

    Returns:
        Delete result

    Example:
        >>> delete_clips_with_ripple("video", 1, [2, 3], ripple=True)
        {
            "success": True,
            "deleted_count": 2,
            "ripple": True,
            "message": "2 clips deleted with ripple"
        }
    """
    try:
        timeline = get_current_timeline()

        # Get timeline items
        all_items = timeline.GetItemListInTrack(track_type, track_index)
        if not all_items:
            return {
                "success": False,
                "error": f"No items in track {track_index}"
            }

        items_to_delete = []
        for idx in item_indices:
            if 1 <= idx <= len(all_items):
                items_to_delete.append(all_items[idx - 1])

        if not items_to_delete:
            return {
                "success": False,
                "error": "No valid items found at specified indices"
            }

        # DeleteClips([timelineItems], Bool)
        result = timeline.DeleteClips(items_to_delete, ripple)

        return {
            "success": bool(result),
            "deleted_count": len(items_to_delete) if result else 0,
            "ripple": ripple,
            "message": f"{'Deleted' if result else 'Delete failed for'} {len(items_to_delete)} clips {'with ripple' if ripple else 'leaving gaps'}"
        }

    except Exception as e:
        logger.error(f"Error deleting clips: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def set_clips_linked(
    track_type: str,
    track_index: int,
    item_indices: List[int],
    linked: bool = True
) -> Dict[str, Any]:
    """
    Link or unlink clips in the timeline.

    Args:
        track_type: Track type ("video" or "audio")
        track_index: Track number (1-based)
        item_indices: List of item indices (1-based)
        linked: True to link clips, False to unlink

    Returns:
        Link/unlink result

    Example:
        >>> set_clips_linked("video", 1, [1, 2, 3], linked=True)
        {
            "success": True,
            "clip_count": 3,
            "linked": True,
            "message": "3 clips linked"
        }
    """
    try:
        timeline = get_current_timeline()

        # Get timeline items
        all_items = timeline.GetItemListInTrack(track_type, track_index)
        if not all_items:
            return {
                "success": False,
                "error": f"No items in track {track_index}"
            }

        items_to_link = []
        for idx in item_indices:
            if 1 <= idx <= len(all_items):
                items_to_link.append(all_items[idx - 1])

        if not items_to_link:
            return {
                "success": False,
                "error": "No valid items found at specified indices"
            }

        # SetClipsLinked([timelineItems], Bool)
        result = timeline.SetClipsLinked(items_to_link, linked)

        return {
            "success": bool(result),
            "clip_count": len(items_to_link) if result else 0,
            "linked": linked,
            "message": f"{len(items_to_link)} clips {'linked' if linked else 'unlinked'}" if result else "Operation failed"
        }

    except Exception as e:
        logger.error(f"Error setting clips linked: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# ============================================================================
# Tool Registration
# ============================================================================

def register_tools(mcp):
    """
    Register Timeline Complete tools with the MCP server.

    Args:
        mcp: FastMCP server instance

    Returns:
        Number of tools registered
    """
    from ..proxy import get_proxy

    proxy = get_proxy()

    # Register HIGH priority timecode tools
    proxy.register_tool(
        "set_start_timecode",
        set_start_timecode,
        "timeline",
        "Set the start timecode for the timeline",
        {"timecode": {"type": "string", "description": "Start timecode (HH:MM:SS:FF)"}}
    )

    proxy.register_tool(
        "set_current_timecode",
        set_current_timecode,
        "timeline",
        "Set the playhead position by timecode",
        {"timecode": {"type": "string", "description": "Target timecode (HH:MM:SS:FF)"}}
    )

    # Register HIGH priority timeline manipulation tools
    proxy.register_tool(
        "duplicate_timeline",
        duplicate_timeline,
        "timeline",
        "Duplicate the current timeline with a new name",
        {"timeline_name": {"type": "string", "description": "Name for the duplicated timeline"}}
    )

    proxy.register_tool(
        "create_fusion_clip",
        create_fusion_clip,
        "timeline",
        "Create a Fusion clip from timeline items",
        {
            "track_type": {"type": "string", "description": "Track type (video/audio)"},
            "track_index": {"type": "integer", "description": "Track number (1-based)"},
            "item_indices": {"type": "array", "description": "List of item indices to include (1-based)"}
        }
    )

    # Register MEDIUM priority generator/title insertion tools
    proxy.register_tool(
        "insert_generator_into_timeline",
        insert_generator_into_timeline,
        "timeline",
        "Insert a generator at the playhead position",
        {"generator_name": {"type": "string", "description": "Name of the generator to insert"}}
    )

    proxy.register_tool(
        "insert_fusion_generator_into_timeline",
        insert_fusion_generator_into_timeline,
        "timeline",
        "Insert a Fusion generator at the playhead position",
        {"generator_name": {"type": "string", "description": "Name of the Fusion generator"}}
    )

    proxy.register_tool(
        "insert_title_into_timeline",
        insert_title_into_timeline,
        "timeline",
        "Insert a title at the playhead position",
        {"title_name": {"type": "string", "description": "Name of the title to insert"}}
    )

    proxy.register_tool(
        "insert_fusion_title_into_timeline",
        insert_fusion_title_into_timeline,
        "timeline",
        "Insert a Fusion title at the playhead position",
        {"title_name": {"type": "string", "description": "Name of the Fusion title"}}
    )

    proxy.register_tool(
        "insert_ofx_generator_into_timeline",
        insert_ofx_generator_into_timeline,
        "timeline",
        "Insert an OFX generator at the playhead position",
        {"generator_name": {"type": "string", "description": "Name of the OFX generator"}}
    )

    proxy.register_tool(
        "insert_fusion_composition_into_timeline",
        insert_fusion_composition_into_timeline,
        "timeline",
        "Insert a new Fusion composition at the playhead position",
        {}
    )

    # Register MEDIUM priority still grabbing tool
    proxy.register_tool(
        "grab_all_stills",
        grab_all_stills,
        "gallery",
        "Grab stills from all clips in the timeline",
        {"still_frame_source": {"type": "integer", "description": "Source for stills (1=first, 2=middle, 3=last)", "default": 1}}
    )

    # Register MEDIUM priority track/graph tools
    proxy.register_tool(
        "get_track_sub_type",
        get_track_sub_type,
        "timeline",
        "Get the sub-type of an audio track (Mono, Stereo, 5.1, etc.)",
        {
            "track_type": {"type": "string", "description": "Track type (audio only)"},
            "track_index": {"type": "integer", "description": "Track number (1-based)"}
        }
    )

    proxy.register_tool(
        "get_timeline_node_graph",
        get_timeline_node_graph,
        "color",
        "Get the timeline-level node graph",
        {}
    )

    proxy.register_tool(
        "get_timeline_media_pool_item",
        get_timeline_media_pool_item,
        "timeline",
        "Get the MediaPoolItem associated with the timeline",
        {}
    )

    # Register HIGH priority compound clip and clip manipulation tools
    proxy.register_tool(
        "create_compound_clip",
        create_compound_clip,
        "timeline",
        "Create a compound clip from timeline items",
        {
            "track_type": {"type": "string", "description": "Track type (video/audio)"},
            "track_index": {"type": "integer", "description": "Track number (1-based)"},
            "item_indices": {"type": "array", "description": "List of item indices to include (1-based)"},
            "clip_info": {"type": "object", "description": "Optional clip information", "optional": True}
        }
    )

    proxy.register_tool(
        "delete_clips_with_ripple",
        delete_clips_with_ripple,
        "timeline",
        "Delete clips from timeline with optional ripple delete",
        {
            "track_type": {"type": "string", "description": "Track type (video/audio)"},
            "track_index": {"type": "integer", "description": "Track number (1-based)"},
            "item_indices": {"type": "array", "description": "List of item indices to delete (1-based)"},
            "ripple": {"type": "boolean", "description": "True for ripple delete, False to leave gaps", "default": True}
        }
    )

    proxy.register_tool(
        "set_clips_linked",
        set_clips_linked,
        "timeline",
        "Link or unlink clips in the timeline",
        {
            "track_type": {"type": "string", "description": "Track type (video/audio)"},
            "track_index": {"type": "integer", "description": "Track number (1-based)"},
            "item_indices": {"type": "array", "description": "List of item indices (1-based)"},
            "linked": {"type": "boolean", "description": "True to link, False to unlink", "default": True}
        }
    )

    logger.info("Registered 17 Timeline Complete tools (Phase 6)")
    return 17


# For standalone testing
if __name__ == "__main__":
    print("Timeline Complete Tools - Testing")
    print("=" * 60)

    try:
        timeline = get_current_timeline()
        if timeline:
            print(f"\nTimeline: {timeline.GetName()}")
            timecode = timeline.GetCurrentTimecode()
            print(f"Current timecode: {timecode}")
        else:
            print("\nNo timeline active")
    except Exception as e:
        print(f"Error: {e}")
