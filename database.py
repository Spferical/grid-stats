import json
import time
from graphitesend import GraphiteClient, TemplateFormatter


def write_player_data(url, players):
    """ Writes a bunch of player data to the time-series database.

    players is a list of dicts with the key "name" for the player's
    username and another key for each stat we are tracking.

    url is the url for the graphite instance to write to.
    """
    timestamp = int(time.time())
    points = []
    for player in players:
        for stat in player:
            if stat != 'name':
                points.append(('grid.{}.{}'.format(stat, player['name']),
                               player[stat]))
    host, port = url.split(':')
    port = int(port)
    client = GraphiteClient(host, port, formatter=TemplateFormatter("{name}"))
    client.send_list(points, timestamp=timestamp)
