FROM python:3.8-alpine

#PYTHONUNBUFFERED ensures that output are sent straight to terminal
ENV PYTHONUNBUFFERRED 1 



COPY ./requirements.txt /requirements.txt
RUN python3 -m pip install --upgrade pip
RUN apk add --update --no-cache postgresql-client jpeg-dev
RUN apk add --update --no-cache --virtual .tmp-build-deps  \
        gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev

RUN pip install -r /requirements.txt
RUN apk del .tmp-build-deps

RUN mkdir /csv_model_files
WORKDIR /csv_model_files
COPY ./csv_model_files /csv_model_files

RUN mkdir /app
WORKDIR /app
COPY ./app /app


RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static
RUN adduser -D user
RUN chown -R user:user /vol/
RUN chmod -R 755 /vol/web
USER user

