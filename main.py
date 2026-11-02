"""PALOSEBO: FIESTA CLIMB - entry point.  Run with:  python main.py"""
import sys


def main():
    try:
        import pygame  # noqa: F401
    except ImportError:
        print("Pygame is not installed. Install it with:  pip install pygame")
        sys.exit(1)
    from app import App
    App().run()


if __name__ == "__main__":
    main()
