#!/usr/bin/env python3
from bottle import route, run
from bs4 import BeautifulSoup
import urllib.request
import re

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
        if len(data_row) == 22:
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


def main():
    get_curr_grid_status()

def run_server():
    run(host='localhost', port=8082)

if __name__ == '__main__':
    main()
