import sys
from famgz_utils import print, input
from pathlib import Path

if __package__ is None:
    sys.path.insert(0, Path(__file__).resolve().parent.parent)

if __name__ == "__main__":

    username = sys.argv[1] if len(sys.argv) > 1 else ""

    while not username:
        username = (
            input("\nEnter a username to search or (Q) to quit\n>").strip().lower()
        )
        if username == "q":
            print("\nExiting...")
            exit()

    from .main import scrape
    from .config import OUTPUT_DIR, session

    print()

    opts = {
        "posts": False,
        "highlights": False,
        "stories": False,
    }

    for opt in opts:
        opts[opt] = bool(input(f"Enter any key to get [bright_blue]{opt}[/]:\n>"))

    if not any([opt for opt in opts.values()]):
        print("\nNothing to do. Exiting...")
        exit()

    try:
        print(f"[white]The files will be saved to: {OUTPUT_DIR}\\{username}")
        scrape(
            username,
            get_posts=opts["posts"],
            get_highlights=opts["highlights"],
            get_stories=opts["stories"],
        )
    finally:
        session.close()
