FROM python:3.10

RUN apt-get update && apt-get install -y netcat-openbsd && apt-get clean

WORKDIR /opt/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV UWSGI_PROCESSES 1
ENV UWSGI_THREADS 16
ENV UWSGI_HARAKIRI 240
ENV DJANGO_SETTINGS_MODULE 'example.settings'

COPY ./run_uwsgi.sh ./run_uwsgi.sh
COPY requirements.txt requirements.txt
COPY uwsgi/uwsgi.ini uwsgi.ini


# mkdir -p создает директории только в том случае, если они еще не существуют,
# веб-серверы (например, Nginx или Apache) ожидают, что статические файлы будут размещены в определенных директориях.
RUN  mkdir -p /var/www/static/ \
     && mkdir -p /var/www/media/ \
     && mkdir -p /opt/app/static/ \
     && mkdir -p /opt/app/media/ \
     && pip install --upgrade pip \
     && pip install --no-cache-dir -r requirements.txt

COPY . .

COPY ./static /var/www/static

EXPOSE 8000
RUN chmod +x ./run_uwsgi.sh
ENTRYPOINT ["./run_uwsgi.sh"]
