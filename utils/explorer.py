import subprocess
import sys


def open_explorer(path):
    if sys.platform.startswith("win32"):
        subprocess.Popen(["explorer", path])
    elif sys.platform.startswith("darwin"):
        subprocess.Popen(["open", "--", path])
    elif sys.platform.startswith("linux"):
        subprocess.Popen(["xdg-open", path])
