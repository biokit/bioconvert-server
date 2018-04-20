#!/bin/bash

cd /code

source resources/tool_shed.sh

msg_info "Applying database migrations"
python manage.py migrate

msg_info "Compilling localization (.po -> .mo)"
python manage.py compilemessages

STATIC_ROOT_DIR=$(python manage.py shell -c "from django.conf import settings; print(settings.STATIC_ROOT)")
msg_info "Creating static root at $STATIC_ROOT_DIR"
if [ "$STATIC_ROOT_DIR" != "" ]; then
    mkdir -p $STATIC_ROOT_DIR
    chmod 777 $STATIC_ROOT_DIR
else
    msg_warning "settings.STATIC_ROOT missing, passed"
fi

msg_info "Collecting static files"
python manage.py collectstatic --noinput

msg_info "Compressing css files"
if [ "$(pip freeze | grep csscompressor | wc -l )" == "1" ]; then
    for css_file in $(find $(python manage.py shell -c "from django.conf import settings; print(settings.STATIC_ROOT)") -name \*.css -print | grep -v .min.css); do
        ls -laH $css_file
        d=$(date -R -r $css_file)
        python -m csscompressor $css_file -o $css_file;
        touch -d "$d" $css_file
    done
else
    msg_warning "csscompressor missing, passed"
fi

MEDIA_ROOT_DIR=$(python manage.py shell -c "from django.conf import settings; print(settings.MEDIA_ROOT)")
msg_info "Creating media root at $MEDIA_ROOT_DIR"
if [ "$MEDIA_ROOT_DIR" != "" ]; then
    mkdir -p $MEDIA_ROOT_DIR
    chmod 777 $MEDIA_ROOT_DIR
else
    msg_warning "settings.MEDIA_ROOT missing, passed"
fi

#Setting up cron tasks
msg_info "Registering cron tasks"
if [ "$(pip freeze | grep django-crontab | wc -l )" == "1" ]; then
    python manage.py crontab add
    service cron start
else
    msg_warning "django-crontab missing, passed"
fi

if [ "$1" == "do_not_start" ]; then
    msg_info "Entrypoint have been run successfully, we are not starting the project as requested"
elif [ "$1" == "django" ]; then
    echo "Running at http://$(ip addr show | tail -n 2 | head -n 1 | cut -d/ -f1 | cut -d' ' -f6):8030"
    exec python manage.py runserver 0.0.0.0:8030
elif [ "$1" == "gunicorn" ]; then
    echo "Running at https://$(ip addr show | tail -n 2 | head -n 1 | cut -d/ -f1 | cut -d' ' -f6)"
    if [ "$(pip freeze | grep gunicorn | wc -l )" == "0" ]; then
        msg_error "gunicorn not installed, we will install it but you should add it to your requirements.txt, it will be installed once for all during the build"
        pip install gunicorn --no-cache-dir
    fi
    exec gunicorn composeexample.wsgi -b 0.0.0.0:443 --certfile certs/$CERT_NAME.crt --keyfile=certs/$CERT_NAME.key
elif [ "$1" == "makemessages" ]; then
    exec python manage.py makemessages -l en --no-location
else
    echo "Running at https://$(ip addr show | tail -n 2 | head -n 1 | cut -d/ -f1 | cut -d' ' -f6)"
    rm -f /var/run/apache2/apache2.pid
    rm -rf /run/httpd/* /tmp/httpd*
    chmod -R 777 /tmp/* 2>/dev/null
    echo "ServerName ${SERVER_NAME}" >> /etc/apache2/apache2.conf
    exec "$@"
fi