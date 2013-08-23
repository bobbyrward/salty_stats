import logging
import requests
import time

from PySide import QtGui
from lxml import html

from salty_stats.parsing.parser import load_tourney_stats


REQUEST_WAIT_INTERVAL = 1.5


def load_stats_from_page(parsed_html):
    return load_tourney_stats(parsed_html)


def find_next_page(parsed_html):
    found = parsed_html.xpath('//div[@id="pagination"]/div[@class="right"]/a/@href')

    if len(found):
        print 'next_page =', found[0]
        return ''.join(('http://www.saltybet.com', found[0]))
    else:
        return None


def crawl_stats_page(url):
    session = requests.session()
    session.headers.update({
        'Origin': 'http://www.saltybet.com',
        'Referer': 'http://www.saltybet.com/authenticate?signin=1',
        'User-Agent': 'User-Agent:Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36',
    })

    app = QtGui.QApplication.instance()

    email = str(app.settings.value('salty_email'))
    password = str(app.settings.value('salty_password'))

    response = session.post('http://www.saltybet.com/authenticate?signin=1', data={
        'email': email,
        'pword': password,
        'authenticate': 'signin',
    })
    response.raise_for_status()

    while True:
        response = session.get(url)
        response.raise_for_status()

        parsed_html = html.fromstring(response.content)
        found_existing = load_stats_from_page(parsed_html)

        if found_existing:
            break

        url = find_next_page(parsed_html)

        if url is not None:
            time.sleep(REQUEST_WAIT_INTERVAL)
        else:
            break


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    #logging.basicConfig(level=logging.INFO)

    import sys
    crawl_stats_page(sys.argv[1])
