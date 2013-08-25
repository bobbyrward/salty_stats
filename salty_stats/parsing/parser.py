import logging
import datetime
import re
import urlparse

from salty_stats.db import Match


log = logging.getLogger(__name__)


BET_EXTRACT_RE = re.compile(r' - \$(\d+)\D*')


def parse_tourney_stats(html_tree):
    rows = html_tree.xpath('//table[contains(@class, "leaderboard")]/tbody/tr')

    if len(rows) == 0:
        raise ValueError("Invalid tourney stats file")

    log.debug('Found {} match rows'.format(len(rows)))

    for row in rows:
        cells = row.findall('td')

        match_link = cells[0].find('a')
        players = match_link.findall('span')

        start_time = datetime.datetime.strptime(cells[2].text, '%I:%M%p')
        end_time = datetime.datetime.strptime(cells[3].text, '%I:%M%p')

        # no winner
        if cells[1].find('span') is None:
            yield None
            continue

        try:
            player_1_bets = BET_EXTRACT_RE.match(players[0].tail).group(1)
        except AttributeError:
            player_1_bets = 0

        try:
            player_2_bets = BET_EXTRACT_RE.match(players[1].tail).group(1)
        except AttributeError:
            player_2_bets = 0

        data = {
            'matchid': urlparse.parse_qs(urlparse.urlparse(match_link.get('href')).query)['match_id'][0],
            'player1': players[0].text,
            'player1_bets': player_1_bets,
            'player2': players[1].text,
            'player2_bets': player_2_bets,
            'winner': cells[1].find('span').text,
            'duration': (end_time - start_time).total_seconds(),
            'bettors': cells[4].text,
        }

        yield data


def load_tourney_stats(session, html_tree):
    stats = {
        'matches': 0,
        'characters': 0,
    }

    try:
        for match in parse_tourney_stats(html_tree):
            if match is None:
                continue

            log.debug('Loading {}'.format(match['matchid']))
            db_match, created = Match.get_or_create(session, match)

            if not created:
                break

            stats['matches'] += 1

        session.commit()

    except Exception:
        log.exception('Error loading tourney stats')
        session.rollback()
        raise

    return not created, stats


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    import sys
    from lxml import html

    with open(sys.argv[1]) as fd:
        load_tourney_stats(html.parse(fd))
