"""
Debug endpoints for development and troubleshooting
"""
from fastapi import APIRouter
import subprocess
import os

router = APIRouter()

@router.get("/debug-version")
async def get_debug_version():
    """
    Get current commit hash and deployment info
    """
    try:
        # Try to get git commit hash
        try:
            commit_hash = subprocess.check_output(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=os.path.dirname(__file__),
                stderr=subprocess.DEVNULL
            ).decode().strip()
        except:
            commit_hash = "unknown"
        
        # Get current timestamp
        import datetime
        current_time = datetime.datetime.utcnow().isoformat()
        
        return {
            "version": commit_hash,
            "commit_hash": commit_hash,
            "timestamp": current_time,
            "status": "active",
            "message": "Debug endpoint working - this confirms deployment is active"
        }
    except Exception as e:
        return {
            "version": "error",
            "commit_hash": "error",
            "timestamp": None,
            "status": "error",
            "message": f"Error getting version info: {str(e)}"
        }

