# Tumblr to Telegram crossposter

The whole project is WIP and so is this readme.

>[!IMPORTANT]
> Needs a `config.py` file containing `blog_name` string, a `tumblr_secret` iterable containing secret stuff (you can get the tuple from the [Tumblr API Console](https://api.tumblr.com/console/calls/user/info)), `telegram_api_key` string (obtainable from [@BotFather](https://t.me/BotFather)), a `telegram_chat_id` string and a `timestamp_file_path` string.

Example `config.py`:

```python
# DO NOT SHARE YOUR CONFIG FILE OR API KEYS WITH ANYONE
blog_name = 'name of a blog'
blog_alias = 'name that will be in tg post'
tumblr_secret = (
    'asdnfbvkjcxzhvjsa',
    'siudfjhgkjfdsvd',
    'asnfskdjkvelfd',
    'cvuhsbfdkjszhvlih'
)

telegram_api_key = '1234567890:asgdyuvcizfnawlvkcvz'
telegram_chat_id = '1234567890'
timestamp_file_path = '/path/to/timestamp/file'
```

## Usage

TODO rewrite this section

- Manual activation: run `telegram_bot.py`
- Automated posting: add it to crontab