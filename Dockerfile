FROM python:3.7-slim-buster as deps

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN apt-get update \
 && apt-get install -y --no-install-recommends gcc build-essential \
 && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt .
RUN pip install --upgrade pip \
 && pip install -r requirements.txt


FROM python:3.7-slim-buster as runtime

WORKDIR /opt/app

RUN apt-get update \
 && apt-get install -y --no-install-recommends git ssh \
 && rm -rf /var/lib/apt/lists/* \
 && chmod g=u /etc/passwd

ENV PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH"

COPY --from=deps /opt/venv /opt/venv

COPY app.py \
     openapi.yaml \
     entrypoint.sh \
     ./

USER 1001
ENTRYPOINT [ "/opt/app/entrypoint.sh" ]
