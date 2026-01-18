import os
import shutil
import stat
import logging

logger = logging.getLogger(__name__)

def safe_remove_directory(path: str):
    """
    Safely removes a directory and all its contents.
    Handles Read-Only files on Windows (common in .git folders) 
    by changing permissions before retry.
    """
    if not path or not os.path.exists(path):
        return

    def remove_readonly(func, path, excinfo):
        """Error handler for shutil.rmtree to handle read-only files"""
        try:
            os.chmod(path, stat.S_IWRITE)
            func(path)
        except Exception as e:
            logger.warning(f"Failed to remove {path} even after chmod: {e}")

    try:
        shutil.rmtree(path, onerror=remove_readonly)
    except Exception as e:
        logger.error(f"Failed to cleanup directory {path}: {e}")
