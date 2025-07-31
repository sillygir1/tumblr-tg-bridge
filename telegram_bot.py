import config
from dotmap import DotMap
import os.path
import pytumblr
import requests
from time import time

import tumblr_post

base_url = f'https://api.telegram.org/bot{config.telegram_api_key}'


def send_text_post(post_text: str):
    response = requests.post(
        f'{base_url}/sendMessage',
        params={
            'chat_id': config.telegram_chat_id,
            'parse_mode': 'MarkdownV2',
            'link_preview_options': '{"is_disabled": true}',
            'text': post_text,
        }
    )
    # print(response.content)


if not os.path.isfile(config.timestamp_file_path):
    with open(config.timestamp_file_path, 'x') as time_file:
        time_file.write(str(int(time())))
    exit(1)

with open(config.timestamp_file_path, 'r') as time_file:
    last_time = int(time_file.readline())

tumblr_client = pytumblr.TumblrRestClient(*config.tumblr_secret)

latest_posts = tumblr_client.posts(config.blog_name,
                                   #    type='text',
                                   limit=5)['posts'][::-1]

for post in latest_posts:
    post = DotMap(post)

    if post.timestamp < last_time:
        continue
    if post.state == 'private':
        continue

    # print(f'{post.type=}')

    if post.type == 'text':
        # print(post)
        parsed_post = tumblr_post.TextPost(post)
        match (parsed_post.media_count):
            case 0:
                post_text = parsed_post.prettify()
                # print(post_text)
                send_text_post(post_text)
                # print('')
                # print('')
            case 1:
                # TODO image post
                pass
            case _:
                # Multiple images. Impossible with current technology.
                continue
    elif post.type == 'answer':
        parsed_post = tumblr_post.AnswerPost(post)
        post_text = parsed_post.prettify()
        # print(post_text)
        send_text_post(post_text)
        # print('')
        # print('')


with open(config.timestamp_file_path, 'w+') as time_file:
    time_file.write(str(int(time())))
