import requests
import json
from influxdb import InfluxDBClient
from dateutil import parser


c = InfluxDBClient()
c.switch_database('grid')

kairosdb_server = "http://localhost:8080"

for day in range(1000, 0, -1):
    queue = []
    data = c.query("select * from userlog " +
                   "where time >= now() - {}d ".format(day) +
                   "and time <= now() - {}d;".format(day-1))
    for data in data:
        for x in data:
            time = int(parser.parse(x['time']).timestamp() * 1000)
            for key in x:
                if key not in ['time', 'username'] and x[key] is not None:
                    queue.append({
                        "name": key,
                        "datapoints": [
                            [time, x[key]],
                        ],
                        'tags': {'username': x['username']},
                    })
                    if len(queue) > 10:
                        response = requests.post(
                            kairosdb_server + "/api/v1/datapoints",
                            json.dumps(queue))
                        if response.text:
                            # possibly an error?
                            print(queue)
                            print(response.text)
                        queue = []
