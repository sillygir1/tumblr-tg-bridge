import pytumblr
import config
import html2text
from urllib.parse import urlparse
import dotmap
import re
import telegram
import telegramify_markdown

media_url_regex = r"(https?://[^\s)]+\.[a-z]{3,4})"


def format_blog_url(blog: str):
    blog = blog.replace('-', '\-')
    return f'[{blog}]({blog}.tumblr.com)'


class TumblrPostTrail:
    def __init__(self, post_trail):
        self.blog = post_trail.blog.name
        self.content = html2text.html2text(post_trail.content, bodywidth=0)
        self._detect_media_()

    def _detect_media_(self):
        self.media = re.findall(media_url_regex, self.content)
        if self.media == []:
            return False
        return True


class TumblrPost:
    def __init__(self, post_data):

        self.author = post_data.trail[-1].blog['name']

        if 'parent_post_url' in post_data.keys():
            self.is_reblog = True
            post_url = urlparse(post_data.parent_post_url)
            # print(f'{post_url=}')
            blog_name = post_url.netloc.split('.')[0]
            if blog_name == 'www':
                blog_name = post_url.path.split('/')[-2]
            if blog_name == self.author:
                blog_name = ''
            self.reblog_source = blog_name
        else:
            self.is_reblog = False
        self.trail = [TumblrPostTrail(trail) for trail in post_data.trail]

        self.media_count = sum([len(trail.media) for trail in self.trail])
        self.tags = post_data.tags
        self.blog = post_data.blog_name
        self.timestamp = post_data.timestamp

    def _format_header_(self) -> str:
        header_buffer = ''
        if self.is_reblog:
            header_buffer += f'{format_blog_url(config.blog_name)} 🔁'
            if self.reblog_source:
                header_buffer += f' {format_blog_url(self.reblog_source)}'
            header_buffer += '\n'
        return header_buffer

    def _format_trail_(self, start: int = 0):
        trail_buffer = ''
        for trail in self.trail[start:]:
            content = telegramify_markdown.markdownify(
                trail.content.replace('\n\n', '\n'))
            trail_buffer += f'{format_blog_url(trail.blog)}:\n{content}\n'
        return trail_buffer

    def _format_tags_(self):
        tag_buffer = ''
        for tag in self.tags:
            tag = telegramify_markdown.markdownify(tag)
            tag_buffer += (f'[\#{tag}](tumblr.com/tagged/{tag}) ')
        return tag_buffer


class TextPost(TumblrPost):
    def prettify(self):
        post_buffer = ''

        post_buffer += self._format_header_()
        post_buffer += self._format_trail_()
        post_buffer += self._format_tags_()

        return post_buffer


class AnswerPost(TumblrPost):
    def __init__(self, post_data):
        super().__init__(post_data)
        self.content = ''
        self.asking_name = post_data.asking_name
        self.question = html2text.html2text(
            post_data.question).replace('\n\n', '\n')
        self.answer = html2text.html2text(
            post_data.answer).replace('\n\n', '\n')

    def prettify(self):
        post_buffer = ''
        post_buffer += self._format_header_()
        if self.asking_name == '>Anonymous':
            post_buffer += f'{self.asking_name}'
        else:
            post_buffer += f'[{self.asking_name}]({self.asking_name}.tumblr.com)'
        post_buffer += ' asked:\n'
        if self.question.endswith('\n'):
            self.question = self.question.removesuffix('\n')
        post_buffer += f'>{telegramify_markdown.markdownify(self.question.replace("\n", "\n>"))}\n'

        post_buffer += f'[{self.trail[0].blog}]({self.trail[0].blog}.tumblr.com)'
        post_buffer += ' answered:\n'
        answer = html2text.html2text(
            self.trail[0].content).replace('\n\n', '\n')
        post_buffer += f'{telegramify_markdown.markdownify(answer)}\n'

        if len(self.trail) == 1:
            return post_buffer

        post_buffer += self._format_trail_(1)

        return post_buffer


class ImagePost(TextPost):
    ...


if __name__ == '__main__':
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
        print(f'{tumblr_post.tags=}')

        print('')
