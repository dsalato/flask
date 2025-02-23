gunicorn --bind 127.0.0.1:5000 wsgi:app & APP_PID=$!
sleep 5
python client.py
kill -TERM $APP_PID
exit 0
