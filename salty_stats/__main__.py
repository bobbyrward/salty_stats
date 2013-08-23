import sys
import logging

from salty_stats.app import Application


#TODO: Add dialog to crawl stats url


def main():
    logging.basicConfig(level=logging.DEBUG)

    app = Application()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
