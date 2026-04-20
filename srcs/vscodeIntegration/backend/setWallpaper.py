#!/usr/bin/env python3
import os
import platform
import subprocess
from pathlib import Path


WALLPAPER_REL_PATH = Path("../resources/flagWall.png")


def getWallpaperPath() -> Path:
    return (Path(__file__).resolve().parent / WALLPAPER_REL_PATH).resolve()


def runCommand(command: list[str]) -> None:
    subprocess.run(command, check=True)


def setLinuxWallpaper(wallpaper_path: Path) -> None:
    desktop = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
    session = os.environ.get("DESKTOP_SESSION", "").lower()
    image_uri = wallpaper_path.as_uri()

    if "gnome" in desktop or "gnome" in session or "unity" in desktop:
        runCommand(
            [
                "gsettings",
                "set",
                "org.gnome.desktop.background",
                "picture-uri",
                image_uri,
            ]
        )
        runCommand(
            [
                "gsettings",
                "set",
                "org.gnome.desktop.background",
                "picture-uri-dark",
                image_uri,
            ]
        )
        return

    if "cinnamon" in desktop or "cinnamon" in session:
        runCommand(
            [
                "gsettings",
                "set",
                "org.cinnamon.desktop.background",
                "picture-uri",
                image_uri,
            ]
        )
        return

    if "mate" in desktop or "mate" in session:
        runCommand(
            [
                "gsettings",
                "set",
                "org.mate.background",
                "picture-filename",
                str(wallpaper_path),
            ]
        )
        return

    raise RuntimeError(
        "Unsupported Linux desktop environment. "
        "Supported desktops: GNOME, Unity, Cinnamon, MATE."
    )


def setMacWallpaper(wallpaper_path: Path) -> None:
    script = (
        'tell application "System Events" to tell every desktop '
        f'to set picture to "{wallpaper_path}"'
    )
    runCommand(["osascript", "-e", script])


def setWindowsWallpaper(wallpaper_path: Path) -> None:
    import ctypes

    result = ctypes.windll.user32.SystemParametersInfoW(20, 0, str(wallpaper_path), 3)
    if not result:
        raise RuntimeError("Windows rejected the wallpaper change.")


def setWallpaper(wallpaper_path: Path) -> None:
    system = platform.system()
    if system == "Linux":
        setLinuxWallpaper(wallpaper_path)
    elif system == "Darwin":
        setMacWallpaper(wallpaper_path)
    elif system == "Windows":
        setWindowsWallpaper(wallpaper_path)
    else:
        raise RuntimeError(f"Unsupported operating system: {system}")


def main() -> None:
    wallpaper_path = getWallpaperPath()

    if not wallpaper_path.is_file():
        raise SystemExit(f"Wallpaper image not found: {wallpaper_path}")

    setWallpaper(wallpaper_path)


if __name__ == "__main__":
    main()
