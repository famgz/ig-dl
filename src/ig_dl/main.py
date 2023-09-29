import json
import os
import requests
from famgz_utils import print, open_folder, json_
from os import path as p
from pathlib import Path
from time import sleep
from unidecode import unidecode

from .config import (
    SOURCE_DIR,
    DATA_DIR,
    COOKIES_DIR,
    TEMP_DIR,
    OUTPUT_DIR,
    cookies,
    headers,
    session,
)

POSTS      = True
HIGHLIGHTS = False
STORIES    = False

_ASCII = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_'

_friends_cache = {}

_debug = []

_profiles_with_news = {}
OPEN_FOLDERS_WITH_NEWS = True

_users_backup = {}
SAVE_USERS_BACKUP = False


def check_profile_dirs(page_name):
    if not p.isdir(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)
    for folder in ['posts', 'stories', 'highlights']:
        path = Path(OUTPUT_DIR, page_name, folder)
        path.mkdir(parents=True, exist_ok=True)


def is_json_response(r):
    return 'json' in r.headers.get('content-type')


def get_page(url, params=None):
    r = session.get(url, headers=headers, cookies=cookies, params=params)
    if not r.ok:
        print(f'[yellow]response not ok for url: {url}')
        if is_json_response(r):
            print(f'[yellow]{r.json()}')
        return None
    return r


def get_user_id(name):
    # url = f'https://www.instagram.com/{name}/?__a=1'  # deprecated
    url = 'https://www.instagram.com/api/v1/users/web_profile_info/'
    params = {
       'username': name,
    }
    r = requests.get(url, headers=headers, params=params)
    rj = r.json()
    # user_id = rj['graphql']['user']['id']  # deprecated
    user_id = rj['data']['user']['id']
    return user_id


def search_friends(username, string, full_profile_links=True, to_json=False):
    # Deprecated function since now desktop Instagram page provides account searcher
    # https://www.instagram.com/api/v1/friendships/ID/following/?query=username
    # TODO: convert this function to find common accounts between two or more profiles
    if username in _friends_cache:
        results = _friends_cache[username]

    else:
        cookies = {
            'GET SEARCHER COOKIES'
        }

        headers = {
            'GET SEARCHER HEADERS'
        }

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


def open_news_folders():
    for username, modes in _profiles_with_news.items():
        for mode in modes:
            folder_path = Path(OUTPUT_DIR, username, mode)
            open_folder(folder_path)
            sleep(0.2)


def media_id_to_code(media_id):
    media_id = int(media_id)
    short_code = ''
    while media_id > 0:
        remainder = media_id % 64
        media_id = (media_id-remainder)//64
        short_code = _ASCII[remainder] + short_code
    return short_code


def code_to_media_id(short_code):
    media_id = 0
    for letter in short_code:
        media_id = (media_id*64) + _ASCII.index(letter)
    return media_id


def save_json(img_urls, page_name, mode):

    def create_json():
        with open(json_path, 'w', encoding='utf-8') as f:
            dct = dict(posts=[], stories=[], highlights=[])
            json.dump(dct, f)

    def write_json():
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(j, f)

    def check_duplicates():
        existing = [x['img_id'] for x in j[mode]]
        new_images = [x for x in img_urls if x['img_id'] not in existing]
        return new_images

    assert mode in ['posts', 'stories', 'highlights']
    json_path = Path(SOURCE_DIR, 'data', f'{page_name}.json')

    if not p.isfile(json_path):
        create_json()

    with open(json_path, encoding='utf-8') as f:
        j = json.load(f)

    # DEPRECATED: no use storing old links since they cannot get validated
    # new_images = check_duplicates()
    # if new_images:
    #     j[mode].extend(new_images)
    # else:
    #     print(f'[bright_black]No new images were found in {page_name}.json. Double checking with files...')

    j[mode] = img_urls
    write_json()

    download_images(page_name, mode)


def download_images(username, mode):

    def save_file(img_path, display_url) -> bool:
        r = get_page(display_url)
        if not r.ok:
            return False
        with open(img_path, 'wb') as f:
            f.write(r.content)
        return True

    json_file = username + '.json'
    json_path = Path(SOURCE_DIR, 'data', json_file)
    folder_path = Path(OUTPUT_DIR, username, mode)
    files = [x.name for x in folder_path.iterdir() if x.is_file()]

    with open(json_path) as f:
        images = json.load(f)[mode]

    saved = 0
    error = []
    CHILL_AFTER_N_ITEMS = 250

    if username in ['dicasdearq', '#saved'] and mode == 'posts':
        images = images[::-1]

    for i, image in enumerate(images):
        img_shortcode = image['shortcode']
        img_id = image['img_id']
        img_url = image['display_url']

        # workaround to index nessa's images
        index = f'{i}_' if username in ['dicasdearq', '#saved'] else ''

        # check if image already exists
        img_file = f'{index}{img_id}_{img_shortcode}.jpg'
        if img_file in files:
            continue
        files.append(img_file)
        img_path = Path(folder_path, img_file)

        # download image
        was_downloaded = save_file(img_path, img_url)

        # little chill every 250 items
        if not i+1 % CHILL_AFTER_N_ITEMS:
            sleep(2)

        # download failed
        if not was_downloaded:
            error.append(img_url)  # TODO properly manage errors.: save them to local file instead of printing
            continue

        # download succeeded
        saved += 1
        print(f'[{i+1}/{len(images)}]', end='\t\r')

    score_f = f'\n\t[bold red]{saved}[yellow]' if saved else f'\t[bright_black]{saved}'
    if saved:
        _profiles_with_news.setdefault(username,[])
        if mode not in _profiles_with_news[username]:
            _profiles_with_news[username].append(mode)
    print(f'{score_f} new {mode}')
    if error:
        print(f'[black on yellow] {len(error)} errors [/]')
        for err in error:
            print(f'[bright_black]{err}')


def get_reels(items):
    img_urls = []
    for i, item in enumerate(items):
        if 'video_codec' in item:  # to avoid videos; not needed as it also offers a video screenshot
            pass
        if 'carousel_media' in item:
            temp = get_reels(item['carousel_media'])  # lol
            img_urls.extend(temp)
            continue
        display_url = item['image_versions2']['candidates'][0]['url']
        img_id = item['pk']
        shortcode = media_id_to_code(img_id)
        dct = dict(img_id=img_id, shortcode=shortcode, display_url=display_url)
        img_urls.append(dct)
    return img_urls


def scrape(page_name='', get_posts=POSTS, get_stories=STORIES, get_highlights=HIGHLIGHTS):

    def check_img(edge):
        node = edge['node']
        if node['is_video']:  # skip video preview image
            return
        get_img(node)

    def get_img(item):
        display_url = item['display_url']
        img_id = item['id']
        shortcode = media_id_to_code(img_id)
        dct = dict(img_id=img_id, shortcode=shortcode, display_url=display_url)
        img_urls.append(dct)
        # print(display_url)

    def divide_reels_per_size(tray):
        # group highlight ids based on total amount of media
        # to prevent `too many requests` error
        MAX_MEDIA_COUNT = 300
        chunks = []
        chunk_temp = []
        media_counter = 0
        for tr in tray:
            medias = tr['media_count']
            if media_counter + medias >= MAX_MEDIA_COUNT:
                chunks.append(chunk_temp)
                chunk_temp = []
                media_counter = 0
            chunk_temp.append(tr['id'])
            media_counter += medias
        return chunks

    if not page_name:
        page_name = input("Input instagram account name:\n>").lower().strip()

    check_profile_dirs(page_name)

    page_id = get_user_id(page_name)
    print(f'\n[bold blue]{page_name}')

    # get posts
    if get_posts:
        hash = '8c2a529969ee035a5063f2fc8602a0fd'
        after = ''
        # get posts
        img_urls = []
        for i in range(100):
            url = 'https://www.instagram.com/graphql/query/?query_hash=%s&variables={"id":"%s","first":50,"after":"%s"}' % (hash, page_id, after)
            r = get_page(url)
            sleep(0.1)
            assert r.ok
            rj = r.json()
            edge_owner_to_timeline_media = rj['data']['user']['edge_owner_to_timeline_media']

            # explore posts
            edges = edge_owner_to_timeline_media['edges']
            # show total posts
            if i == 0:
                count = edge_owner_to_timeline_media['count']
                print(f'[white]{count} total posts')
                if count and not edges:
                    print('[black on yellow] hidden data, private account. Use proper cookies ')
                    break
            for edge in edges:
                # explore carousel
                if edge['node'].get('edge_sidecar_to_children'):
                    car_edges = [x for x in edge['node']['edge_sidecar_to_children']['edges']]
                    for car_edge in car_edges:
                        check_img(car_edge)
                # get image if not carousel
                else:
                    check_img(edge)
            print(f'[white]{len(edges)} new edges, total images: {len(img_urls)}', end='\t\r')
            # get next_page
            has_next_page = edge_owner_to_timeline_media['page_info']['has_next_page']
            if has_next_page:
                after = edge_owner_to_timeline_media['page_info']['end_cursor']
            else:
                break
        print()
        if img_urls:
            save_json(img_urls, page_name, 'posts')
        else:
            print('No posts')

    # get highlights
    if get_highlights:
        url = f'https://i.instagram.com/api/v1/highlights/{page_id}/highlights_tray/'
        r = get_page(url)
        rj = r.json()
        tray = rj['tray']
        if not tray:
            print('No highlights')
        else:
            # highlight_ids = [x['id'] for x in tray]
            number_of_medias = sum( [x['media_count'] for x in tray] )
            highlight_ids = divide_reels_per_size(tray)
            for chunk in highlight_ids:
                params = (('reel_ids', chunk),)
                r = get_page('https://i.instagram.com/api/v1/feed/reels_media/', params=params)
                sleep(0.1)
                if not r:
                    continue
                rj = r.json()
                reels = [y['items'] for y in rj['reels_media']]
                items = []
                for i in reels:
                    for j in i:
                        items.append(j)
                print(f'{len(chunk)} highlights with {len(items)} images')
                img_urls = get_reels(items)
                if img_urls:
                    save_json(img_urls, page_name, 'highlights')
                else:
                    print('No highlights')

    # get stories
    if get_stories:
        img_urls = []
        url = f'https://i.instagram.com/api/v1/feed/user/{page_id}/story/'
        r = get_page(url)
        sleep(0.1)
        if r:
            rj = r.json()
            reel = rj['reel']
            if not reel:
                print('No stories')
            else:
                items = rj['reel']['items']
                print(len(items), 'total stories')
                img_urls = get_reels(items)
                if img_urls:
                    save_json(img_urls, page_name, 'stories')
                else:
                    print('No stories')


def routine():
    routine_profiles = [
        'python_brasil'
    ]

    try:
        for profile in routine_profiles:
            scrape(profile, get_posts=POSTS, get_stories=STORIES, get_highlights=HIGHLIGHTS)

    finally:
        if _profiles_with_news and OPEN_FOLDERS_WITH_NEWS:
            open_news_folders()
