# ModelConverterWeb
Web server for model converter

- 启动celery
celery -A tasks worker --pool=solo -l info
celery -A tasks flower --loglevel=INFO --port=5555

- 启动redis
redis-server.exe redis.windows.conf

- 监视redis队列
redis-cli.exe -h 127.0.0.1 -p 9394 -n 1 llen celery