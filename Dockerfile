FROM python:3.12-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PICSHELF_IMAGES_DIR=/data/images \
    PORT=8080

WORKDIR /app

RUN addgroup -S picshelf \
    && adduser -S -G picshelf picshelf \
    && mkdir -p /data/images \
    && chown -R picshelf:picshelf /app /data/images

COPY --chown=picshelf:picshelf src/picshelf /app/picshelf

USER picshelf

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "from urllib.request import urlopen; urlopen('http://127.0.0.1:8080/health', timeout=2).read()"

CMD ["python", "-m", "picshelf.server"]
