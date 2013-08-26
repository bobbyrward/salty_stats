import sys
import logging

from salty_stats.app import Application

#Features
#TODO: Try screen capture to determine characters? Probably not

#Improvements/Bugs
#TODO: Put screenshot in git

#TODO: Fix this
# Traceback (most recent call last):
#   File "salty_stats/crawler_dialog.py", line 51, in on_crawl_complete
#     self.parent.next()
# AttributeError: 'builtin_function_or_method' object has no attribute 'next'
# Bets just stop working...
# Background requests freeze the app.  GIL not getting released?
# Get the websocket state update notification working

#Predictions
#TODO: Don't show <5 wins warning if they have a lot of losses (how many?)
#TODO: Bad prediction when ratings are similar(~100) and drastically different ratio
#TODO: Determine the characters one losses two and determine if the opponent is similar


def main():
    logging.basicConfig(level=logging.DEBUG)

    app = Application()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
