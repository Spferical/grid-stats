From python:2-onbuild

RUN apt-get update && apt-get -y install cron

ADD crontab /etc/cron.d/gridstats-cron

RUN chmod 0644 /etc/cron.d/gridstats-cron

RUN touch /var/log/cron.log

ENV KAIROSDB_URL http://localhost:8080

CMD env > /root/.profile && tail -f /var/log/cron.log & cron -f
