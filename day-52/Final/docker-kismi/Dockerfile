FROM python:3.13-slim

RUN useradd --create-home --uid 10001 appuser \
    && mkdir -p /lab/src /lab/runtime \
    && chown appuser:appuser /lab/runtime

WORKDIR /lab/src

COPY app.py /lab/src/app.py

USER appuser

CMD ["python", "/lab/src/app.py"]
