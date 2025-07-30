# Tumblr to Telegram crossposter

The whole project is WIP and so is this readme.

>[!IMPORTANT]
> Needs a `config.py` file containing `blog_name` string and a `tumblr_secret` iterable containing secret stuff (you can get the tuple from the [Tumblr API Console](https://api.tumblr.com/console/calls/user/info)).

```python
blog_name = username

tumblr_secret = (
    consumer_key,
    consumer_secret,
    oauth_token,
    oauth_secret
)

```