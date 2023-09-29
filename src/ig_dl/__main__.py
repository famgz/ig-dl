import sys
from famgz_utils import print


if __name__ == '__main__':

    username = sys.argv[1] if len(sys.argv) > 1 else ''

    while not username:
        username = input('\nEnter a username to search or (Q) to quit\n>').strip().lower()
        if username == 'q':
            exit()

    from ig_dl.main import scrape
    from ig_dl.config import OUTPUT_DIR, session

    try:
        print(f'[white]The files will be saved to: {OUTPUT_DIR}\\{username}')
        scrape(username)
    finally:
        session.close()
