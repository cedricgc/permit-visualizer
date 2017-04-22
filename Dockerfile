# https://github.com/docker-library/python/blob/master/3.6/onbuild/Dockerfile
FROM python:3.6-alpine

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /usr/src/app

CMD ["gunicorn", "--config", "gunicorn.conf", "permit_visualizer:app"]
