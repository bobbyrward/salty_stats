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

#Predictions
#TODO: Take into account current win streaks
#TODO: Take current loss streak into account.
#TODO: Have they beaten anyone around that rating before?
#TODO: Try reducing initial rating?


def main():
    logging.basicConfig(level=logging.DEBUG)

    app = Application()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
