import config
from dotmap import DotMap
# import os.path
import json
import pytumblr
import requests
from time import time, sleep
import threading
import traceback
import tumblr_post
from urllib.parse import urlparse


class TelegramBot:
    def __init__(self, config_file):
        self.is_bridge = 'bridge' in config_file.mode
        self.is_inline = 'inline' in config_file.mode
        self.api_base = config_file.api_url
        self.debug = config_file.debug
        self.blog_name = config_file.blog_name
        self.tumblr_client = pytumblr.TumblrRestClient(
            *config_file.tumblr_secret)

        self.bridge_running = False
        self.inline_running = False

        if self.is_bridge:
            self.chat_id = config_file.telegram_chat_id
            self.update_time = config_file.update_time
            self.last_post_time = int(time())

        if self.is_inline:
            if config_file.allowed_user_ids == 'all':
                self.allowed_users = 'all'
            else:
                self.allowed_users = config_file.allowed_user_ids

    def _bridge_post_text_(self, post_text: str):
        response = requests.post(
            f'{self.api_base}/sendMessage',
            params={
                'chat_id': config.telegram_chat_id,
                'parse_mode': 'MarkdownV2',
                'link_preview_options': '{"is_disabled": true}',
                'text': post_text,
            }
        )
        if self.debug:
            print(response.content)

    def _bridge_post_image_(self, post_text: str, image_url: str):
        response = requests.post(
            f'{self.api_base}/sendPhoto',
            params={
                'chat_id': config.telegram_chat_id,
                'parse_mode': 'MarkdownV2',
                'link_preview_options': '{"is_disabled": true}',
                'photo': image_url,
                'show_caption_above_media': True,
                'caption': post_text,
            }
        )
        if self.debug:
            print(response.content)

    def _bridge_post_video_(self, post_text: str, video_url: str):
        response = requests.post(
            f'{self.api_base}/sendVideo',
            params={
                'chat_id': config.telegram_chat_id,
                'parse_mode': 'MarkdownV2',
                'link_preview_options': '{"is_disabled": true}',
                'video': video_url,
                'show_caption_above_media': True,
                'caption': post_text,
            }
        )
        if self.debug:
            print(response.content)

    def _inline_post_(self, query_id: str, post_type: str, *post):
        if post_type == 'text':
            response_results = json.dumps(
                [{
                    'type': 'article',
                    'id': '0',
                    'title': f'{post[:20]}...',
                    'input_message_content': {
                        'message_text': post[0],
                        'parse_mode': 'MarkdownV2',
                        'link_preview_options': {'is_disabled': True}
                    },
                    'thumbnail_url': 'https://assets.tumblr.com/pop/manifest/favicon-0e3d244a.ico',
                }])
            response = requests.post(f'{self.api_base}/answerInlineQuery',
                                     params={
                'inline_query_id': query_id,
                'results': response_results,
                'is_personal': True,
                'cache_time': 0,
            }
            )
            if self.debug:
                print(response.content)
        elif post_type == 'image':
            response_results = json.dumps(
                [{
                    'type': 'photo',
                    'id': '0',
                    'title': f'{post[0][:20]}...',
                    'photo_url': post[1],
                    'caption': post[0],
                    'parse_mode': 'MarkdownV2',
                    'show_caption_above_media': True,
                    'link_preview_options': {'is_disabled': True},
                    'thumbnail_url': 'https://assets.tumblr.com/pop/manifest/favicon-0e3d244a.ico',
                }])
            response = requests.post(f'{self.api_base}/answerInlineQuery',
                                     params={
                'inline_query_id': query_id,
                'results': response_results,
                'is_personal': True,
            }
            )
            if self.debug:
                print(response.content)
        # TODO video

    def _bridge_post_(self, post_type, *post):
        match post_type:
            case 'text':
                self._bridge_post_text_(post)
            case 'image':
                self._bridge_post_image_(*post)
            case 'video':
                self._bridge_post_video_(*post)

    def _process_post_(self, post: dict):
        # Reusing old logic here

        if post.type == 'text':
            try:
                parsed_post = tumblr_post.TextPost(post)
            except Exception as e:
                if self.debug:
                    print('Exception when getting latest posts.')
                    print(traceback.format_exc())
            match (parsed_post.media_count):
                case 0:
                    post_text = parsed_post.prettify()
                    # print(post_text)
                    # print('')
                    # print('')
                    return 'text', post_text
                case 1:
                    media_url = [
                        trail.media for trail in parsed_post.trail if trail.media][0][0]
                    if media_url.endswith('.jpg') or\
                            media_url.endswith('.jpeg') or\
                            media_url.endswith('.png'):
                        parsed_post = tumblr_post.ImagePost(post)
                        post_text, image_url = parsed_post.prettify()
                        # print(f'{post_text=}')
                        # print(f'{image_url=}')
                        return 'image', post_text, image_url
                    elif media_url.endswith('.mp4'):
                        parsed_post = tumblr_post.VideoPost(post)
                        post_text, video_url = parsed_post.prettify()
                        # print(f'{post_text=}')
                        # print(f'{image_url=}')
                        return 'video', post_text, video_url
                case _:
                    # Multiple images. Impossible with current technology.
                    pass
        elif post.type == 'answer':
            parsed_post = tumblr_post.AnswerPost(post)
            post_text = parsed_post.prettify()
            # print(post_text)
            # print('')
            # print('')
            return 'text', post_text

    def _parse_url_(self, url: str):
        url = urlparse(url
                       .replace('/blog/view/', '/')
                       .replace('/post/', '/'))
        possible_blogname = url.netloc.split('.')[0]
        if possible_blogname == 'www':
            return list(filter(None, url.path.split('/')))[:2]
        else:
            return possible_blogname, url.path.replace('/', '')

    def _bridge_thread_(self):
        self.bridge_running = True

        while self.bridge_running:
            try:
                latest_posts = self.tumblr_client.posts(config.blog_name,
                                                        #    type='text',
                                                        limit=5)['posts'][::-1]
            except Exception as e:
                if self.debug:
                    print('Exception when getting latest posts.')
                    print(traceback.format_exc())

            if latest_posts:
                for post in latest_posts:

                    post = DotMap(post)

                    if post.timestamp < self.last_post_time:
                        continue
                    if post.state == 'private':
                        continue

                    post_processed = self._process_post_(post)
                    if post_processed:
                        self._bridge_post_(*post_processed)

            self.last_post_time = int(time())
            sleep(self.update_time)

    def _inline_thread_(self):
        # TODO don't forget `inline_running`
        self.inline_running = True

        # Init
        response = DotMap(json.loads(requests.get(
            f'{self.api_base}/getUpdates').content))
        if response.ok:
            if not response.result:
                # print('Empty update queue. Can\t start inline mode')
                # return
                last_update = 0
            else:
                last_update = response.result[0].update_id
        else:
            print('Can\'t get updates.')

        while self.inline_running:
            sleep(1)
            try:
                response = DotMap(
                    json.loads(
                        requests.get(
                            f'{self.api_base}/getUpdates',
                            params={
                                'offset': last_update + 1,
                                'allowed_updates': '["inline_query"]',
                            }).content))
                if not response.ok:
                    print('Can\'t get updates')
                    continue

                results = response.result
                if not results:
                    continue

                last_update = response.result[-1].update_id
                # print(f'{results=}')
                for result in results:
                    if str(result.inline_query['from'].id) not in self.allowed_users:
                        continue
                    query = result.inline_query.query
                    if not 'tumblr.com/' in query:
                        continue
                    blog, post_id = self._parse_url_(query)
                    if not blog or not post_id:
                        continue
                    post = self.tumblr_client.posts(
                        blog, id=post_id)['posts'][0]
                    if not post:
                        continue
                    post = self._process_post_(DotMap(post))
                    self._inline_post_(result.inline_query.id, *post)
            except Exception as e:
                print('Exception when getting post inline.')
                print(traceback.format_exc())

    def start(self):
        if self.is_bridge:
            self.thread_bridge = threading.Thread(target=self._bridge_thread_)
            self.thread_bridge.start()
        if self.is_inline:
            self.thread_inline = threading.Thread(target=self._inline_thread_)
            self.thread_inline.start()

    def wait(self):
        if self.inline_running:
            self.thread_inline.join()
        if self.bridge_running:
            self.thread_bridge.join()


if __name__ == '__main__':
    bot = TelegramBot(config)
    bot.start()
    bot.wait()
