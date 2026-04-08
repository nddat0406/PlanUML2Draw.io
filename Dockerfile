FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    JAVA_TOOL_OPTIONS="-Djava.awt.headless=true"

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        default-jre-headless \
        fontconfig \
        libfreetype6 \
        libharfbuzz0b \
        libpng16-16 \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt requirements-web.txt setup.py ./
COPY src ./src
COPY templates ./templates
COPY static ./static
COPY web_app.py ./

RUN pip install --no-cache-dir -r requirements-web.txt \
    && pip install --no-cache-dir -e .

EXPOSE 10000

CMD ["sh", "-c", "waitress-serve --host 0.0.0.0 --port ${PORT:-10000} web_app:app"]
