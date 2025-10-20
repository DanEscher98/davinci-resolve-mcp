"""
DaVinci Resolve MCP - Gallery Advanced Operations

Implements advanced Gallery API operations including:
- PowerGrade album management
- Direct still operations (bypass album-level)
- Color group clip retrieval

HIGH PRIORITY: Essential for advanced color grading and PowerGrade workflows
"""

from typing import Dict, Any, List, Optional
import json
import logging

logger = logging.getLogger("davinci-resolve-mcp.tools.gallery_advanced")

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


def get_gallery():
    """Helper to get Gallery object from current project."""
    project = get_current_project()
    if not project:
        raise ValueError("No project is currently open")

    gallery = project.GetGallery()
    if not gallery:
        raise ValueError("Could not access Gallery")

    return gallery


# ============================================================================
# PowerGrade Album Operations (HIGH PRIORITY)
# ============================================================================

def get_gallery_power_grade_albums() -> List[Dict[str, Any]]:
    """
    Get list of all PowerGrade albums in the Gallery.

    PowerGrades are complete node graph structures that can be applied
    to clips, containing multiple nodes, settings, and plugins.

    Returns:
        List of PowerGrade album information

    Example:
        >>> get_gallery_power_grade_albums()
        [
            {"index": 0, "label": "Hero Looks", "powergrade_count": 5},
            {"index": 1, "label": "Film Emulation", "powergrade_count": 12}
        ]
    """
    try:
        gallery = get_gallery()

        # GetGalleryPowerGradeAlbums()
        albums = gallery.GetGalleryPowerGradeAlbums()

        if not albums:
            return []

        result = []
        for idx, album in enumerate(albums):
            # Try to get PowerGrades in the album
            try:
                power_grades = album.GetPowerGrades() if hasattr(album, 'GetPowerGrades') else []
                pg_count = len(power_grades) if power_grades else 0
            except:
                pg_count = 0

            try:
                label = album.GetLabel()
            except:
                label = f"PowerGrade Album {idx + 1}"

            result.append({
                "index": idx,
                "label": label,
                "powergrade_count": pg_count
            })

        return result

    except Exception as e:
        logger.error(f"Error getting PowerGrade albums: {e}")
        return []


def get_album_name(album_index: int, album_type: str = "still") -> str:
    """
    Get the name/label of a Gallery album.

    Args:
        album_index: Index of the album (0-based)
        album_type: Type of album ("still" or "powergrade")

    Returns:
        Album name/label

    Example:
        >>> get_album_name(album_index=0, album_type="powergrade")
        "Hero Looks"
    """
    try:
        gallery = get_gallery()

        if album_type.lower() == "powergrade":
            albums = gallery.GetGalleryPowerGradeAlbums()
        else:
            albums = gallery.GetGalleryStillAlbums()

        if not albums or album_index < 0 or album_index >= len(albums):
            raise ValueError(f"Invalid album index {album_index}")

        album = albums[album_index]

        # GetAlbumName(galleryStillAlbum) - note this might be a Gallery method
        # or could be GetLabel() on the album object
        try:
            name = gallery.GetAlbumName(album)
        except:
            name = album.GetLabel()

        return name

    except Exception as e:
        logger.error(f"Error getting album name: {e}")
        return f"Album {album_index}"


# ============================================================================
# Direct Still Operations (HIGH PRIORITY)
# ============================================================================

def get_stills(album_index: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Get list of stills from Gallery (direct access, not album-specific).

    Args:
        album_index: Optional album index to filter by

    Returns:
        List of still information

    Example:
        >>> get_stills()
        [
            {"index": 0, "name": "Still 001", "album": "Stills 1"},
            {"index": 1, "name": "Still 002", "album": "Stills 1"}
        ]
    """
    try:
        gallery = get_gallery()

        if album_index is not None:
            # Get stills from specific album
            albums = gallery.GetGalleryStillAlbums()
            if not albums or album_index < 0 or album_index >= len(albums):
                return {
                    "success": False,
                    "error": f"Invalid album index {album_index}"
                }
            album = albums[album_index]
            stills = album.GetStills()
        else:
            # GetStills() - direct Gallery method
            stills = gallery.GetStills()

        if not stills:
            return []

        result = []
        for idx, still in enumerate(stills):
            if isinstance(still, dict):
                result.append({
                    "index": idx,
                    **still
                })
            else:
                # Try to extract information from still object
                try:
                    name = still.GetName() if hasattr(still, 'GetName') else f"Still {idx + 1:03d}"
                except:
                    name = f"Still {idx + 1:03d}"

                result.append({
                    "index": idx,
                    "name": name
                })

        return result

    except Exception as e:
        logger.error(f"Error getting stills: {e}")
        return []


def import_stills(file_paths: List[str]) -> Dict[str, Any]:
    """
    Import still images directly into Gallery.

    Args:
        file_paths: List of file paths to import (.dpx, .drx, .png, .jpg formats)

    Returns:
        Import result with count of imported stills

    Example:
        >>> import_stills([
        ...     "/stills/grade1.drx",
        ...     "/stills/grade2.drx"
        ... ])
        {
            "success": True,
            "imported_count": 2,
            "attempted_count": 2
        }
    """
    try:
        gallery = get_gallery()

        if not file_paths:
            return {
                "success": False,
                "error": "No file paths provided"
            }

        # ImportStills([filePaths])
        result = gallery.ImportStills(file_paths)

        if isinstance(result, bool):
            return {
                "success": result,
                "attempted_count": len(file_paths),
                "message": f"Import {'succeeded' if result else 'failed'}"
            }
        elif isinstance(result, int):
            return {
                "success": result > 0,
                "imported_count": result,
                "failed_count": len(file_paths) - result,
                "attempted_count": len(file_paths)
            }
        else:
            return {
                "success": True,
                "message": "Import completed",
                "result": result
            }

    except Exception as e:
        logger.error(f"Error importing stills: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def export_stills(
    still_indices: List[int],
    folder_path: str,
    file_prefix: str,
    format: str = "drx"
) -> Dict[str, Any]:
    """
    Export stills directly from Gallery.

    Args:
        still_indices: List of still indices to export (0-based)
        folder_path: Destination folder path
        file_prefix: Prefix for exported filenames
        format: Export format ("drx" or "dpx")

    Returns:
        Export result with count of exported stills

    Example:
        >>> export_stills(
        ...     still_indices=[0, 1, 2],
        ...     folder_path="/exports/stills",
        ...     file_prefix="look",
        ...     format="drx"
        ... )
        {
            "success": True,
            "exported_count": 3,
            "folder_path": "/exports/stills"
        }
    """
    try:
        gallery = get_gallery()

        if not still_indices:
            return {
                "success": False,
                "error": "No still indices provided"
            }

        # Validate format
        if format.lower() not in ["drx", "dpx"]:
            return {
                "success": False,
                "error": f"Invalid format '{format}'. Use 'drx' or 'dpx'"
            }

        # Get stills from Gallery
        all_stills = gallery.GetStills()
        if not all_stills:
            return {
                "success": False,
                "error": "No stills available in Gallery"
            }

        # Get specific stills by index
        stills_to_export = []
        for idx in still_indices:
            if 0 <= idx < len(all_stills):
                stills_to_export.append(all_stills[idx])

        if not stills_to_export:
            return {
                "success": False,
                "error": "No valid stills at specified indices"
            }

        # ExportStills([galleryStill], folderPath, filePrefix, format)
        result = gallery.ExportStills(stills_to_export, folder_path, file_prefix, format)

        if isinstance(result, bool):
            return {
                "success": result,
                "attempted_count": len(stills_to_export),
                "folder_path": folder_path,
                "message": f"Export {'succeeded' if result else 'failed'}"
            }
        elif isinstance(result, int):
            return {
                "success": result > 0,
                "exported_count": result,
                "failed_count": len(stills_to_export) - result,
                "folder_path": folder_path
            }
        else:
            return {
                "success": True,
                "message": "Export completed",
                "folder_path": folder_path,
                "result": result
            }

    except Exception as e:
        logger.error(f"Error exporting stills: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# ============================================================================
# Color Group Clip Retrieval (HIGH PRIORITY)
# ============================================================================

def get_clips_in_timeline_for_color_group(
    color_group_name: str,
    timeline_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get all clips in a specific timeline that belong to a color group.

    Args:
        color_group_name: Name of the color group
        timeline_name: Name of timeline (uses current if None)

    Returns:
        List of clips in the color group within the specified timeline

    Example:
        >>> get_clips_in_timeline_for_color_group(
        ...     color_group_name="Day Exteriors",
        ...     timeline_name="Main Timeline"
        ... )
        {
            "success": True,
            "color_group": "Day Exteriors",
            "timeline": "Main Timeline",
            "clip_count": 8,
            "clips": [...]
        }
    """
    try:
        project = get_current_project()

        # Get timeline
        if timeline_name:
            # Find timeline by name
            timeline_count = project.GetTimelineCount()
            timeline = None
            for i in range(1, timeline_count + 1):
                tl = project.GetTimelineByIndex(i)
                if tl and tl.GetName() == timeline_name:
                    timeline = tl
                    break

            if not timeline:
                return {
                    "success": False,
                    "error": f"Timeline '{timeline_name}' not found"
                }
        else:
            timeline = get_current_timeline()
            timeline_name = timeline.GetName() if timeline else "Unknown"

        if not timeline:
            return {
                "success": False,
                "error": "No timeline available"
            }

        # Get color group object
        color_groups_list = project.GetColorGroupsList()
        if not color_groups_list or color_group_name not in color_groups_list:
            return {
                "success": False,
                "error": f"Color group '{color_group_name}' not found"
            }

        # GetClipsInTimeline(Timeline) - called on ColorGroup object
        # Note: We need to get the actual ColorGroup object, not just the name
        # This is simplified - actual implementation may need to iterate to find the object

        clips_in_group = []

        # Iterate through timeline tracks to find clips in this color group
        track_count = timeline.GetTrackCount("video")
        for track_idx in range(1, track_count + 1):
            items = timeline.GetItemListInTrack("video", track_idx)
            if items:
                for item in items:
                    try:
                        # Check if item belongs to the color group
                        color_group = item.GetColorGroup()
                        if color_group:
                            group_name = color_group.GetName()
                            if group_name == color_group_name:
                                clips_in_group.append({
                                    "name": item.GetName(),
                                    "track": track_idx,
                                    "start": item.GetStart(),
                                    "end": item.GetEnd()
                                })
                    except:
                        continue

        return {
            "success": True,
            "color_group": color_group_name,
            "timeline": timeline_name,
            "clip_count": len(clips_in_group),
            "clips": clips_in_group
        }

    except Exception as e:
        logger.error(f"Error getting clips in timeline for color group: {e}")
        return {
            "success": False,
            "error": str(e),
            "color_group": color_group_name
        }


# ============================================================================
# Tool Registration
# ============================================================================

def register_tools(mcp):
    """
    Register Gallery Advanced Operations tools with the MCP server.

    Args:
        mcp: FastMCP server instance

    Returns:
        Number of tools registered
    """
    from ..proxy import get_proxy

    proxy = get_proxy()

    # Register HIGH priority PowerGrade tools
    proxy.register_tool(
        "get_gallery_power_grade_albums",
        get_gallery_power_grade_albums,
        "gallery",
        "Get list of all PowerGrade albums in the Gallery",
        {}
    )

    proxy.register_tool(
        "get_album_name",
        get_album_name,
        "gallery",
        "Get the name/label of a Gallery album (still or PowerGrade)",
        {
            "album_index": {"type": "integer", "description": "Index of the album (0-based)"},
            "album_type": {"type": "string", "description": "Type of album (still or powergrade)", "default": "still"}
        }
    )

    # Register HIGH priority direct still operations
    proxy.register_tool(
        "get_stills",
        get_stills,
        "gallery",
        "Get list of stills from Gallery (direct access)",
        {"album_index": {"type": "integer", "description": "Optional album index to filter by", "optional": True}}
    )

    proxy.register_tool(
        "import_stills",
        import_stills,
        "gallery",
        "Import still images directly into Gallery (.dpx, .drx, .png, .jpg)",
        {"file_paths": {"type": "array", "description": "List of file paths to import"}}
    )

    proxy.register_tool(
        "export_stills",
        export_stills,
        "gallery",
        "Export stills directly from Gallery",
        {
            "still_indices": {"type": "array", "description": "List of still indices to export (0-based)"},
            "folder_path": {"type": "string", "description": "Destination folder path"},
            "file_prefix": {"type": "string", "description": "Prefix for exported filenames"},
            "format": {"type": "string", "description": "Export format (drx or dpx)", "default": "drx"}
        }
    )

    # Register HIGH priority color group clip retrieval
    proxy.register_tool(
        "get_clips_in_timeline_for_color_group",
        get_clips_in_timeline_for_color_group,
        "color",
        "Get all clips in a timeline that belong to a color group",
        {
            "color_group_name": {"type": "string", "description": "Name of the color group"},
            "timeline_name": {"type": "string", "description": "Name of timeline (uses current if None)", "optional": True}
        }
    )

    logger.info("Registered 6 Gallery Advanced Operations tools")
    return 6


# For standalone testing
if __name__ == "__main__":
    print("Gallery Advanced Operations Tools - Testing")
    print("=" * 60)

    try:
        powergrade_albums = get_gallery_power_grade_albums()
        print(f"\nPowerGrade Albums ({len(powergrade_albums)}):")
        for album in powergrade_albums:
            print(f"  - {album['label']}: {album['powergrade_count']} PowerGrades")
    except Exception as e:
        print(f"Error: {e}")
