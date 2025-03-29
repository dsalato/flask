#!/bin/bash
# Запускаем Gunicorn в фоновом режиме
gunicorn --bind 127.0.0.1:5000 wsgi:app & APP_PID=$!
# Даем серверу время на запуск
sleep 5
echo "Gunicorn process ID: $APP_PID"
# Останавливаем сервер
kill -TERM $APP_PID
echo "Gunicorn process terminated"
exit 0