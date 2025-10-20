"""
DaVinci Resolve MCP - Advanced MediaPool Tools

Implements advanced MediaPool API operations including:
- Folder management (create, move, organize)
- Timeline creation from clips
- Timeline import (AAF, EDL, XML, FCPXML, etc.)
- Media relinking
- Auto audio sync

HIGH PRIORITY: Essential for media organization and workflow management
"""

from typing import Dict, Any, List, Optional, Union
import json
import logging

logger = logging.getLogger("davinci-resolve-mcp.tools.mediapool_advanced")

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


def get_media_pool():
    """Helper to get MediaPool from current project."""
    project = get_current_project()
    if not project:
        raise ValueError("No project is currently open")

    media_pool = project.GetMediaPool()
    if not media_pool:
        raise ValueError("Could not access Media Pool")

    return media_pool


# ============================================================================
# Folder Management Operations (HIGH PRIORITY)
# ============================================================================

def add_sub_folder(
    parent_folder_name: str,
    subfolder_name: str
) -> Dict[str, Any]:
    """
    Create a subfolder in the Media Pool.

    Folders help organize media clips into bins, essential for
    large projects with hundreds or thousands of clips.

    Args:
        parent_folder_name: Name of the parent folder (use "Master" for root)
        subfolder_name: Name for the new subfolder

    Returns:
        Folder creation result

    Example:
        >>> add_sub_folder(
        ...     parent_folder_name="Master",
        ...     subfolder_name="Interview Clips"
        ... )
        {
            "success": True,
            "parent_folder": "Master",
            "subfolder_name": "Interview Clips"
        }
    """
    try:
        media_pool = get_media_pool()

        # Get parent folder
        if parent_folder_name == "Master" or parent_folder_name == "Root":
            parent_folder = media_pool.GetRootFolder()
        else:
            # Search for folder by name
            root = media_pool.GetRootFolder()
            parent_folder = _find_folder_by_name(root, parent_folder_name)

        if not parent_folder:
            return {
                "success": False,
                "error": f"Parent folder '{parent_folder_name}' not found"
            }

        # AddSubFolder(folder, name)
        result = media_pool.AddSubFolder(parent_folder, subfolder_name)

        return {
            "success": bool(result),
            "parent_folder": parent_folder_name,
            "subfolder_name": subfolder_name,
            "message": f"Subfolder {'created' if result else 'creation failed'}"
        }

    except Exception as e:
        logger.error(f"Error adding subfolder: {e}")
        return {
            "success": False,
            "error": str(e),
            "parent_folder": parent_folder_name,
            "subfolder_name": subfolder_name
        }


def move_clips(
    clip_names: List[str],
    target_folder_name: str
) -> Dict[str, Any]:
    """
    Move clips to a target folder in the Media Pool.

    Args:
        clip_names: List of clip names to move
        target_folder_name: Name of the destination folder

    Returns:
        Move result with count of moved clips

    Example:
        >>> move_clips(
        ...     clip_names=["A001_C002.mov", "A001_C003.mov"],
        ...     target_folder_name="Interview Clips"
        ... )
        {
            "success": True,
            "moved_count": 2,
            "target_folder": "Interview Clips"
        }
    """
    try:
        media_pool = get_media_pool()
        root = media_pool.GetRootFolder()

        # Find clips by name
        clips = []
        for clip_name in clip_names:
            clip = _find_clip_by_name(root, clip_name)
            if clip:
                clips.append(clip)

        if not clips:
            return {
                "success": False,
                "error": "No clips found with specified names",
                "clip_names": clip_names
            }

        # Find target folder
        target_folder = _find_folder_by_name(root, target_folder_name)
        if not target_folder:
            return {
                "success": False,
                "error": f"Target folder '{target_folder_name}' not found"
            }

        # MoveClips([clips], targetFolder)
        result = media_pool.MoveClips(clips, target_folder)

        return {
            "success": bool(result),
            "moved_count": len(clips) if result else 0,
            "target_folder": target_folder_name,
            "message": f"Moved {len(clips) if result else 0} clips"
        }

    except Exception as e:
        logger.error(f"Error moving clips: {e}")
        return {
            "success": False,
            "error": str(e),
            "clip_names": clip_names
        }


# ============================================================================
# Timeline Creation Operations (HIGH PRIORITY)
# ============================================================================

def create_timeline_from_clips(
    timeline_name: str,
    clip_names: Optional[List[str]] = None,
    clip_info: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Create a timeline from specified clips.

    Three variants supported:
    1. Empty timeline: No clips specified
    2. Simple: List of clip names
    3. Advanced: List of clip info dictionaries with frame ranges

    Args:
        timeline_name: Name for the new timeline
        clip_names: Optional list of clip names to add (simple mode)
        clip_info: Optional list of clip info dicts (advanced mode)
            Each dict can contain:
            - "mediaPoolItem": clip name
            - "startFrame": start frame
            - "endFrame": end frame
            - "recordFrame": timeline position

    Returns:
        Timeline creation result

    Example:
        >>> # Simple mode
        >>> create_timeline_from_clips(
        ...     timeline_name="Interview Sequence",
        ...     clip_names=["A001_C002.mov", "A001_C003.mov"]
        ... )

        >>> # Advanced mode with frame ranges
        >>> create_timeline_from_clips(
        ...     timeline_name="Custom Sequence",
        ...     clip_info=[
        ...         {"mediaPoolItem": "A001_C002.mov", "startFrame": 100, "endFrame": 500},
        ...         {"mediaPoolItem": "A001_C003.mov", "startFrame": 200, "endFrame": 600}
        ...     ]
        ... )
    """
    try:
        media_pool = get_media_pool()
        root = media_pool.GetRootFolder()

        # Variant 1: Empty timeline
        if not clip_names and not clip_info:
            timeline = media_pool.CreateEmptyTimeline(timeline_name)
            return {
                "success": bool(timeline),
                "timeline_name": timeline_name,
                "clips_added": 0,
                "message": f"Empty timeline {'created' if timeline else 'creation failed'}"
            }

        # Variant 2: Simple mode with clip names
        if clip_names:
            clips = []
            for clip_name in clip_names:
                clip = _find_clip_by_name(root, clip_name)
                if clip:
                    clips.append(clip)

            if not clips:
                return {
                    "success": False,
                    "error": "No clips found with specified names",
                    "clip_names": clip_names
                }

            # CreateTimelineFromClips(name, [clips])
            timeline = media_pool.CreateTimelineFromClips(timeline_name, clips)

            return {
                "success": bool(timeline),
                "timeline_name": timeline_name,
                "clips_added": len(clips) if timeline else 0,
                "message": f"Timeline {'created' if timeline else 'creation failed'} with {len(clips)} clips"
            }

        # Variant 3: Advanced mode with clip info
        if clip_info:
            # Resolve clip names to MediaPoolItem objects
            processed_info = []
            for info in clip_info:
                clip_name = info.get("mediaPoolItem")
                if clip_name:
                    clip = _find_clip_by_name(root, clip_name)
                    if clip:
                        info_copy = info.copy()
                        info_copy["mediaPoolItem"] = clip
                        processed_info.append(info_copy)

            if not processed_info:
                return {
                    "success": False,
                    "error": "No valid clip info provided"
                }

            # CreateTimelineFromClips(name, [clipInfo])
            timeline = media_pool.CreateTimelineFromClips(timeline_name, processed_info)

            return {
                "success": bool(timeline),
                "timeline_name": timeline_name,
                "clips_added": len(processed_info) if timeline else 0,
                "message": f"Timeline {'created' if timeline else 'creation failed'} with {len(processed_info)} clips"
            }

    except Exception as e:
        logger.error(f"Error creating timeline from clips: {e}")
        return {
            "success": False,
            "error": str(e),
            "timeline_name": timeline_name
        }


def import_timeline_from_file(
    file_path: str,
    import_options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Import a timeline from file (AAF, EDL, XML, FCPXML, DRT, ADL, OTIO).

    Supports industry-standard interchange formats for bringing in
    timelines from other NLEs or projects.

    Args:
        file_path: Path to the timeline file
        import_options: Optional import settings:
            - "timelineName": Custom name for imported timeline
            - "importSourceClips": Import source clips (default: True)
            - "sourceClipsPath": Path to source media
            - "sourceClipsFolders": List of folders to search
            - "interlaceProcessing": Interlace processing mode

    Returns:
        Import result

    Example:
        >>> import_timeline_from_file(
        ...     file_path="/imports/sequence.xml",
        ...     import_options={
        ...         "timelineName": "Imported Sequence",
        ...         "importSourceClips": True,
        ...         "sourceClipsPath": "/media"
        ...     }
        ... )
        {
            "success": True,
            "file_path": "/imports/sequence.xml",
            "timeline_name": "Imported Sequence"
        }
    """
    try:
        media_pool = get_media_pool()

        import_options = import_options or {}

        # ImportTimelineFromFile(filePath, {importOptions})
        result = media_pool.ImportTimelineFromFile(file_path, import_options)

        timeline_name = import_options.get("timelineName", "Imported Timeline")

        return {
            "success": bool(result),
            "file_path": file_path,
            "timeline_name": timeline_name,
            "message": f"Timeline {'imported' if result else 'import failed'} from {file_path}"
        }

    except Exception as e:
        logger.error(f"Error importing timeline from file: {e}")
        return {
            "success": False,
            "error": str(e),
            "file_path": file_path
        }


# ============================================================================
# Media Management Operations (HIGH PRIORITY)
# ============================================================================

def relink_clips(
    clip_names: List[str],
    folder_path: str
) -> Dict[str, Any]:
    """
    Relink offline media clips to files in a folder.

    When media goes offline (moved or renamed), this reconnects clips
    to their source files in a new location.

    Args:
        clip_names: List of clip names to relink
        folder_path: Path to folder containing replacement media

    Returns:
        Relink result with count of relinked clips

    Example:
        >>> relink_clips(
        ...     clip_names=["A001_C002.mov", "A001_C003.mov"],
        ...     folder_path="/new_media_location"
        ... )
        {
            "success": True,
            "relinked_count": 2,
            "folder_path": "/new_media_location"
        }
    """
    try:
        media_pool = get_media_pool()
        root = media_pool.GetRootFolder()

        # Find clips by name
        clips = []
        for clip_name in clip_names:
            clip = _find_clip_by_name(root, clip_name)
            if clip:
                clips.append(clip)

        if not clips:
            return {
                "success": False,
                "error": "No clips found with specified names",
                "clip_names": clip_names
            }

        # RelinkClips([MediaPoolItem], folderPath)
        result = media_pool.RelinkClips(clips, folder_path)

        return {
            "success": bool(result),
            "relinked_count": len(clips) if result else 0,
            "folder_path": folder_path,
            "message": f"Relinked {len(clips) if result else 0} clips"
        }

    except Exception as e:
        logger.error(f"Error relinking clips: {e}")
        return {
            "success": False,
            "error": str(e),
            "clip_names": clip_names,
            "folder_path": folder_path
        }


def auto_sync_audio(
    clip_names: List[str],
    audio_sync_settings: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Auto-sync audio using waveform analysis.

    Automatically synchronizes dual-system audio (camera audio + external
    recorder) by analyzing waveforms.

    Args:
        clip_names: List of clip names to sync
        audio_sync_settings: Optional sync settings:
            - "mode": Sync mode (default: "waveform")
            - "offset": Frame offset adjustment
            - "threshold": Matching threshold (0.0-1.0)

    Returns:
        Sync result

    Example:
        >>> auto_sync_audio(
        ...     clip_names=["A001_C002.mov", "A001_C002_audio.wav"],
        ...     audio_sync_settings={"mode": "waveform", "threshold": 0.7}
        ... )
        {
            "success": True,
            "synced_count": 2,
            "mode": "waveform"
        }
    """
    try:
        media_pool = get_media_pool()
        root = media_pool.GetRootFolder()

        # Find clips by name
        clips = []
        for clip_name in clip_names:
            clip = _find_clip_by_name(root, clip_name)
            if clip:
                clips.append(clip)

        if not clips:
            return {
                "success": False,
                "error": "No clips found with specified names",
                "clip_names": clip_names
            }

        audio_sync_settings = audio_sync_settings or {}

        # AutoSyncAudio([MediaPoolItems], {audioSyncSettings})
        result = media_pool.AutoSyncAudio(clips, audio_sync_settings)

        return {
            "success": bool(result),
            "synced_count": len(clips) if result else 0,
            "mode": audio_sync_settings.get("mode", "waveform"),
            "message": f"Auto-synced {len(clips) if result else 0} clips"
        }

    except Exception as e:
        logger.error(f"Error auto-syncing audio: {e}")
        return {
            "success": False,
            "error": str(e),
            "clip_names": clip_names
        }


# ============================================================================
# Helper Functions
# ============================================================================

def _find_folder_by_name(root_folder, folder_name: str):
    """Recursively search for a folder by name."""
    if root_folder.GetName() == folder_name:
        return root_folder

    subfolders = root_folder.GetSubFolderList()
    if subfolders:
        for subfolder in subfolders:
            result = _find_folder_by_name(subfolder, folder_name)
            if result:
                return result

    return None


def _find_clip_by_name(folder, clip_name: str):
    """Recursively search for a clip by name."""
    clips = folder.GetClipList()
    if clips:
        for clip in clips:
            if clip.GetName() == clip_name:
                return clip

    # Search subfolders
    subfolders = folder.GetSubFolderList()
    if subfolders:
        for subfolder in subfolders:
            result = _find_clip_by_name(subfolder, clip_name)
            if result:
                return result

    return None


# ============================================================================
# Tool Registration
# ============================================================================

def register_tools(mcp):
    """
    Register advanced MediaPool tools with the MCP server.

    Args:
        mcp: FastMCP server instance

    Returns:
        Number of tools registered
    """
    from ..proxy import get_proxy

    proxy = get_proxy()

    # Register HIGH priority folder management tools
    proxy.register_tool(
        "add_sub_folder",
        add_sub_folder,
        "media",
        "Create a subfolder in the Media Pool for organizing clips",
        {
            "parent_folder_name": {"type": "string", "description": "Name of parent folder (use 'Master' for root)"},
            "subfolder_name": {"type": "string", "description": "Name for the new subfolder"}
        }
    )

    proxy.register_tool(
        "move_clips",
        move_clips,
        "media",
        "Move clips to a target folder in the Media Pool",
        {
            "clip_names": {"type": "array", "description": "List of clip names to move"},
            "target_folder_name": {"type": "string", "description": "Name of the destination folder"}
        }
    )

    # Register HIGH priority timeline creation tools
    proxy.register_tool(
        "create_timeline_from_clips",
        create_timeline_from_clips,
        "timeline",
        "Create a timeline from specified clips (supports empty, simple, and advanced modes)",
        {
            "timeline_name": {"type": "string", "description": "Name for the new timeline"},
            "clip_names": {"type": "array", "description": "Optional list of clip names (simple mode)", "optional": True},
            "clip_info": {"type": "array", "description": "Optional clip info with frame ranges (advanced mode)", "optional": True}
        }
    )

    proxy.register_tool(
        "import_timeline_from_file",
        import_timeline_from_file,
        "timeline",
        "Import a timeline from file (AAF, EDL, XML, FCPXML, DRT, ADL, OTIO)",
        {
            "file_path": {"type": "string", "description": "Path to the timeline file"},
            "import_options": {"type": "object", "description": "Optional import settings", "optional": True}
        }
    )

    # Register HIGH priority media management tools
    proxy.register_tool(
        "relink_clips",
        relink_clips,
        "media",
        "Relink offline media clips to files in a folder",
        {
            "clip_names": {"type": "array", "description": "List of clip names to relink"},
            "folder_path": {"type": "string", "description": "Path to folder containing replacement media"}
        }
    )

    proxy.register_tool(
        "auto_sync_audio",
        auto_sync_audio,
        "media",
        "Auto-sync dual-system audio using waveform analysis",
        {
            "clip_names": {"type": "array", "description": "List of clip names to sync"},
            "audio_sync_settings": {"type": "object", "description": "Optional sync settings", "optional": True}
        }
    )

    logger.info("Registered 6 advanced MediaPool tools")
    return 6


# For standalone testing
if __name__ == "__main__":
    print("Advanced MediaPool Tools - Testing")
    print("=" * 60)

    try:
        media_pool = get_media_pool()
        root = media_pool.GetRootFolder()
        print(f"\nRoot folder: {root.GetName()}")
    except Exception as e:
        print(f"Error: {e}")
