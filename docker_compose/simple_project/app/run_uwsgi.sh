#!/usr/bin/env bash

# если где-то возникает ошибка процесс выполнения останавливается
set -e
# www-data — это системный пользователь и группа, 
# которые используются веб-серверами, такими как Nginx 
# и Apache, для выполнения своих задач. Это своего рода 
# идентификатор, указывающий, что определённые ресурсы 
# (файлы, директории) могут использоваться этими приложениями.
chown www-data:www-data /var/log
echo "Waiting for database to be ready..."
while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
done 
echo "Database is ready. Proceeding with migrations..."

python manage.py migrate

python manage.py collectstatic --noinput

exec uwsgi --strict --ini ./uwsgi/uwsgi.ini
