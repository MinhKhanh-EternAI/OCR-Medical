import sys
from pathlib import Path

def resource_path(relative_path: str) -> Path:
    """
    Get absolute path to resource - works for dev and PyInstaller
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = Path(sys._MEIPASS)
    except Exception:
        # Development mode
        base_path = Path(__file__).resolve().parent.parent
    
    return base_path / relative_path