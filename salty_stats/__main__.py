import sys
import logging

from salty_stats.app import Application

#Features
#TODO: Add a confidence rating to predictions
#TODO: Add the ability to attach notes to a character
#TODO: Try screen capture to determine characters? Probably not
#TODO: Export stats to sqlite and keep in git
#TODO: Add personal stats tracking of bets

#Improvements/Bugs
#TODO: Make the crawl wizard less horrible
#TODO: Seems like sometimes authentication doesn't work
#TODO: Add crawler check for unauthenticated attempt
#TODO: File menu stays highlighted after crawler wizard opens
#TODO: Fix the tab order
#TODO: Select all text on edit box mouse focus

#TODO: Fix this
# Traceback (most recent call last):
#   File "salty_stats/crawler_dialog.py", line 51, in on_crawl_complete
#     self.parent.next()
# AttributeError: 'builtin_function_or_method' object has no attribute 'next'

#Predictions
#TODO: Take into account current win streaks
#TODO: Take current loss streak into account.
#TODO: Have they beaten anyone around that rating before?
#TODO: Try reducing initial rating?
#TODO: Take undefeated into account


def main():
    logging.basicConfig(level=logging.DEBUG)

    app = Application()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
