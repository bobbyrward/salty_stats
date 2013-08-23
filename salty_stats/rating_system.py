import math


def rank_match(winner, loser):
    rating_diff = winner.rating - loser.rating

    exp = (rating_diff * -1) / 400.0
    odds = 1 / (1 + math.pow(10, exp))

    if winner.rating < 2100:
        k = 32
    elif winner.rating >= 2100 and winner.rating < 2400:
        k = 24
    else:
        k = 16

    new_winner_rating = round(winner.rating + (k * (1 - odds)))
    new_rating_diff = new_winner_rating - winner.rating
    loser.rating = loser.rating - new_rating_diff

    if loser.rating < 1:
        loser.rating = 1

    winner.rating = new_winner_rating

    return new_winner_rating


def build_ratings():
    from salty_stats import db

    session = db.Session()

    for match in session.query(db.Match).all():
        winner = match.winner
        try:
            loser = [x.character for x in match.characters if not x.won][0]
        except IndexError:
            print 'Match {}:'.format(match.match_id), ', '.join('{}={}'.format(x.character.name, x.won) for x in match.characters)
            continue

        rank_match(winner, loser)

    try:
        session.commit()
    except Exception:
        session.rollback()
        raise
