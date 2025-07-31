import config
from dotmap import DotMap
import os.path
import pytumblr
import requests
from time import time

import tumblr_post

base_url = f'https://api.telegram.org/bot{config.telegram_api_key}'
timestamp_file_name = 'last_checked'


if not os.path.isfile(timestamp_file_name):
    with open(timestamp_file_name, 'x') as time_file:
        time_file.write(str(int(time())))
    exit(1)

with open(timestamp_file_name, 'r') as time_file:
    last_time = int(time_file.readline())

tumblr_client = pytumblr.TumblrRestClient(*config.tumblr_secret)

latest_posts = tumblr_client.posts(config.blog_name,
                                   type='text',
                                   limit=5)['posts'][::-1]

for post in latest_posts:
    post = DotMap(post)

    if post.timestamp < last_time:
        continue
    # Commented for testing purposes
    # if post.state == 'private':
        # continue

    if post.type == 'text':
        parsed_post = tumblr_post.TextPost(post)
        post_text = parsed_post.prettify()
        # print(post_text)
        # print('')
        # print('')
        response = requests.post(
            f'{base_url}/sendMessage',
            params={
                'chat_id': config.telegram_chat_id,
                'parse_mode': 'Markdown',
                'link_preview_options': '{"is_disabled": true}',
                'text': post_text,
            }
        )
        print(response.content)


with open(timestamp_file_name, 'w+') as time_file:
    time_file.write(str(int(time())))
