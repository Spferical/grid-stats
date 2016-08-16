import database as db
from influxdb import InfluxDBClient
s = db.Session()
users = s.query(db.User)
c = InfluxDBClient()
c.switch_database('grid')
logs = s.query(db.UserLog).yield_per(100)

usernames = {}
for user in s.query(db.User):
    usernames[user.id] = user.name

points = []

for log in logs:
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
        c.write_points(points)
        points = []
c.write_points(points)
