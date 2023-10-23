import requests
from famgz_utils import print, json_
from pathlib import Path
from time import sleep
from unidecode import unidecode

from .config import (
    TEMP_DIR,
    cookies,
    headers,
)
from .main import get_user_id

_debug = []
_friends_cache = {}
_users_backup = {}


def search_friends(username, string, full_profile_links=True, to_json=False):
    # Deprecated function since now desktop Instagram page provides account searcher
    # https://www.instagram.com/api/v1/friendships/ID/following/?query=username
    # TODO: However it could be converted to find common accounts between two or more profiles
    if username in _friends_cache:
        results = _friends_cache[username]

    else:
        results = {}
        user_id = get_user_id(username)
        ITEMS = 100

        print(f'[bright_blue]{username} [white]search...')

        for mode in ['followers', 'following']:
            i = 0
            count = 0
            while True:
                params = {
                    'count': str(ITEMS),
                    'max_id': str(ITEMS * i),
                    'search_surface': 'follow_list_page',
                }

                if i == 0:
                    del params['max_id']

                if mode == 'following':
                    del params['search_surface']

                url = f'https://www.instagram.com/api/v1/friendships/{user_id}/{mode}/'
                r = requests.get(
                    url,
                    params=params,
                    cookies=cookies,
                    headers=headers,
                )
                rj = r.json()
                friends = rj.get('users')

                count += len(friends)

                print(f'[bright_black]\[{mode}] {i+1} requests -> {count} accounts', end='\t\t\t\r')

                i += 1

                # no results, end of search
                if not friends:
                    break

                sleep(0.1)

                # save unique items
                for friend in friends:
                    _username = friend['username']
                    _fullname = unidecode(friend['full_name'])
                    if _username not in results:
                        results[_username] = _fullname
                    # log data for debugging
                    if _username not in _debug:
                        _debug.append(_username)
                    if to_json:
                        _users_backup.update({_username: friend})

                # no more future results, end of search
                if not rj.get('next_max_id'):
                    pass

            # print(f'\n[white]{len(results)} accounts found')
            print()
        print(f'{len(results)} [yellow]total accounts')

    if to_json:
        json_path = Path(TEMP_DIR, 'users.json')
        json_(json_path, _users_backup, sort_keys=True)

    string = string.lower()
    link = 'https://www.instagram.com/' if full_profile_links else ''

    # caching results for more inquiries
    _friends_cache.setdefault(username, {})
    has_news = False
    for _username, _fullname in results.items():
        if _username in _friends_cache[username]:
            continue
        _friends_cache[username][_username] = _fullname
        has_news = True
    if has_news:
        _friends_cache[username] = dict(sorted(_friends_cache[username].items()))

    matches = [link + _username for _username, _fullname in results.items() if string in _username or string in _fullname.lower()]
    matches = list(set(matches))
    return matches
