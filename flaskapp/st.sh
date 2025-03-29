#!/bin/bash

# Запускаем сервер в фоне
gunicorn --bind 127.0.0.1:5000 wsgi:app & APP_PID=$!
sleep 10  # Даем серверу больше времени на запуск

# Запускаем тесты
echo "Starting client tests..."
python3 client.py
APP_CODE=$?

# Останавливаем сервер
echo "Stopping server..."
kill -TERM $APP_PID
wait $APP_PID

# Выходим с кодом клиента
echo "Client exit code: $APP_CODE"
exit $APP_CODE