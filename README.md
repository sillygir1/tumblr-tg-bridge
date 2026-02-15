# Tumblr to Telegram bridge

The whole project is WIP and so is this readme.

## Usage

- Create a env file with API keys (use `example.env` as reference).

- Create a `compose.yml` referencing `example-compose.yml`:

- Run it with `docker-compose up -d`.


## TODO

- Bridge:
    - [x] Text posts
    - [x] Asks
        - [x] Text-only
        - [x] With image attached
    - [x] Single image posts
    - [x] Video posts
    - [ ] GIFs
- Inline mode:
    - [x] Text posts
    - [x] Asks
        - [x] Text-only
        - [x] With image attached
    - [ ] Image posts
        - [x] On mobile
        - [ ] In tdesktop
    - [ ] Video posts
    - [ ] GIFs
