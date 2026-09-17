FROM python:3.13-slim AS builder

WORKDIR /lab

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt



FROM python:3.13-slim AS runtime

COPY --from=builder /usr/local/ /usr/local/

WORKDIR /lab

COPY src/ ./src/

RUN useradd \
    --create-home \
    --uid 10001 \
    --user-group \
    --shell /usr/sbin/nologin \
    appuser \
    && mkdir -p /lab/runtime \
    && chown appuser:appuser /lab/runtime

USER appuser

CMD ["python","src/check_owner.py","blue-team"]
