From python:3-alpine

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt

COPY *.py *.sh /usr/src/app/

ENV GRAPHITE_URL graphite:2003

CMD python3 /usr/src/app/app.py --graphite_url $GRAPHITE_URL
