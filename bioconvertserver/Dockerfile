FROM python:3.4
ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
    apt-get install -y \
        nano \
        wget \
        gettext \
        apache2 \
        libapache2-mod-wsgi-py3 \
        python3.4-dev \
        cron \
 && rm -rf /var/lib/apt/lists/*

RUN a2enmod \
        ssl \
        wsgi \
        rewrite \
        expires \
        proxy_http \
 && a2dissite 000-default

RUN mkdir /code
WORKDIR /code

ADD requirements.txt /code/
#RUN pip install --upgrade pip && \
#    pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ./resources/docker-entrypoint.sh /
RUN chmod a+x /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]

COPY ./resources/django.conf /etc/apache2/sites-enabled/django.conf

# create unprivileged user
RUN adduser --disabled-password --gecos '' myuser

ADD . /code/
