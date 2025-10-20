"""
DaVinci Resolve MCP - GalleryStillAlbum Complete

Implements ALL GalleryStillAlbum API operations for 100% coverage.

Includes:
- Still management (get, import, export, delete)
- Still labeling

HIGH PRIORITY: Essential for Gallery and still management workflows
"""

from typing import Dict, Any, List
import logging

logger = logging.getLogger("davinci-resolve-mcp.tools.gallerystillalbum_complete")

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
    """Helper to get Gallery object."""
    project = get_current_project()
    if not project:
        raise ValueError("No project is currently open")

    gallery = project.GetGallery()
    if not gallery:
        raise ValueError("Could not access Gallery")

    return gallery


def _get_album_by_index(album_index: int, album_type: str = "still"):
    """Helper to get album by index."""
    gallery = get_gallery()

    if album_type.lower() == "powergrade":
        albums = gallery.GetGalleryPowerGradeAlbums()
    else:
        albums = gallery.GetGalleryStillAlbums()

    if not albums or album_index < 0 or album_index >= len(albums):
        raise ValueError(f"Invalid album index {album_index}")

    return albums[album_index]


# ============================================================================
# Still Management (HIGH PRIORITY)
# ============================================================================

def get_stills_in_album(album_index: int) -> List[Dict[str, Any]]:
    """
    Get list of stills in a still album.

    Args:
        album_index: Index of the still album (0-based)

    Returns:
        List of still information

    Example:
        >>> get_stills_in_album(0)
        [
            {"index": 0, "label": "Still 001"},
            {"index": 1, "label": "Hero Grade"}
        ]
    """
    try:
        album = _get_album_by_index(album_index, "still")

        # GetStills()
        stills = album.GetStills()

        if not stills:
            return []

        result = []
        for idx, still in enumerate(stills):
            # Try to get label
            try:
                label = album.GetLabel(still) if hasattr(album, 'GetLabel') else f"Still {idx + 1:03d}"
            except:
                label = f"Still {idx + 1:03d}"

            result.append({
                "index": idx,
                "label": label
            })

        return result

    except Exception as e:
        logger.error(f"Error getting stills in album: {e}")
        return []


def get_still_label(album_index: int, still_index: int) -> str:
    """
    Get the label of a still in an album.

    Args:
        album_index: Index of the still album (0-based)
        still_index: Index of the still (0-based)

    Returns:
        Still label

    Example:
        >>> get_still_label(0, 2)
        "Hero Grade"
    """
    try:
        album = _get_album_by_index(album_index, "still")
        stills = album.GetStills()

        if not stills or still_index < 0 or still_index >= len(stills):
            return "Invalid Index"

        still = stills[still_index]

        # GetLabel(galleryStill)
        label = album.GetLabel(still)

        return label if label else f"Still {still_index + 1:03d}"

    except Exception as e:
        logger.error(f"Error getting still label: {e}")
        return "Error"


def set_still_label(album_index: int, still_index: int, label: str) -> Dict[str, Any]:
    """
    Set the label of a still in an album.

    Args:
        album_index: Index of the still album (0-based)
        still_index: Index of the still (0-based)
        label: New label for the still

    Returns:
        Set result

    Example:
        >>> set_still_label(0, 2, "Hero Grade")
        {
            "success": True,
            "label": "Hero Grade",
            "message": "Still label set"
        }
    """
    try:
        album = _get_album_by_index(album_index, "still")
        stills = album.GetStills()

        if not stills or still_index < 0 or still_index >= len(stills):
            return {
                "success": False,
                "error": f"Invalid still index {still_index}"
            }

        still = stills[still_index]

        # SetLabel(galleryStill, label)
        result = album.SetLabel(still, label)

        return {
            "success": bool(result),
            "label": label,
            "message": f"Still label {'set' if result else 'set failed'}"
        }

    except Exception as e:
        logger.error(f"Error setting still label: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def import_stills_to_album(album_index: int, file_paths: List[str]) -> Dict[str, Any]:
    """
    Import still images into an album.

    Args:
        album_index: Index of the still album (0-based)
        file_paths: List of file paths to import (.dpx, .drx, .png, .jpg)

    Returns:
        Import result

    Example:
        >>> import_stills_to_album(0, ["/stills/grade1.drx", "/stills/grade2.drx"])
        {
            "success": True,
            "imported_count": 2,
            "attempted_count": 2
        }
    """
    try:
        album = _get_album_by_index(album_index, "still")

        if not file_paths:
            return {
                "success": False,
                "error": "No file paths provided"
            }

        # ImportStills([filePaths])
        result = album.ImportStills(file_paths)

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
        logger.error(f"Error importing stills to album: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def export_stills_from_album(
    album_index: int,
    still_indices: List[int],
    folder_path: str,
    file_prefix: str,
    format: str = "drx"
) -> Dict[str, Any]:
    """
    Export stills from an album.

    Args:
        album_index: Index of the still album (0-based)
        still_indices: List of still indices to export (0-based)
        folder_path: Destination folder path
        file_prefix: Prefix for exported filenames
        format: Export format ("drx" or "dpx")

    Returns:
        Export result

    Example:
        >>> export_stills_from_album(0, [0, 1, 2], "/exports/", "look", "drx")
        {
            "success": True,
            "exported_count": 3,
            "folder_path": "/exports/"
        }
    """
    try:
        album = _get_album_by_index(album_index, "still")

        if not still_indices:
            return {
                "success": False,
                "error": "No still indices provided"
            }

        if format.lower() not in ["drx", "dpx"]:
            return {
                "success": False,
                "error": f"Invalid format '{format}'. Use 'drx' or 'dpx'"
            }

        # Get stills from album
        all_stills = album.GetStills()
        if not all_stills:
            return {
                "success": False,
                "error": "No stills available in album"
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
        result = album.ExportStills(stills_to_export, folder_path, file_prefix, format)

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
        logger.error(f"Error exporting stills from album: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def delete_stills_from_album(album_index: int, still_indices: List[int]) -> Dict[str, Any]:
    """
    Delete stills from an album.

    Args:
        album_index: Index of the still album (0-based)
        still_indices: List of still indices to delete (0-based)

    Returns:
        Delete result

    Example:
        >>> delete_stills_from_album(0, [0, 1])
        {
            "success": True,
            "deleted_count": 2,
            "message": "Stills deleted"
        }
    """
    try:
        album = _get_album_by_index(album_index, "still")

        if not still_indices:
            return {
                "success": False,
                "error": "No still indices provided"
            }

        # Get stills from album
        all_stills = album.GetStills()
        if not all_stills:
            return {
                "success": False,
                "error": "No stills available in album"
            }

        # Get specific stills by index
        stills_to_delete = []
        for idx in still_indices:
            if 0 <= idx < len(all_stills):
                stills_to_delete.append(all_stills[idx])

        if not stills_to_delete:
            return {
                "success": False,
                "error": "No valid stills at specified indices"
            }

        # DeleteStills([galleryStill])
        result = album.DeleteStills(stills_to_delete)

        return {
            "success": bool(result),
            "deleted_count": len(stills_to_delete) if result else 0,
            "message": f"{'Deleted' if result else 'Delete failed for'} {len(stills_to_delete)} stills"
        }

    except Exception as e:
        logger.error(f"Error deleting stills: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# ============================================================================
# Tool Registration
# ============================================================================

def register_tools(mcp):
    """
    Register GalleryStillAlbum Complete tools with the MCP server.

    Args:
        mcp: FastMCP server instance

    Returns:
        Number of tools registered
    """
    from ..proxy import get_proxy

    proxy = get_proxy()

    # Register HIGH priority still management tools
    proxy.register_tool(
        "get_stills_in_album",
        get_stills_in_album,
        "gallery",
        "Get list of stills in a still album",
        {"album_index": {"type": "integer", "description": "Index of the still album (0-based)"}}
    )

    proxy.register_tool(
        "get_still_label",
        get_still_label,
        "gallery",
        "Get the label of a still in an album",
        {
            "album_index": {"type": "integer", "description": "Index of the still album (0-based)"},
            "still_index": {"type": "integer", "description": "Index of the still (0-based)"}
        }
    )

    proxy.register_tool(
        "set_still_label",
        set_still_label,
        "gallery",
        "Set the label of a still in an album",
        {
            "album_index": {"type": "integer", "description": "Index of the still album (0-based)"},
            "still_index": {"type": "integer", "description": "Index of the still (0-based)"},
            "label": {"type": "string", "description": "New label for the still"}
        }
    )

    proxy.register_tool(
        "import_stills_to_album",
        import_stills_to_album,
        "gallery",
        "Import still images into an album (.dpx, .drx, .png, .jpg)",
        {
            "album_index": {"type": "integer", "description": "Index of the still album (0-based)"},
            "file_paths": {"type": "array", "description": "List of file paths to import"}
        }
    )

    proxy.register_tool(
        "export_stills_from_album",
        export_stills_from_album,
        "gallery",
        "Export stills from an album",
        {
            "album_index": {"type": "integer", "description": "Index of the still album (0-based)"},
            "still_indices": {"type": "array", "description": "List of still indices to export (0-based)"},
            "folder_path": {"type": "string", "description": "Destination folder path"},
            "file_prefix": {"type": "string", "description": "Prefix for exported filenames"},
            "format": {"type": "string", "description": "Export format (drx or dpx)", "default": "drx"}
        }
    )

    proxy.register_tool(
        "delete_stills_from_album",
        delete_stills_from_album,
        "gallery",
        "Delete stills from an album",
        {
            "album_index": {"type": "integer", "description": "Index of the still album (0-based)"},
            "still_indices": {"type": "array", "description": "List of still indices to delete (0-based)"}
        }
    )

    logger.info("Registered 6 GalleryStillAlbum Complete tools (Phase 6)")
    return 6


# For standalone testing
if __name__ == "__main__":
    print("GalleryStillAlbum Complete Tools - Testing")
    print("=" * 60)

    try:
        gallery = get_gallery()
        if gallery:
            albums = gallery.GetGalleryStillAlbums()
            print(f"\nStill Albums: {len(albums) if albums else 0}")
        else:
            print("\nNo gallery available")
    except Exception as e:
        print(f"Error: {e}")
