"""
DaVinci Resolve MCP - Advanced Project Management Tools

Implements advanced Project API operations including:
- Project import/export (.drp files)
- Project archiving and restore
- Render preset management
- Project backup operations

HIGH PRIORITY: Essential for project management and collaboration workflows
"""

from typing import Dict, Any, List, Optional
import json
import logging

logger = logging.getLogger("davinci-resolve-mcp.tools.project_advanced")

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
# Project Import/Export Operations (HIGH PRIORITY)
# ============================================================================

def export_project(
    project_name: str,
    file_path: str,
    with_stills_and_luts: bool = True
) -> Dict[str, Any]:
    """
    Export a project as a .drp file with optional stills and LUTs.

    .drp files are DaVinci Resolve's native project format, containing
    all timeline edits, grades, and metadata. Optionally includes gallery
    stills and LUT files.

    Args:
        project_name: Name of the project to export
        file_path: Destination path for .drp file
        with_stills_and_luts: Include gallery stills and LUTs (default: True)

    Returns:
        Export result with success status

    Example:
        >>> export_project(
        ...     project_name="My Film Project",
        ...     file_path="/backups/my_film_project.drp",
        ...     with_stills_and_luts=True
        ... )
        {
            "success": True,
            "project_name": "My Film Project",
            "file_path": "/backups/my_film_project.drp",
            "includes_stills_and_luts": True
        }
    """
    try:
        project_manager = get_project_manager()

        # ExportProject(projectName, filePath, withStillsAndLUTs)
        result = project_manager.ExportProject(project_name, file_path, with_stills_and_luts)

        return {
            "success": bool(result),
            "project_name": project_name,
            "file_path": file_path,
            "includes_stills_and_luts": with_stills_and_luts,
            "message": f"Project {'exported' if result else 'export failed'} to {file_path}"
        }

    except Exception as e:
        logger.error(f"Error exporting project: {e}")
        return {
            "success": False,
            "error": str(e),
            "project_name": project_name,
            "file_path": file_path
        }


def import_project(
    file_path: str,
    project_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Import a project from a .drp file.

    Args:
        file_path: Path to the .drp file to import
        project_name: Optional name for imported project (uses file name if None)

    Returns:
        Import result with success status

    Example:
        >>> import_project(
        ...     file_path="/backups/my_film_project.drp",
        ...     project_name="My Film Project - Imported"
        ... )
        {
            "success": True,
            "file_path": "/backups/my_film_project.drp",
            "project_name": "My Film Project - Imported"
        }
    """
    try:
        project_manager = get_project_manager()

        # ImportProject(filePath, projectName)
        if project_name:
            result = project_manager.ImportProject(file_path, project_name)
        else:
            result = project_manager.ImportProject(file_path)

        return {
            "success": bool(result),
            "file_path": file_path,
            "project_name": project_name or "Auto-named from file",
            "message": f"Project {'imported' if result else 'import failed'} from {file_path}"
        }

    except Exception as e:
        logger.error(f"Error importing project: {e}")
        return {
            "success": False,
            "error": str(e),
            "file_path": file_path
        }


def archive_project(
    project_name: str,
    file_path: str,
    is_archive_src_media: bool = True,
    is_archive_render_cache: bool = True,
    is_archive_proxy_media: bool = False
) -> Dict[str, Any]:
    """
    Archive a project with media, cache, and proxy files.

    Creates a complete project archive including source media, render cache,
    and optionally proxy media. Essential for long-term storage and project
    handoff.

    Args:
        project_name: Name of the project to archive
        file_path: Destination path for archive
        is_archive_src_media: Include source media files (default: True)
        is_archive_render_cache: Include render cache (default: True)
        is_archive_proxy_media: Include proxy media (default: False)

    Returns:
        Archive result with success status

    Example:
        >>> archive_project(
        ...     project_name="My Film Project",
        ...     file_path="/archives/my_film_complete.zip",
        ...     is_archive_src_media=True,
        ...     is_archive_render_cache=True,
        ...     is_archive_proxy_media=False
        ... )
        {
            "success": True,
            "project_name": "My Film Project",
            "file_path": "/archives/my_film_complete.zip",
            "includes_media": True,
            "includes_cache": True,
            "includes_proxies": False
        }
    """
    try:
        project_manager = get_project_manager()

        # ArchiveProject(projectName, filePath, isArchiveSrcMedia, isArchiveRenderCache, isArchiveProxyMedia)
        result = project_manager.ArchiveProject(
            project_name,
            file_path,
            is_archive_src_media,
            is_archive_render_cache,
            is_archive_proxy_media
        )

        return {
            "success": bool(result),
            "project_name": project_name,
            "file_path": file_path,
            "includes_media": is_archive_src_media,
            "includes_cache": is_archive_render_cache,
            "includes_proxies": is_archive_proxy_media,
            "message": f"Project {'archived' if result else 'archive failed'} to {file_path}"
        }

    except Exception as e:
        logger.error(f"Error archiving project: {e}")
        return {
            "success": False,
            "error": str(e),
            "project_name": project_name,
            "file_path": file_path
        }


def restore_project(
    file_path: str,
    project_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Restore a project from backup/archive.

    Args:
        file_path: Path to the backup/archive file
        project_name: Optional name for restored project

    Returns:
        Restore result with success status

    Example:
        >>> restore_project(
        ...     file_path="/archives/my_film_backup.drp",
        ...     project_name="My Film - Restored"
        ... )
        {
            "success": True,
            "file_path": "/archives/my_film_backup.drp",
            "project_name": "My Film - Restored"
        }
    """
    try:
        project_manager = get_project_manager()

        # RestoreProject(filePath, projectName)
        if project_name:
            result = project_manager.RestoreProject(file_path, project_name)
        else:
            result = project_manager.RestoreProject(file_path)

        return {
            "success": bool(result),
            "file_path": file_path,
            "project_name": project_name or "Auto-named",
            "message": f"Project {'restored' if result else 'restore failed'} from {file_path}"
        }

    except Exception as e:
        logger.error(f"Error restoring project: {e}")
        return {
            "success": False,
            "error": str(e),
            "file_path": file_path
        }


# ============================================================================
# Render Preset Management (HIGH PRIORITY)
# ============================================================================

def import_render_preset(preset_path: str) -> Dict[str, Any]:
    """
    Import a render preset from file.

    Render presets (.xml files) contain encoding settings, resolution,
    frame rate, and codec configurations.

    Args:
        preset_path: Path to the render preset file (.xml)

    Returns:
        Import result with success status

    Example:
        >>> import_render_preset("/presets/ProRes_422_HQ.xml")
        {
            "success": True,
            "preset_path": "/presets/ProRes_422_HQ.xml"
        }
    """
    try:
        project = get_current_project()

        # ImportRenderPreset(presetPath)
        result = project.ImportRenderPreset(preset_path)

        return {
            "success": bool(result),
            "preset_path": preset_path,
            "message": f"Render preset {'imported' if result else 'import failed'}"
        }

    except Exception as e:
        logger.error(f"Error importing render preset: {e}")
        return {
            "success": False,
            "error": str(e),
            "preset_path": preset_path
        }


def export_render_preset(
    preset_name: str,
    export_path: str
) -> Dict[str, Any]:
    """
    Export a render preset to file.

    Args:
        preset_name: Name of the preset to export
        export_path: Destination path for preset file (.xml)

    Returns:
        Export result with success status

    Example:
        >>> export_render_preset(
        ...     preset_name="My Custom H.264",
        ...     export_path="/presets/custom_h264.xml"
        ... )
        {
            "success": True,
            "preset_name": "My Custom H.264",
            "export_path": "/presets/custom_h264.xml"
        }
    """
    try:
        project = get_current_project()

        # ExportRenderPreset(presetName, exportPath)
        result = project.ExportRenderPreset(preset_name, export_path)

        return {
            "success": bool(result),
            "preset_name": preset_name,
            "export_path": export_path,
            "message": f"Render preset {'exported' if result else 'export failed'}"
        }

    except Exception as e:
        logger.error(f"Error exporting render preset: {e}")
        return {
            "success": False,
            "error": str(e),
            "preset_name": preset_name
        }


def save_as_new_render_preset(preset_name: str) -> Dict[str, Any]:
    """
    Save current render settings as a new preset.

    Creates a preset from the current render page settings, allowing
    you to reuse configurations across projects.

    Args:
        preset_name: Name for the new preset

    Returns:
        Save result with success status

    Example:
        >>> save_as_new_render_preset("My ProRes LT Preset")
        {
            "success": True,
            "preset_name": "My ProRes LT Preset",
            "message": "Render preset saved"
        }
    """
    try:
        project = get_current_project()

        # SaveAsNewRenderPreset(presetName)
        result = project.SaveAsNewRenderPreset(preset_name)

        return {
            "success": bool(result),
            "preset_name": preset_name,
            "message": f"Render preset {'saved' if result else 'save failed'}"
        }

    except Exception as e:
        logger.error(f"Error saving render preset: {e}")
        return {
            "success": False,
            "error": str(e),
            "preset_name": preset_name
        }


# ============================================================================
# Tool Registration
# ============================================================================

def register_tools(mcp):
    """
    Register advanced Project Management tools with the MCP server.

    Args:
        mcp: FastMCP server instance

    Returns:
        Number of tools registered
    """
    from ..proxy import get_proxy

    proxy = get_proxy()

    # Register HIGH priority project import/export tools
    proxy.register_tool(
        "export_project",
        export_project,
        "project",
        "Export a project as a .drp file with optional stills and LUTs",
        {
            "project_name": {"type": "string", "description": "Name of the project to export"},
            "file_path": {"type": "string", "description": "Destination path for .drp file"},
            "with_stills_and_luts": {"type": "boolean", "description": "Include gallery stills and LUTs", "default": True}
        }
    )

    proxy.register_tool(
        "import_project",
        import_project,
        "project",
        "Import a project from a .drp file",
        {
            "file_path": {"type": "string", "description": "Path to the .drp file"},
            "project_name": {"type": "string", "description": "Optional name for imported project", "optional": True}
        }
    )

    proxy.register_tool(
        "archive_project",
        archive_project,
        "project",
        "Archive a project with media, cache, and proxy files for long-term storage",
        {
            "project_name": {"type": "string", "description": "Name of the project to archive"},
            "file_path": {"type": "string", "description": "Destination path for archive"},
            "is_archive_src_media": {"type": "boolean", "description": "Include source media", "default": True},
            "is_archive_render_cache": {"type": "boolean", "description": "Include render cache", "default": True},
            "is_archive_proxy_media": {"type": "boolean", "description": "Include proxy media", "default": False}
        }
    )

    proxy.register_tool(
        "restore_project",
        restore_project,
        "project",
        "Restore a project from backup/archive",
        {
            "file_path": {"type": "string", "description": "Path to the backup/archive file"},
            "project_name": {"type": "string", "description": "Optional name for restored project", "optional": True}
        }
    )

    # Register HIGH priority render preset tools
    proxy.register_tool(
        "import_render_preset",
        import_render_preset,
        "delivery",
        "Import a render preset from file (.xml)",
        {"preset_path": {"type": "string", "description": "Path to the render preset file"}}
    )

    proxy.register_tool(
        "export_render_preset",
        export_render_preset,
        "delivery",
        "Export a render preset to file (.xml)",
        {
            "preset_name": {"type": "string", "description": "Name of the preset to export"},
            "export_path": {"type": "string", "description": "Destination path for preset file"}
        }
    )

    proxy.register_tool(
        "save_as_new_render_preset",
        save_as_new_render_preset,
        "delivery",
        "Save current render settings as a new preset",
        {"preset_name": {"type": "string", "description": "Name for the new preset"}}
    )

    logger.info("Registered 7 advanced Project Management tools")
    return 7


# For standalone testing
if __name__ == "__main__":
    print("Advanced Project Management Tools - Testing")
    print("=" * 60)

    try:
        project_manager = get_project_manager()
        print(f"\nProject Manager initialized")
    except Exception as e:
        print(f"Error: {e}")
