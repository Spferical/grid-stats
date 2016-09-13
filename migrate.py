import database as db
from influxdb import InfluxDBClient
from time import sleep
s = db.Session()
users = s.query(db.User)
c = InfluxDBClient()
c.switch_database('grid')
logs = s.query(db.UserLog).yield_per(100)
count = logs.count()
print(count, "logs")

usernames = {}
for user in s.query(db.User):
    usernames[user.id] = user.name

points = []

i=0
for log in logs:
    i += 1
    points.append({
        "tags": {"username": usernames[log.user_id]},
        "time": log.time,
        'measurement': 'userlog',
        "fields": {
            "squares": log.squares,
            "units": log.units,
            "farms": log.farms,
            "cities": log.cities,
            "bank": log.bank}})

    if len(points) >= 100:
        worked = False
        while not worked:
            try:
                c.write_points(points)
                worked = True
            except:
                print("Exception! Waiting a minute.")
                sleep(60)
        points = []
        print(i, '/', count)
        sleep(1)
c.write_points(points)
