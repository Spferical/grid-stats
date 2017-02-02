From python:2-onbuild

RUN apt-get update && apt-get -y install cron

ADD crontab /etc/cron.d/gridstats-cron

RUN chmod 0644 /etc/cron.d/gridstats-cron

RUN touch /var/log/cron.log

CMD cron && /usr/bin/tail -F /var/log/cron.log
