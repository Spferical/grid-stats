#!/usr/bin/env python2
from bottle import route, run, static_file, template
from bs4 import BeautifulSoup
import re
import os
import argparse
import database
import pandas as pd
import numpy as np
import bearcart
import datetime
try:  # Python 3
    from urllib.request import urlopen
except ImportError:  # Python 2
    from urllib import urlopen

NUM_COLUMNS_IN_GRID_TABLE = 22

stats = ("units", "farms", "cities", "squares", "bank")
intervals = ('month', 'week', 'day')


# one page for each interval
@route('/<interval:re:(%s)>' % '|'.join(intervals))
def show_graphs(interval):
    return template('template.tpl', stats=stats, interval=interval)

@route('/')
def index():
    return static_file('index.html', os.getcwd())

@route(r'/<filename:re:.+\.(html|css|svg|js|json)>')
def get_file(filename):
    return static_file(filename, os.getcwd())


def get_ranks_table():
    page = urlopen("http://codeelf.com/games/the-grid-2/grid/ranks/")
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
        'rank': row[0],
        'name': row[1],
        'squares': row[2],
        'units': row[3],
        'clout': row[4],
        'gold': row[5],
        'silver': row[6],
        'farms': row[7],
        'cities': row[8],
        'rebels': row[9],
        'bank': row[10],
        'wizards': row[11],
        'energy': row[12],
        'perm': row[13],
        'wipes': row[14],
        'wiped': row[15],
        'IPC': row[16],
        'kills': row[17],
        'slain': row[18],
        'loan': row[19],
        'trait': row[20],
        'activity': row[21],
    }
    return player


def update_database():
    data = get_ranks_table()
    players = [parse_player(row) for row in data]
    database.add_data(players)


def set_foregroundcolor(ax, color):
    '''For the specified axes, sets the color of the frame, major ticks,
    tick labels, axis labels, title and legend
    From https://gist.github.com/jasonmc/1160951
    '''
    for tl in ax.get_xticklines() + ax.get_yticklines():
        tl.set_color(color)
    for spine in ax.spines:
        ax.spines[spine].set_edgecolor(color)
    for tick in ax.xaxis.get_major_ticks():
        tick.label1.set_color(color)
    for tick in ax.yaxis.get_major_ticks():
        tick.label1.set_color(color)
    ax.axes.xaxis.label.set_color(color)
    ax.axes.yaxis.label.set_color(color)
    ax.axes.xaxis.get_offset_text().set_color(color)
    ax.axes.yaxis.get_offset_text().set_color(color)
    ax.axes.title.set_color(color)
    lh = ax.get_legend()
    if lh != None:
        lh.get_title().set_color(color)
        lh.legendPatch.set_edgecolor('none')
        labels = lh.get_texts()
        for lab in labels:
            lab.set_color(color)
    for tl in ax.get_xticklabels():
        tl.set_color(color)
    for tl in ax.get_yticklabels():
        tl.set_color(color)


def set_backgroundcolor(ax, color):
    '''Sets the background color of the current axes (and legend).
         Use 'None' (with quotes) for transparent. To get transparent
         background on saved figures, use:
         pp.savefig("fig1.svg", transparent=True)
         From https://gist.github.com/jasonmc/1160951
     '''
    ax.patch.set_facecolor(color)
    lh = ax.get_legend()
    if lh != None:
        lh.legendPatch.set_facecolor(color)


def update_graphs():
    for interval in intervals:
        update_graphs_for_interval(interval)


def update_graphs_for_interval(interval):
    if interval == 'all':
        min_time = datetime.datetime.min
    elif interval == 'month':
        min_time = datetime.datetime.now() -  datetime.timedelta(days=30)
    elif interval == 'week':
        min_time = datetime.datetime.now() -  datetime.timedelta(days=7)
    elif interval == 'day':
        min_time = datetime.datetime.now() -  datetime.timedelta(days=1)

    session = database.Session()
    users = session.query(database.User)
    # only show users who have played the game in the time interval
    # so, as an initial pass, create a list with only these users
    active_users = []
    for user in users:
        data = session.query(database.UserLog).filter(
            database.UserLog.user_id == user.id,
            database.UserLog.time >= min_time)
        if len(data.all()) != 0:
            max_units = max([log.units for log in data])
        else:
            max_units = 0
        if max_units != 0:
            active_users.append(user)

    users = active_users

    data = session.query(database.UserLog).filter(
        database.UserLog.time >= min_time)

    start_time = data[0].time
    end_time = data[-1].time

    for stat in stats:
        full_data = {}
        for i, user in enumerate(users):
            data = session.query(database.UserLog).filter(
                database.UserLog.user_id == user.id,
                database.UserLog.time >= min_time)
            xvals = [log.time for log in data]
            yvals = [log.__getattribute__(stat) for log in data]
            xvals = pd.DatetimeIndex(xvals)
            ns1hr = 60 * 60 * 1000000000  # 1 hour in nanoseconds
            # round to nearest minute
            xvals = np.array(xvals, dtype='datetime64[h]')
            series = pd.Series(yvals, index=xvals)
            # remove duplicate NaNs
            series = series.groupby(series.index).first()
            full_data[user.name] = series
        frame = pd.DataFrame(full_data)
        vis = bearcart.Chart(frame)

        html_path = '%s_%s.html' % (stat, interval)
        data_path = '%s_%s.json' % (stat, interval)
        vis.create_chart(html_path=html_path, data_path=data_path)
    session.close()


def main():
    parser = argparse.ArgumentParser(
        description="Web application to graph stats of The Grid over time")
    subparsers = parser.add_subparsers(dest="command")
    server_parser = subparsers.add_parser("server", help="run web server")
    update_database_parser = subparsers.add_parser(
        "update-database",
        help="update the grid stats database")
    create_database_parser = subparsers.add_parser(
        "create-database",
        help="create the grid stats database")
    update_graphs_parser = subparsers.add_parser(
        "update-graphs",
        help="update the grid stats graphs")
    args = vars(parser.parse_args())
    if args["command"] == "server":
        run_server()
    elif args["command"] == "update-database":
        update_database()
        update_graphs()
    elif args["command"] == "create-database":
        database.create_database()
    elif args["command"] == "update-graphs":
        update_graphs()


def run_server():
    run(host='0.0.0.0', port=8082)


if __name__ == '__main__':
    main()
