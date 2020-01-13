FROM python:3.7-slim-buster as deps

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN apt-get update \
 && apt-get install -y --no-install-recommends gcc build-essential

COPY ./requirements.txt .
RUN pip install --upgrade pip \
 && pip install -r requirements.txt

FROM python:3.7-slim-buster as runtime

COPY --from=deps /opt/venv /opt/venv

ENV PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /usr/src/app

RUN addgroup --system user && adduser --system --no-create-home --group user \
 && chown -R user:user /usr/src/app && chmod -R 755 /usr/src/app
USER user

COPY app.py \
     openapi.yaml \
     ./

CMD ["uwsgi", "--http", ":8080", "-w", "app"]