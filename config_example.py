# DO NOT SHARE YOUR CONFIG FILE OR API KEYS WITH ANYONE

# Mode options:
# mode = 'inline'
mode = 'bridge'
# mode = 'bridge', 'inline'

# Log to CLI if true
debug = False

telegram_api_key = 'api_key'
api_url = f'https://api.telegram.org/bot{telegram_api_key}'

# Bridge mode config:

blog_name = 'blog_name'
tumblr_secret = (
    'consumer_key',
    'consumer_secret',
    'oauth_token',
    'oauth_token_secret'
)
telegram_chat_id = '1234567890'

# Inline mode config:

# allowed_user_ids = 'all'
allowed_user_ids = (
    '123456789',  # User 1
    '987654321',  # User 2
)
