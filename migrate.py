import database as db
from influxdb import InfluxDBClient
s = db.Session()
users = s.query(db.User)
c = InfluxDBClient()
c.create_database('grid')
c.switch_database('grid')
logs = s.query(db.UserLog)
usernames = {}
for user in s.query(db.User):
    usernames[user.id] = user.name
points = [{
        "tags": {"username": usernames[log.user_id]},
        "time": log.time,
        'measurement': 'userlog',
        "fields": {
            "squares": log.squares,
            "units": log.units,
            "farms": log.farms,
            "cities": log.cities,
            "bank": log.bank}}
        for log in logs]
c.write_points(points)
