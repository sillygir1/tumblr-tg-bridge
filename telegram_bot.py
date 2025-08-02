import config
from dotmap import DotMap
# import os.path
import pytumblr
import requests
from time import time, sleep
import threading
import traceback
import tumblr_post


class TelegramBot:
    def __init__(self, config_file):
        self.is_bridge = 'bridge' in config_file.mode
        self.is_inline = 'inline' in config_file.mode
        self.api_base = config_file.api_url
        self.debug = config_file.debug

        self.bridge_running = False
        self.inline_running = False

        if self.is_bridge:
            self.blog_name = config_file.blog_name
            self.tumblr_client = pytumblr.TumblrRestClient(
                *config_file.tumblr_secret)
            self.chat_id = config_file.telegram_chat_id

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

    def _process_post_(self, post: dict):
        # Reusing old logic here
        post = DotMap(post)

        if post.timestamp < self.last_post_time:
            return
        if post.state == 'private':
            return

        print(f'{post.type=}')
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
                    self._bridge_post_text_(post_text)
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
                        self._bridge_post_image_(post_text, image_url)
                    elif media_url.endswith('.mp4'):
                        parsed_post = tumblr_post.VideoPost(post)
                        post_text, video_url = parsed_post.prettify()
                        # print(f'{post_text=}')
                        # print(f'{image_url=}')
                        self._bridge_post_video_(post_text, video_url)
                case _:
                    # Multiple images. Impossible with current technology.
                    pass
        elif post.type == 'answer':
            parsed_post = tumblr_post.AnswerPost(post)
            post_text = parsed_post.prettify()
            # print(post_text)
            # print('')
            # print('')
            self._bridge_post_text_(post_text)

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
                    self._process_post_(post)

            self.last_post_time = int(time())
            sleep(60)

    def _inline_thread_(self):
        # TODO don't forget `inline_running`
        pass

    def start(self):
        if self.is_bridge:
            self.thread_bridge = threading.Thread(target=self._bridge_thread_)
            self.thread_bridge.start()
        if self.is_inline:
            self.thread_inline = threading.Thread(target=self._inline_thread_)
            self.thread_inline.start()

    def stop(self):
        if self.bridge_running:
            self.bridge_running = False
            self.thread_bridge.join()
        if self.inline_running:
            self.inline_running = False
            self.thread_inline.join()


if __name__ == '__main__':
    bot = TelegramBot(config)
    bot.start()
    input('press ENTER to stop')
    bot.stop()
