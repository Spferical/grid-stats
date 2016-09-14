import requests
import json
from influxdb import InfluxDBClient
from dateutil import parser
import datetime


c = InfluxDBClient()
c.switch_database('grid')

kairosdb_server = "http://localhost:8080"

now = datetime.datetime.now()
for day in range(1000, 0, -1):
    time1 = (now - datetime.timedelta(days=day)).isoformat('T') + 'Z'
    time2 = (now - datetime.timedelta(days=day - 1)).isoformat('T') + 'Z'
    queue = []
    data = c.query("select * from userlog " +
                   "where time >= '{}' ".format(time1) +
                   "and time <= '{}';".format(time2))
    print("Migrating data from {}-{} days ago".format(day-1, day))
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
                    if len(queue) > 100:
                        response = requests.post(
                            kairosdb_server + "/api/v1/datapoints",
                            json.dumps(queue))
                        if response.text:
                            # possibly an error?
                            print(queue)
                            print(response.text)
                        queue = []
