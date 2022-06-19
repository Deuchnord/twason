FROM python:3.9-slim

RUN useradd --create-home --shell /bin/bash bot

WORKDIR /home/bot

ENV PATH="/home/bot:${PATH}"

# Prepare environment
RUN python -m pip install --upgrade pip
RUN pip install poetry

COPY pyproject.toml .
COPY poetry.lock .

COPY twason/ twason/

# Install project
RUN poetry install && \
    poetry build && \
    pip install dist/*.whl

RUN mkdir config

USER bot

CMD ["python", "-m", "twason", "--config=config/config.json"]
