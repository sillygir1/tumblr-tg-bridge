FROM python:3.11-slim

ENV IS_RUNNING_IN_DOCKER=True

WORKDIR /app
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY *.py ./

CMD ["python", "telegram_bot.py"]