FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9-slim as base
RUN apt-get update && apt-get install -y wget

ENV PYTHONFAULTHANDLER=1 \
    PYTHONWRITEBYTECODE=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1

WORKDIR /app

FROM base as builder

COPY requirements.txt /app/
RUN python -m venv /venv

# Allow installing dev dependencies to run tests
ENV PATH="/venv/bin:${PATH}" \
    VIRTUAL_ENV="/venv"

RUN . /venv/bin/activate
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

FROM base as final

COPY --from=builder /venv /venv

ENV PATH="/venv/bin:${PATH}" \
    VIRTUAL_ENV="/venv"

COPY . /app/
