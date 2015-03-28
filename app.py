#!/usr/bin/env python3
from bottle import route, run
from bs4 import BeautifulSoup
import urllib.request
import re
import argparse
import database
import matplotlib.pyplot as plt
from matplotlib import colors
import matplotlib.cm as cmx

NUM_COLUMNS_IN_GRID_TABLE = 22

@route('/')
def index():
    return '<strong>Hello world!</strong>'


def get_ranks_table():
    page = urllib.request.urlopen("http://codeelf.com/games/the-grid-2/grid/ranks/")
    soup = BeautifulSoup(page)
    data = []
    for row in soup.findAll("tr"):
        all_tds = row.findAll("td")
        data_row = []
        for td in all_tds:
            span = td.find("span")
            if span:
                data_row.append(span.string)
            else:
                val = td.renderContents().strip()
                num = parse_number(val)
                if num is not None:
                    data_row.append(num)
                else:
                    data_row.append(val)
        if len(data_row) == NUM_COLUMNS_IN_GRID_TABLE:
            data.append(data_row)
    return data


def parse_number(x):
    if x == b'NA':
        return 0
    try:
        # remove commas from numbers and try parsing as float
        x = float(re.sub(b"[^\d\.]", b"", x))
        if x.is_integer():
            x = int(x)
        return x
    except ValueError:
        pass
    except TypeError:
        pass


def parse_player(row):
    player = {
        'rank' : row[0],
        'name' : row[1],
        'squares' : row[2],
        'units' : row[3],
        'clout' : row[4],
        'gold' : row[5],
        'silver' : row[6],
        'farms' : row[7],
        'cities' : row[8],
        'rebels' : row[9],
        'bank' : row[10],
        'wizards' : row[11],
        'energy' : row[12],
        'perm' : row[13],
        'wipes' : row[14],
        'wiped' : row[15],
        'IPC' : row[16],
        'kills' : row[17],
        'slain' : row[18],
        'loan' : row[19],
        'trait' : row[20],
        'activity' : row[21],
    }
    return player


def update_database():
    data = get_ranks_table()
    players = [parse_player(row) for row in data]
    database.add_data(players)


def update_graphs():
    session = database.Session()
    users = session.query(database.User)
    fig = plt.figure(figsize=(10, 7.5))
    ax = fig.add_subplot(111)
    cmap = plt.get_cmap('Dark2')
    c_norm = colors.Normalize(vmin=0, vmax=1)
    scalar_map = cmx.ScalarMappable(norm=c_norm, cmap=cmap)
    # only show users who have played the game in the time interval
    # so, as an initial pass, create a list with only these users
    active_users = []
    for user in users:
        data = session.query(database.UserLog).filter_by(user_id=user.id)
        max_units = max([log.units for log in data])
        if max_units != 0:
            active_users.append(user)

    users = active_users

    for stat in ("units", "farms", "cities", "squares"):
        plt.title(stat.capitalize())
        plt.ylabel(stat.capitalize())
        plt.xlabel("Time")
        min_time = max_time = None
        for i, user in enumerate(users):
            data = session.query(database.UserLog).filter_by(user_id=user.id)
            if min_time is None or data[0].time < min_time:
                min_time = data[0].time
            if max_time is None or data[-1].time > max_time:
                max_time = data[-1].time
            xvals = [log.time for log in data]
            yvals = [log.__getattribute__(stat) for log in data]
            plt.plot(xvals, yvals, label=user.name,
                    color=scalar_map.to_rgba(i / len(users)))

        ax.set_xlim(min_time, max_time)
        plt.legend(ncol=2, loc=2)
        plt.savefig('%s.svg' % stat)
        fig.clf()

    session.close()


def main():
    parser = argparse.ArgumentParser(
        description="Web application to graph stats of The Grid over time")
    subparsers = parser.add_subparsers(dest="command")
    server_parser = subparsers.add_parser(
        "server", help="run web server")
    update_database_parser = subparsers.add_parser(
        "update-database", help="update the grid stats database")
    create_database_parser = subparsers.add_parser(
        "create-database", help="create the grid stats database")
    args = vars(parser.parse_args())
    if args["command"] == "server":
        run_server()
    elif args["command"] == "update-database":
        update_database()
        update_graphs()
    elif args["command"] == "create-database":
        database.create_database()


def run_server():
    run(host='localhost', port=8082)


if __name__ == '__main__':
    main()
