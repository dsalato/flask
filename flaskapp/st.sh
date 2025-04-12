#!/bin/bash

gunicorn --bind 127.0.0.1:5000 wsgi:app & APP_PID=$!
sleep 10

echo "Starting client tests..."
python3 client.py
APP_CODE=$?

echo "Stopping server..."
kill -TERM $APP_PID
wait $APP_PID

echo "Client exit code: $APP_CODE"
exit $APP_CODE