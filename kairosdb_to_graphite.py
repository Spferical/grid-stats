import sys
import json
from time import sleep
from graphitesend import GraphiteClient, TemplateFormatter, GraphiteSendException

client = GraphiteClient('localhost', 2003, formatter=TemplateFormatter("{name}"))

for line in sys.stdin:
    data = json.loads(line)
    stat = data['name']
    if 'username' not in data['tags']:
        continue
    username = data['tags']['username']
    metric = 'grid.{}.{}'.format(stat, username)
    print(metric)
    for pt in data['datapoints']:
        (timestamp_ms, value, _) = pt
        timestamp = int(timestamp_ms / 1000)
        while True:
            try:
                client.send(metric, value, timestamp=timestamp)
                break
            except GraphiteSendException:
                sleep(60)

