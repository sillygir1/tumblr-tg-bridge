# Tumblr to Telegram bridge

The whole project is WIP and so is this readme.

## Usage

- Create a `.env` file as in `.env_example`.

- Run docker container
    ```sh
    docker run -d --name tumblr-bridge --env-file=/path/to/.env ghcr.io/sillygir1/tumblr-tg-bridge:main
    ```

## TODO

- Bridge:
    - [x] Text posts
    - [ ] Asks
        - [x] Text-only
        - [x] With image attached
    - [x] Single image posts
    - [x] Video posts
    - [ ] GIFs
- Inline mode:
    - [x] Text posts
    - [ ] Asks
        - [x] Text-only
        - [x] With image attached
    - [ ] Image posts
        - [x] On mobile
        - [ ] In tdesktop
    - [ ] Video posts
    - [ ] GIFs
