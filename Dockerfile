ARG PYTHON_VERSION=3.9.9
FROM python:${PYTHON_VERSION}-alpine3.15

ARG ENVIRONMENT
ENV APP_ENV=${ENVIRONMENT:-local}

# setup working directory
WORKDIR /opt/application/

# install application executable package/code
COPY . .

# install dependencies & setup directories
RUN apk update \
    && apk add libpq \
    && apk add --no-cache --virtual .build-deps gcc python3-dev musl-dev postgresql-dev \
    && apk add jpeg-dev zlib-dev libjpeg \
    && pip install --no-cache-dir -r requirements.txt \
    && apk del .build-deps \
    && rm -rf /var/cache/apk/* \
    && mkdir /var/log/application/

# declare exposed ports
EXPOSE 8080

# command to run application
CMD ["gunicorn", "app.main:application", "-b", "0.0.0.0:8080"]