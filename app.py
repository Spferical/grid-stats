#!/usr/bin/env python3
from bottle import route, run
from bs4 import BeautifulSoup
import urllib.request
import re
import argparse

NUM_COLUMNS_IN_GRID_TABLE = 22

@route('/')
def index():
    return '<strong>Hello world!</strong>'


def get_curr_grid_status():
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

def update_database_with_curr_grid_status():
    pass


def main():
    parser = argparse.ArgumentParser(
        description="Web application to graph stats of The Grid over time")
    subparsers = parser.add_subparsers(dest="command")
    server_parser = subparsers.add_parser(
        "server", help="run web server")
    update_database_parser = subparsers.add_parser(
        "update-database", help="update the grid stats database")
    args = vars(parser.parse_args())
    if args["command"] == "server":
        run_server()
    elif args["command"] == "update-database":
        update_database_with_curr_grid_status()

def run_server():
    run(host='localhost', port=8082)

if __name__ == '__main__':
    main()
