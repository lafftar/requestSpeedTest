from pathlib import Path
import sys


def get_project_root() -> str:
    """
    Determines the root directory of the project.
    Works correctly on Windows, macOS, and Linux, whether the code is run
    as a Python script or as a packaged .exe.
    """
    if getattr(sys, 'frozen', False):  # Check if running as a packaged .exe
        # Get the directory containing the .exe file
        path = Path(sys.executable).parent
    else:
        # Get the directory containing the Python script
        path = Path(__file__).parent.parent

    # Return the normalized path as a string
    return str(path.resolve())


if __name__ == "__main__":
    print(get_project_root())
