"""
DaVinci Resolve MCP - Resolve and ProjectManager Complete

Implements all remaining Resolve and ProjectManager API operations for 100% coverage.

Includes:
- Render preset import/export (Resolve level)
- Keyframe mode management
- Database folder navigation

MEDIUM/HIGH PRIORITY: Completing Resolve and ProjectManager objects
"""

from typing import Dict, Any, List, Optional
import json
import logging

logger = logging.getLogger("davinci-resolve-mcp.tools.resolve_complete")

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
# Resolve Object - Render Preset Operations (HIGH PRIORITY)
# ============================================================================

def import_render_preset_resolve(preset_path: str) -> Dict[str, Any]:
    """
    Import a render preset from file (Resolve-level operation).

    Args:
        preset_path: Path to the render preset file (.xml)

    Returns:
        Import result

    Example:
        >>> import_render_preset_resolve("/presets/ProRes_422_HQ.xml")
        {
            "success": True,
            "preset_path": "/presets/ProRes_422_HQ.xml"
        }
    """
    try:
        resolve = get_resolve()

        # ImportRenderPreset(presetPath)
        result = resolve.ImportRenderPreset(preset_path)

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


def export_render_preset_resolve(
    preset_name: str,
    export_path: str
) -> Dict[str, Any]:
    """
    Export a render preset to file (Resolve-level operation).

    Args:
        preset_name: Name of the preset to export
        export_path: Destination path for preset file (.xml)

    Returns:
        Export result

    Example:
        >>> export_render_preset_resolve(
        ...     preset_name="My Custom Preset",
        ...     export_path="/presets/custom.xml"
        ... )
        {
            "success": True,
            "preset_name": "My Custom Preset",
            "export_path": "/presets/custom.xml"
        }
    """
    try:
        resolve = get_resolve()

        # ExportRenderPreset(presetName, exportPath)
        result = resolve.ExportRenderPreset(preset_name, export_path)

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


# ============================================================================
# Resolve Object - Keyframe Mode Operations (MEDIUM PRIORITY)
# ============================================================================

def get_keyframe_mode() -> Dict[str, Any]:
    """
    Get the current keyframe mode.

    Keyframe modes determine which parameters are keyframed:
    - All: All keyframeable parameters
    - Color: Only color parameters
    - Sizing: Only sizing/transform parameters

    Returns:
        Dictionary with current keyframe mode

    Example:
        >>> get_keyframe_mode()
        {
            "success": True,
            "keyframe_mode": "All"
        }
    """
    try:
        resolve = get_resolve()

        # GetKeyframeMode()
        mode = resolve.GetKeyframeMode()

        mode_names = {
            0: "All",
            1: "Color",
            2: "Sizing"
        }

        return {
            "success": True,
            "keyframe_mode": mode_names.get(mode, f"Unknown ({mode})"),
            "mode_value": mode
        }

    except Exception as e:
        logger.error(f"Error getting keyframe mode: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def set_keyframe_mode(keyframe_mode: str) -> Dict[str, Any]:
    """
    Set the keyframe mode.

    Args:
        keyframe_mode: Mode to set. Options:
            - "All" - Keyframe all parameters
            - "Color" - Keyframe only color parameters
            - "Sizing" - Keyframe only sizing/transform parameters

    Returns:
        Set result

    Example:
        >>> set_keyframe_mode("Color")
        {
            "success": True,
            "keyframe_mode": "Color"
        }
    """
    try:
        resolve = get_resolve()

        # Map string to mode value
        mode_map = {
            "All": 0,
            "Color": 1,
            "Sizing": 2
        }

        mode_value = mode_map.get(keyframe_mode)
        if mode_value is None:
            return {
                "success": False,
                "error": f"Invalid keyframe mode '{keyframe_mode}'. Use 'All', 'Color', or 'Sizing'"
            }

        # SetKeyframeMode(keyframeMode)
        result = resolve.SetKeyframeMode(mode_value)

        return {
            "success": bool(result),
            "keyframe_mode": keyframe_mode,
            "message": f"Keyframe mode {'set to' if result else 'set failed for'} {keyframe_mode}"
        }

    except Exception as e:
        logger.error(f"Error setting keyframe mode: {e}")
        return {
            "success": False,
            "error": str(e),
            "keyframe_mode": keyframe_mode
        }


# ============================================================================
# ProjectManager Object - Database Folder Navigation (MEDIUM PRIORITY)
# ============================================================================

def goto_root_folder_db() -> Dict[str, Any]:
    """
    Navigate to the root folder in the database (project list).

    Returns:
        Navigation result

    Example:
        >>> goto_root_folder_db()
        {
            "success": True,
            "message": "Navigated to root folder in database"
        }
    """
    try:
        pm = get_project_manager()

        # GotoRootFolder()
        result = pm.GotoRootFolder()

        return {
            "success": bool(result),
            "message": f"Navigated to root folder in database" if result else "Navigation failed"
        }

    except Exception as e:
        logger.error(f"Error navigating to root folder: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def goto_parent_folder_db() -> Dict[str, Any]:
    """
    Navigate to the parent folder in the database.

    Returns:
        Navigation result

    Example:
        >>> goto_parent_folder_db()
        {
            "success": True,
            "message": "Navigated to parent folder"
        }
    """
    try:
        pm = get_project_manager()

        # GotoParentFolder()
        result = pm.GotoParentFolder()

        return {
            "success": bool(result),
            "message": f"Navigated to parent folder" if result else "Navigation failed (may be at root)"
        }

    except Exception as e:
        logger.error(f"Error navigating to parent folder: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def get_current_folder_db() -> str:
    """
    Get the name of the current folder in the database.

    Returns:
        Current folder name

    Example:
        >>> get_current_folder_db()
        "My Projects"
    """
    try:
        pm = get_project_manager()

        # GetCurrentFolder()
        folder_name = pm.GetCurrentFolder()

        return folder_name if folder_name else "Root"

    except Exception as e:
        logger.error(f"Error getting current folder: {e}")
        return "Error"


def open_folder_db(folder_name: str) -> Dict[str, Any]:
    """
    Open a folder by name in the database.

    Args:
        folder_name: Name of the folder to open

    Returns:
        Open result

    Example:
        >>> open_folder_db("My Projects")
        {
            "success": True,
            "folder_name": "My Projects"
        }
    """
    try:
        pm = get_project_manager()

        # OpenFolder(folderName)
        result = pm.OpenFolder(folder_name)

        return {
            "success": bool(result),
            "folder_name": folder_name,
            "message": f"Folder {'opened' if result else 'open failed'}"
        }

    except Exception as e:
        logger.error(f"Error opening folder: {e}")
        return {
            "success": False,
            "error": str(e),
            "folder_name": folder_name
        }


# ============================================================================
# Tool Registration
# ============================================================================

def register_tools(mcp):
    """
    Register Resolve and ProjectManager Complete tools with the MCP server.

    Args:
        mcp: FastMCP server instance

    Returns:
        Number of tools registered
    """
    from ..proxy import get_proxy

    proxy = get_proxy()

    # Register Resolve render preset tools
    proxy.register_tool(
        "import_render_preset_resolve",
        import_render_preset_resolve,
        "delivery",
        "Import a render preset from file (Resolve-level)",
        {"preset_path": {"type": "string", "description": "Path to the render preset file (.xml)"}}
    )

    proxy.register_tool(
        "export_render_preset_resolve",
        export_render_preset_resolve,
        "delivery",
        "Export a render preset to file (Resolve-level)",
        {
            "preset_name": {"type": "string", "description": "Name of the preset to export"},
            "export_path": {"type": "string", "description": "Destination path for preset file"}
        }
    )

    # Register Resolve keyframe mode tools
    proxy.register_tool(
        "get_keyframe_mode",
        get_keyframe_mode,
        "color",
        "Get the current keyframe mode (All/Color/Sizing)",
        {}
    )

    proxy.register_tool(
        "set_keyframe_mode",
        set_keyframe_mode,
        "color",
        "Set the keyframe mode (All/Color/Sizing)",
        {"keyframe_mode": {"type": "string", "description": "Mode to set (All, Color, or Sizing)"}}
    )

    # Register ProjectManager database folder navigation tools
    proxy.register_tool(
        "goto_root_folder_db",
        goto_root_folder_db,
        "project",
        "Navigate to the root folder in the database (project list)",
        {}
    )

    proxy.register_tool(
        "goto_parent_folder_db",
        goto_parent_folder_db,
        "project",
        "Navigate to the parent folder in the database",
        {}
    )

    proxy.register_tool(
        "get_current_folder_db",
        get_current_folder_db,
        "project",
        "Get the name of the current folder in the database",
        {}
    )

    proxy.register_tool(
        "open_folder_db",
        open_folder_db,
        "project",
        "Open a folder by name in the database",
        {"folder_name": {"type": "string", "description": "Name of the folder to open"}}
    )

    logger.info("Registered 8 Resolve and ProjectManager Complete tools")
    return 8


# For standalone testing
if __name__ == "__main__":
    print("Resolve and ProjectManager Complete Tools - Testing")
    print("=" * 60)

    try:
        mode = get_keyframe_mode()
        print(f"\nKeyframe mode: {mode}")
    except Exception as e:
        print(f"Error: {e}")
