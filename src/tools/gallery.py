"""
DaVinci Resolve MCP - Gallery Tools

Implements all Gallery and GalleryStillAlbum API operations for managing
color grading stills, albums, and grade management.

HIGH PRIORITY: Gallery operations are essential for professional color workflows
"""

from typing import Dict, Any, List, Optional
import json

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
# Gallery Operations
# ============================================================================

def get_current_still_album() -> Dict[str, Any]:
    """
    Get the currently selected gallery still album.

    Returns:
        Dictionary with album information including label

    Example:
        >>> get_current_still_album()
        {
            "album_index": 0,
            "label": "Stills 1",
            "still_count": 5
        }
    """
    gallery = get_gallery()
    album = gallery.GetCurrentStillAlbum()

    if not album:
        return {
            "success": False,
            "error": "No still album is currently selected"
        }

    return {
        "success": True,
        "album": {
            "label": album.GetLabel(),
            "still_count": len(album.GetStills()) if album.GetStills() else 0
        }
    }


def set_current_still_album(album_index: int) -> Dict[str, Any]:
    """
    Set the currently selected gallery still album by index.

    Args:
        album_index: Index of the album to select (0-based)

    Returns:
        Success status

    Example:
        >>> set_current_still_album(album_index=2)
        {"success": True, "message": "Album 2 selected"}
    """
    gallery = get_gallery()
    albums = gallery.GetGalleryStillAlbums()

    if not albums or album_index < 0 or album_index >= len(albums):
        return {
            "success": False,
            "error": f"Invalid album index {album_index}. Available: 0-{len(albums)-1 if albums else 0}"
        }

    album = albums[album_index]
    success = gallery.SetCurrentStillAlbum(album)

    return {
        "success": success,
        "message": f"Album {album_index} ({'selected' if success else 'selection failed'})"
    }


def get_gallery_still_albums() -> List[Dict[str, Any]]:
    """
    Get list of all gallery still albums in the current project.

    Returns:
        List of album information dictionaries

    Example:
        >>> get_gallery_still_albums()
        [
            {"index": 0, "label": "Stills 1", "still_count": 3},
            {"index": 1, "label": "Hero Grades", "still_count": 12},
            {"index": 2, "label": "Day Exteriors", "still_count": 5}
        ]
    """
    gallery = get_gallery()
    albums = gallery.GetGalleryStillAlbums()

    if not albums:
        return []

    result = []
    for idx, album in enumerate(albums):
        stills = album.GetStills()
        result.append({
            "index": idx,
            "label": album.GetLabel(),
            "still_count": len(stills) if stills else 0
        })

    return result


# ============================================================================
# GalleryStillAlbum Operations
# ============================================================================

def get_album_stills(album_index: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Get list of all stills in a gallery album.

    Args:
        album_index: Index of album (uses current if None)

    Returns:
        List of still information

    Example:
        >>> get_album_stills(album_index=0)
        [
            {"index": 0, "label": "Still 001"},
            {"index": 1, "label": "Still 002"}
        ]
    """
    gallery = get_gallery()

    if album_index is not None:
        albums = gallery.GetGalleryStillAlbums()
        if not albums or album_index < 0 or album_index >= len(albums):
            return {
                "success": False,
                "error": f"Invalid album index {album_index}"
            }
        album = albums[album_index]
    else:
        album = gallery.GetCurrentStillAlbum()
        if not album:
            return {
                "success": False,
                "error": "No album selected"
            }

    stills = album.GetStills()
    if not stills:
        return []

    # Stills are typically dictionaries or objects with metadata
    result = []
    for idx, still in enumerate(stills):
        # Try to extract label/name if available
        if isinstance(still, dict):
            result.append({
                "index": idx,
                **still
            })
        else:
            result.append({
                "index": idx,
                "label": f"Still {idx + 1:03d}"
            })

    return result


def get_album_label(album_index: Optional[int] = None) -> str:
    """
    Get the label/name of a gallery still album.

    Args:
        album_index: Index of album (uses current if None)

    Returns:
        Album label string

    Example:
        >>> get_album_label(album_index=1)
        "Hero Grades"
    """
    gallery = get_gallery()

    if album_index is not None:
        albums = gallery.GetGalleryStillAlbums()
        if not albums or album_index < 0 or album_index >= len(albums):
            raise ValueError(f"Invalid album index {album_index}")
        album = albums[album_index]
    else:
        album = gallery.GetCurrentStillAlbum()
        if not album:
            raise ValueError("No album selected")

    return album.GetLabel()


def set_album_label(label: str, album_index: Optional[int] = None) -> Dict[str, Any]:
    """
    Set the label/name of a gallery still album.

    Args:
        label: New label for the album
        album_index: Index of album (uses current if None)

    Returns:
        Success status

    Example:
        >>> set_album_label(label="Day Exteriors", album_index=2)
        {"success": True, "message": "Album renamed to 'Day Exteriors'"}
    """
    gallery = get_gallery()

    if album_index is not None:
        albums = gallery.GetGalleryStillAlbums()
        if not albums or album_index < 0 or album_index >= len(albums):
            return {
                "success": False,
                "error": f"Invalid album index {album_index}"
            }
        album = albums[album_index]
    else:
        album = gallery.GetCurrentStillAlbum()
        if not album:
            return {
                "success": False,
                "error": "No album selected"
            }

    success = album.SetLabel(label)

    return {
        "success": success,
        "message": f"Album {'renamed to' if success else 'rename failed for'} '{label}'"
    }


def import_stills_to_album(
    file_paths: List[str],
    album_index: Optional[int] = None
) -> Dict[str, Any]:
    """
    Import still images (.dpx, .drx files) into a gallery album.

    Args:
        file_paths: List of file paths to import (.dpx, .drx formats)
        album_index: Index of album (uses current if None)

    Returns:
        Import result with count of imported stills

    Example:
        >>> import_stills_to_album(
        ...     file_paths=["/path/to/grade1.drx", "/path/to/grade2.drx"],
        ...     album_index=0
        ... )
        {
            "success": True,
            "imported_count": 2,
            "failed_count": 0
        }
    """
    gallery = get_gallery()

    if album_index is not None:
        albums = gallery.GetGalleryStillAlbums()
        if not albums or album_index < 0 or album_index >= len(albums):
            return {
                "success": False,
                "error": f"Invalid album index {album_index}"
            }
        album = albums[album_index]
    else:
        album = gallery.GetCurrentStillAlbum()
        if not album:
            return {
                "success": False,
                "error": "No album selected"
            }

    if not file_paths:
        return {
            "success": False,
            "error": "No file paths provided"
        }

    # ImportStills typically returns bool or count
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
            "failed_count": len(file_paths) - result
        }
    else:
        return {
            "success": True,
            "message": "Import completed",
            "result": result
        }


def export_stills_from_album(
    still_indices: List[int],
    folder_path: str,
    file_prefix: str,
    format: str = "drx",
    album_index: Optional[int] = None
) -> Dict[str, Any]:
    """
    Export stills from a gallery album to disk.

    Args:
        still_indices: List of still indices to export (0-based)
        folder_path: Destination folder path
        file_prefix: Prefix for exported filenames
        format: Export format ("drx" or "dpx")
        album_index: Index of album (uses current if None)

    Returns:
        Export result with count of exported stills

    Example:
        >>> export_stills_from_album(
        ...     still_indices=[0, 1, 2],
        ...     folder_path="/exports/grades",
        ...     file_prefix="hero_grade",
        ...     format="drx"
        ... )
        {
            "success": True,
            "exported_count": 3,
            "folder_path": "/exports/grades"
        }
    """
    gallery = get_gallery()

    if album_index is not None:
        albums = gallery.GetGalleryStillAlbums()
        if not albums or album_index < 0 or album_index >= len(albums):
            return {
                "success": False,
                "error": f"Invalid album index {album_index}"
            }
        album = albums[album_index]
    else:
        album = gallery.GetCurrentStillAlbum()
        if not album:
            return {
                "success": False,
                "error": "No album selected"
            }

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

    # ExportStills(stillIndices, folderPath, filePrefix, format)
    result = album.ExportStills(still_indices, folder_path, file_prefix, format)

    if isinstance(result, bool):
        return {
            "success": result,
            "attempted_count": len(still_indices),
            "folder_path": folder_path,
            "message": f"Export {'succeeded' if result else 'failed'}"
        }
    elif isinstance(result, int):
        return {
            "success": result > 0,
            "exported_count": result,
            "failed_count": len(still_indices) - result,
            "folder_path": folder_path
        }
    else:
        return {
            "success": True,
            "message": "Export completed",
            "folder_path": folder_path,
            "result": result
        }


def delete_stills_from_album(
    still_indices: List[int],
    album_index: Optional[int] = None
) -> Dict[str, Any]:
    """
    Delete stills from a gallery album.

    Args:
        still_indices: List of still indices to delete (0-based)
        album_index: Index of album (uses current if None)

    Returns:
        Deletion result

    Example:
        >>> delete_stills_from_album(still_indices=[0, 2, 5])
        {
            "success": True,
            "deleted_count": 3
        }
    """
    gallery = get_gallery()

    if album_index is not None:
        albums = gallery.GetGalleryStillAlbums()
        if not albums or album_index < 0 or album_index >= len(albums):
            return {
                "success": False,
                "error": f"Invalid album index {album_index}"
            }
        album = albums[album_index]
    else:
        album = gallery.GetCurrentStillAlbum()
        if not album:
            return {
                "success": False,
                "error": "No album selected"
            }

    if not still_indices:
        return {
            "success": False,
            "error": "No still indices provided"
        }

    result = album.DeleteStills(still_indices)

    if isinstance(result, bool):
        return {
            "success": result,
            "attempted_count": len(still_indices),
            "message": f"Delete {'succeeded' if result else 'failed'}"
        }
    elif isinstance(result, int):
        return {
            "success": result > 0,
            "deleted_count": result,
            "failed_count": len(still_indices) - result
        }
    else:
        return {
            "success": True,
            "message": "Delete completed",
            "result": result
        }


# ============================================================================
# Tool Registration
# ============================================================================

def register_tools(mcp):
    """
    Register all Gallery and GalleryStillAlbum tools with the MCP server.

    Args:
        mcp: FastMCP server instance

    Returns:
        Number of tools registered
    """
    from ..proxy import get_proxy
    import logging

    logger = logging.getLogger("davinci-resolve-mcp.tools.gallery")
    proxy = get_proxy()

    # Register all tools with proxy for search/execute
    proxy.register_tool(
        "get_current_still_album",
        get_current_still_album,
        "gallery",
        "Get the currently selected gallery still album",
        {}
    )

    proxy.register_tool(
        "set_current_still_album",
        set_current_still_album,
        "gallery",
        "Set the currently selected gallery still album by index",
        {"album_index": {"type": "integer", "description": "Index of the album to select (0-based)"}}
    )

    proxy.register_tool(
        "get_gallery_still_albums",
        get_gallery_still_albums,
        "gallery",
        "Get list of all gallery still albums in the project",
        {}
    )

    proxy.register_tool(
        "get_album_stills",
        get_album_stills,
        "gallery",
        "Get list of all stills in a gallery album",
        {"album_index": {"type": "integer", "description": "Index of album (uses current if None)", "optional": True}}
    )

    proxy.register_tool(
        "get_album_label",
        get_album_label,
        "gallery",
        "Get the label/name of a gallery still album",
        {"album_index": {"type": "integer", "description": "Index of album (uses current if None)", "optional": True}}
    )

    proxy.register_tool(
        "set_album_label",
        set_album_label,
        "gallery",
        "Set the label/name of a gallery still album",
        {
            "label": {"type": "string", "description": "New label for the album"},
            "album_index": {"type": "integer", "description": "Index of album (uses current if None)", "optional": True}
        }
    )

    proxy.register_tool(
        "import_stills_to_album",
        import_stills_to_album,
        "gallery",
        "Import still images (.dpx, .drx files) into a gallery album",
        {
            "file_paths": {"type": "array", "description": "List of file paths to import (.dpx, .drx formats)"},
            "album_index": {"type": "integer", "description": "Index of album (uses current if None)", "optional": True}
        }
    )

    proxy.register_tool(
        "export_stills_from_album",
        export_stills_from_album,
        "gallery",
        "Export stills from a gallery album to disk",
        {
            "still_indices": {"type": "array", "description": "List of still indices to export (0-based)"},
            "folder_path": {"type": "string", "description": "Destination folder path"},
            "file_prefix": {"type": "string", "description": "Prefix for exported filenames"},
            "format": {"type": "string", "description": "Export format (drx or dpx)", "default": "drx"},
            "album_index": {"type": "integer", "description": "Index of album (uses current if None)", "optional": True}
        }
    )

    proxy.register_tool(
        "delete_stills_from_album",
        delete_stills_from_album,
        "gallery",
        "Delete stills from a gallery album",
        {
            "still_indices": {"type": "array", "description": "List of still indices to delete (0-based)"},
            "album_index": {"type": "integer", "description": "Index of album (uses current if None)", "optional": True}
        }
    )

    logger.info("Registered 9 Gallery tools")
    return 9


# For standalone testing
if __name__ == "__main__":
    print("Gallery Tools - Testing")
    print("=" * 60)

    try:
        albums = get_gallery_still_albums()
        print(f"\nFound {len(albums)} gallery albums:")
        for album in albums:
            print(f"  - {album['label']}: {album['still_count']} stills")
    except Exception as e:
        print(f"Error: {e}")
