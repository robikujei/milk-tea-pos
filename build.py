"""Copy static assets to Vercel's public directory, keeping their URL unchanged."""

from pathlib import Path
from shutil import copytree


if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    copytree(root / "static", root / "public" / "static", dirs_exist_ok=True)
