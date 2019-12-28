#!/usr/bin/env python3
from bs4 import BeautifulSoup
import re
import argparse
from datetime import datetime, timedelta
from urllib.request import urlopen
import pause
import database


NUM_COLUMNS_IN_GRID_TABLE = 22


def get_ranks_table():
    page = urlopen("http://codeelf.com/games/the-grid-2/grid/ranks/")
    soup = BeautifulSoup(page, "html.parser")
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
        'IPC': row[16],
        'kills': row[17],
        'slain': row[18],
        'loan': row[19],
    }
    return player


def update_database(kairosdb_url):
    data = get_ranks_table()
    players = [parse_player(row) for row in data]
    database.write_player_data(kairosdb_url, players)


def main():
    parser = argparse.ArgumentParser(
        description="Web application to graph stats of The Grid over time")
    parser.add_argument('--graphite_url', default="localhost:2003")
    args = vars(parser.parse_args())

    while True:
        # run every hour
        dt = datetime.now() + timedelta(hours=1)
        dt = dt.replace(minute=0, second=0, microsecond=0)
        print("waiting until {}".format(dt))
        pause.until(dt)
        print('[{}] reading stats...'.format(datetime.now()))
        update_database(args['graphite_url'])
        print('[{}] done'.format(datetime.now()))


if __name__ == '__main__':
    main()
