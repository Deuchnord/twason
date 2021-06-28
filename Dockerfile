FROM python:3.9-slim

RUN useradd --create-home --shell /bin/bash bot

WORKDIR /home/bot

ENV PATH="/home/bot:${PATH}"

# Prepare environment
RUN python -m pip install --upgrade pip
RUN pip install pipenv
COPY Pipfile.lock .
RUN pipenv sync && pipenv run pip freeze > requirements.txt

# Add files
RUN pip install -r requirements.txt && mkdir config
COPY _twitchbot/ _twitchbot/
COPY bot.py .

USER bot

CMD ["python", "bot.py", "--config=config/config.json"]
