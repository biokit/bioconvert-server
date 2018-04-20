#!/bin/sh

cd /code

# wait for RabbitMQ server to start
sleep 10

# run Celery worker for our project bioconvertserver with Celery configuration stored in Celeryconf
su -m myuser -c "celery worker -A bioconvertserver.celeryconf -Q default -n default@%h"
