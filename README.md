# Tumblr to Telegram crossposter

The whole project is WIP and so is this readme.

>[!IMPORTANT]
> Needs a `config.py` file containing `blog_name` and `blog_alias` strings, a `tumblr_secret` iterable containing secret stuff (you can get the tuple from the [Tumblr API Console](https://api.tumblr.com/console/calls/user/info)), `telegram_api_key` string (obtainable from [@BotFather](https://t.me/BotFather)) and a `telegram_chat_id` string.

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
```
