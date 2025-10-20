"""
DaVinci Resolve MCP - Render Settings Tools

Implements render configuration API operations including:
- Quick Export presets
- Render format and codec management
- Render settings configuration

HIGH PRIORITY: Essential for delivery and export workflows
"""

from typing import Dict, Any, List, Optional
import json
import logging

logger = logging.getLogger("davinci-resolve-mcp.tools.render_settings")

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
# Quick Export Operations (HIGH PRIORITY)
# ============================================================================

def get_quick_export_render_presets() -> List[str]:
    """
    Get list of available Quick Export render presets.

    Quick Export provides one-click export options optimized for
    common delivery formats (YouTube, Vimeo, H.264, ProRes, etc.).

    Returns:
        List of Quick Export preset names

    Example:
        >>> get_quick_export_render_presets()
        [
            "YouTube - 1080p",
            "Vimeo - 4K",
            "H.264 Master",
            "ProRes 422 HQ",
            "DNxHR HQX"
        ]
    """
    try:
        project = get_current_project()

        # GetQuickExportRenderPresets()
        presets = project.GetQuickExportRenderPresets()

        return presets if presets else []

    except Exception as e:
        logger.error(f"Error getting Quick Export presets: {e}")
        return []


def render_with_quick_export(
    preset_name: str,
    target_dir: Optional[str] = None,
    custom_name: Optional[str] = None,
    **additional_params
) -> Dict[str, Any]:
    """
    Render using a Quick Export preset.

    Quick Export provides fast, one-click rendering with optimized
    presets for common platforms and formats.

    Args:
        preset_name: Name of the Quick Export preset
        target_dir: Optional custom output directory
        custom_name: Optional custom output filename
        **additional_params: Additional preset-specific parameters

    Returns:
        Render result with job ID

    Example:
        >>> render_with_quick_export(
        ...     preset_name="YouTube - 1080p",
        ...     target_dir="/exports/youtube",
        ...     custom_name="my_video_final"
        ... )
        {
            "success": True,
            "preset_name": "YouTube - 1080p",
            "job_id": "render_job_123",
            "target_dir": "/exports/youtube"
        }
    """
    try:
        project = get_current_project()

        # Build parameter dictionary
        params = {}
        if target_dir:
            params["TargetDir"] = target_dir
        if custom_name:
            params["CustomName"] = custom_name

        # Add any additional parameters
        params.update(additional_params)

        # RenderWithQuickExport(preset_name, {param_dict})
        result = project.RenderWithQuickExport(preset_name, params)

        return {
            "success": bool(result),
            "preset_name": preset_name,
            "job_id": result if result else None,
            "target_dir": target_dir,
            "custom_name": custom_name,
            "message": f"Quick Export render {'started' if result else 'failed'}"
        }

    except Exception as e:
        logger.error(f"Error rendering with Quick Export: {e}")
        return {
            "success": False,
            "error": str(e),
            "preset_name": preset_name
        }


# ============================================================================
# Render Format and Codec Management (HIGH PRIORITY)
# ============================================================================

def get_render_formats() -> List[str]:
    """
    Get list of available render formats.

    Returns all render container formats supported by the system
    (QuickTime, MP4, MXF, etc.).

    Returns:
        List of render format names

    Example:
        >>> get_render_formats()
        [
            "QuickTime",
            "MP4",
            "MXF OP1a",
            "AVI",
            "Wave",
            "AIFF"
        ]
    """
    try:
        project = get_current_project()

        # GetRenderFormats()
        formats = project.GetRenderFormats()

        return formats if formats else []

    except Exception as e:
        logger.error(f"Error getting render formats: {e}")
        return []


def get_render_codecs(render_format: str) -> List[str]:
    """
    Get list of available codecs for a specific render format.

    Args:
        render_format: The render format name (e.g., "QuickTime", "MP4")

    Returns:
        List of codec names available for the format

    Example:
        >>> get_render_codecs("QuickTime")
        [
            "Apple ProRes 422 HQ",
            "Apple ProRes 422",
            "Apple ProRes 422 LT",
            "Apple ProRes 422 Proxy",
            "H.264",
            "H.265"
        ]
    """
    try:
        project = get_current_project()

        # GetRenderCodecs(renderFormat)
        codecs = project.GetRenderCodecs(render_format)

        return codecs if codecs else []

    except Exception as e:
        logger.error(f"Error getting render codecs for format '{render_format}': {e}")
        return []


def set_current_render_format_and_codec(
    render_format: str,
    codec: str
) -> Dict[str, Any]:
    """
    Set the current render format and codec.

    Configures the render page with the specified format and codec
    combination.

    Args:
        render_format: The render format (e.g., "QuickTime", "MP4")
        codec: The codec (e.g., "Apple ProRes 422 HQ", "H.264")

    Returns:
        Set result with success status

    Example:
        >>> set_current_render_format_and_codec(
        ...     render_format="QuickTime",
        ...     codec="Apple ProRes 422 HQ"
        ... )
        {
            "success": True,
            "render_format": "QuickTime",
            "codec": "Apple ProRes 422 HQ",
            "message": "Render format and codec set"
        }
    """
    try:
        project = get_current_project()

        # SetCurrentRenderFormatAndCodec(format, codec)
        result = project.SetCurrentRenderFormatAndCodec(render_format, codec)

        return {
            "success": bool(result),
            "render_format": render_format,
            "codec": codec,
            "message": f"Render format and codec {'set' if result else 'set failed'}"
        }

    except Exception as e:
        logger.error(f"Error setting render format and codec: {e}")
        return {
            "success": False,
            "error": str(e),
            "render_format": render_format,
            "codec": codec
        }


def get_current_render_mode() -> Dict[str, Any]:
    """
    Get the current render mode settings.

    Returns information about the current render configuration.

    Returns:
        Dictionary with current render mode settings

    Example:
        >>> get_current_render_mode()
        {
            "render_mode": "Individual clips",
            "mark_in": 0,
            "mark_out": 1000
        }
    """
    try:
        project = get_current_project()

        # GetCurrentRenderMode() returns int
        # 0: Individual clips, 1: Single clip
        mode_int = project.GetCurrentRenderMode()

        mode_names = {
            0: "Individual clips",
            1: "Single clip"
        }

        return {
            "render_mode": mode_names.get(mode_int, f"Unknown ({mode_int})"),
            "mode_value": mode_int
        }

    except Exception as e:
        logger.error(f"Error getting current render mode: {e}")
        return {
            "error": str(e)
        }


def set_current_render_mode(mode: int) -> Dict[str, Any]:
    """
    Set the current render mode.

    Args:
        mode: Render mode (0 = Individual clips, 1 = Single clip)

    Returns:
        Set result with success status

    Example:
        >>> set_current_render_mode(mode=0)
        {
            "success": True,
            "mode": 0,
            "mode_name": "Individual clips"
        }
    """
    try:
        project = get_current_project()

        mode_names = {
            0: "Individual clips",
            1: "Single clip"
        }

        # SetCurrentRenderMode(mode)
        result = project.SetCurrentRenderMode(mode)

        return {
            "success": bool(result),
            "mode": mode,
            "mode_name": mode_names.get(mode, f"Unknown ({mode})"),
            "message": f"Render mode {'set' if result else 'set failed'}"
        }

    except Exception as e:
        logger.error(f"Error setting current render mode: {e}")
        return {
            "success": False,
            "error": str(e),
            "mode": mode
        }


# ============================================================================
# Tool Registration
# ============================================================================

def register_tools(mcp):
    """
    Register Render Settings tools with the MCP server.

    Args:
        mcp: FastMCP server instance

    Returns:
        Number of tools registered
    """
    from ..proxy import get_proxy

    proxy = get_proxy()

    # Register HIGH priority Quick Export tools
    proxy.register_tool(
        "get_quick_export_render_presets",
        get_quick_export_render_presets,
        "delivery",
        "Get list of available Quick Export render presets",
        {}
    )

    proxy.register_tool(
        "render_with_quick_export",
        render_with_quick_export,
        "delivery",
        "Render using a Quick Export preset for fast one-click delivery",
        {
            "preset_name": {"type": "string", "description": "Name of the Quick Export preset"},
            "target_dir": {"type": "string", "description": "Optional custom output directory", "optional": True},
            "custom_name": {"type": "string", "description": "Optional custom output filename", "optional": True}
        }
    )

    # Register HIGH priority format/codec tools
    proxy.register_tool(
        "get_render_formats",
        get_render_formats,
        "delivery",
        "Get list of available render formats (QuickTime, MP4, MXF, etc.)",
        {}
    )

    proxy.register_tool(
        "get_render_codecs",
        get_render_codecs,
        "delivery",
        "Get list of available codecs for a specific render format",
        {"render_format": {"type": "string", "description": "The render format name"}}
    )

    proxy.register_tool(
        "set_current_render_format_and_codec",
        set_current_render_format_and_codec,
        "delivery",
        "Set the current render format and codec",
        {
            "render_format": {"type": "string", "description": "The render format (e.g., QuickTime, MP4)"},
            "codec": {"type": "string", "description": "The codec (e.g., Apple ProRes 422 HQ)"}
        }
    )

    proxy.register_tool(
        "get_current_render_mode",
        get_current_render_mode,
        "delivery",
        "Get the current render mode settings",
        {}
    )

    proxy.register_tool(
        "set_current_render_mode",
        set_current_render_mode,
        "delivery",
        "Set the current render mode (Individual clips or Single clip)",
        {"mode": {"type": "integer", "description": "Render mode (0 = Individual clips, 1 = Single clip)"}}
    )

    logger.info("Registered 7 Render Settings tools")
    return 7


# For standalone testing
if __name__ == "__main__":
    print("Render Settings Tools - Testing")
    print("=" * 60)

    try:
        presets = get_quick_export_render_presets()
        print(f"\nQuick Export Presets ({len(presets)}):")
        for preset in presets:
            print(f"  - {preset}")

        formats = get_render_formats()
        print(f"\nRender Formats ({len(formats)}):")
        for fmt in formats[:5]:
            print(f"  - {fmt}")
    except Exception as e:
        print(f"Error: {e}")
