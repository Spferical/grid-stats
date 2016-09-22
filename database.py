import requests
import json
import datetime


KAIROSDB_SERVER = "http://localhost:8080"

def write_player_data(players):
    """ Writes a bunch of player data to the time-series database.

    players is a list of dicts with the key "name" for the player's
    username and another key for each stat we are tracking."""
    time = int(datetime.datetime.now().timestamp() * 1000)
    points = []
    for player in players:
        for stat in player:
            if stat != 'name':
                points.append({
                    "name": stat,
                    "datapoints": [
                        [time, player[stat]],
                    ],
                    "tags": {"username": player["name"]},
                })
    write_points(points)


def write_points(points):
    """
    Takes a list of points of the form:
    {
        "name": "(metric_name)",
        "datapoints": [
            [(timestamp_in_ms_since_epoch), (value)]
        ],
        "tags": {"username": "(username)"}
    }

    And sends it over to KairosDB.
    """
    response = requests.post(
        KAIROSDB_SERVER + "/api/v1/datapoints", json.dumps(points))
    if not 200 <= response.status_code < 300:
        print("Something happened when writing points " + json.dumps(points) +
                "\n" + response.text)
        print(response.status_code)
