import pytumblr
import config
import html2text
from urllib.parse import urlparse
import dotmap
import re

url_regex = r"(https?://[^\s)]+\.[a-z]{3,4})"


class TumblrPostTrail:
    def __init__(self, post_trail):
        self.blog = post_trail.blog.name
        self.content = html2text.html2text(post_trail.content)
        self.media_present = self._detect_media_()

    def _detect_media_(self):
        media = re.findall(url_regex, self.content)
        if media == []:
            return False
        self.media = media
        return True


class TumblrPost:
    def __init__(self, post_data):

        self.author = post_data.trail[-1].blog['name']

        if 'parent_post_url' in post_data.keys():
            self.is_reblog = True
            post_url = urlparse(post_data.parent_post_url)
            blog_name = post_url.netloc.split('.')[0]
            if blog_name == 'www':
                blog_name = ''
            self.reblog_source = blog_name
        else:
            self.is_reblog = False
        self.trail = [TumblrPostTrail(trail) for trail in post_data.trail]

        self.media_present = any([trail.media_present for trail in self.trail])
        self.blog = post_data.blog_name
        self.timestamp = post_data.timestamp


class TextPost(TumblrPost):
    ...


class ImagePost(TumblrPost):
    ...


class OtherPost(TumblrPost):
    ...


client = pytumblr.TumblrRestClient(*config.tumblr_secret)

posts = client.posts(config.blog_name)

for post in posts['posts'][:20]:

    post = dotmap.DotMap(post)

    # try:
    tumblr_post = TumblrPost(post)
    # except Exception as e:
    # print('Uwu some ewwow happened')

    print(f'{tumblr_post.is_reblog=}')
    print(f'{tumblr_post.author=}')
    if tumblr_post.is_reblog:
        print(f'{tumblr_post.reblog_source=}')
    for trail in tumblr_post.trail:
        print(f'{trail.blog=}')
        print(f'{trail.content=}')
        print(f'{trail.media_present=}')
        if trail.media_present:
            print(f'{trail.media=}')

    print('')
