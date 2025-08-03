import pytumblr
import config
import html2text
from urllib.parse import urlparse
import dotmap
import re
import json
import telegramify_markdown

media_url_regex = r'(https?://[^\s)]+?\.tumblr\.com/[^\s]+?\.[a-z0-9]{3,4})'
markdown_url_regex = r'\[(.*)\]\(' + media_url_regex + r'\)'
image_emoji = '🖼'
markdown_image_regex = image_emoji + markdown_url_regex
html_figure_regex = r'<figure class=\"tmblr-full\" data-npf=\"({[^\s]+?})+?\"></figure>'

image_placeholder = '\[image\]'
video_placeholder = '\[video\]'


def format_blog_url(blog: str, *, post_url: str = '', post_id: int = 0):
    blog = blog.replace('-', '\-')
    if post_url:
        return f'[{blog}]({post_url})'
    elif post_id:
        return f'[{blog}]({blog}.tumblr.com/{post_id})'
    else:
        return f'[{blog}]({blog}.tumblr.com)'


class TumblrPostTrail:
    def __init__(self, post_trail):
        self.blog = post_trail.blog.name
        self.id = post_trail.post.id

        self.content = post_trail.content
        self._detect_media_()

        self.content = html2text.html2text(self.content, bodywidth=0)

    def _detect_media_(self):

        # Detect video first, replace it with a video url,
        # html2text can't do figures and will
        # disregard the video otherwise
        figures = re.findall(html_figure_regex, self.content)
        if len(figures) > 1:
            # Multiple media, the final check in
            # this function will catch them
            pass
        elif figures:
            figure = dotmap.DotMap(json.loads(html2text.html2text(
                figures[0], bodywidth=0).strip()))
            if figure.type == 'video':
                video_url = figure.url
                self.content = re.sub(
                    html_figure_regex, f'<a href="{video_url}">video</a>', self.content)

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
            blog_name = post_url.netloc.split('.')[0]
            if blog_name == 'www':
                blog_name = post_url.path.split('/')[-2]
            if blog_name == self.author:
                blog_name = ''
            self.reblog_source = blog_name
        else:
            self.is_reblog = False
        self.trail = [TumblrPostTrail(trail) for trail in post_data.trail]

        self.post_url = post_data.post_url
        self.media_count = sum([len(trail.media) for trail in self.trail])
        self.tags = post_data.tags
        self.blog = post_data.blog_name
        self.post_url = post_data.post_url
        self.parent_post_url = post_data.parent_post_url
        self.timestamp = post_data.timestamp

    def _format_header_(self) -> str:
        header_buffer = ''
        if self.is_reblog:
            header_buffer += f'{format_blog_url(self.blog, post_url=self.post_url)} 🔁 '
            # header_buffer += f' []({self.post_url}) '
            if self.reblog_source:
                header_buffer += f' {format_blog_url(self.reblog_source, post_url=self.parent_post_url)}'
            header_buffer += '\n'
        return header_buffer

    def _format_trail_(self, start: int = 0):
        trail_buffer = ''
        for trail in self.trail[start:]:
            content = telegramify_markdown.markdownify(
                trail.content.replace('\n\n', '\n'))
            trail_buffer += f'{format_blog_url(trail.blog, post_id=trail.id)}:\n{content}\n'
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
            post_data.question, bodywidth=0).replace('\n\n', '\n')
        self.answer = html2text.html2text(
            post_data.answer, bodywidth=0).replace('\n\n', '\n')

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
        question = telegramify_markdown.markdownify(
            self.question.replace("\n", "\n>"))
        post_buffer += f'>{question}\n'

        post_buffer += f'[{self.trail[0].blog}]({self.trail[0].blog}.tumblr.com)'
        post_buffer += ' answered:\n'
        answer = html2text.html2text(
            self.trail[0].content, bodywidth=0).replace('\n\n', '\n')
        post_buffer += f'{telegramify_markdown.markdownify(answer)}\n'

        if len(self.trail) == 1:
            return post_buffer

        post_buffer += self._format_trail_(1)

        return post_buffer


class MediaPost(TextPost):

    def prettify(self):
        if self.media_count != 1:
            return '', ''

        prettified_text = super().prettify()
        image_url = re.findall(
            self.media_regex, prettified_text)[0][1]

        prettified_text = re.sub(
            self.media_regex, self.media_placeholder, prettified_text)
        prettified_text = prettified_text.replace(
            f'{self.media_placeholder}ALT', self.media_placeholder)

        if prettified_text.strip().endswith(self.media_placeholder):
            prettified_text = prettified_text.replace(
                self.media_placeholder, '')
        return prettified_text, image_url


class ImagePost(MediaPost):
    media_regex = markdown_image_regex
    media_placeholder = image_placeholder


class VideoPost(MediaPost):
    media_regex = markdown_url_regex
    media_placeholder = video_placeholder


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
