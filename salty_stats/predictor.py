

def predict_winner(session, player1, player2):
    """Very naive and cautious match predictor

    There is currently no attempt to predict upsets.  This should be a goal.

    Additonally things like notes aobut problems w/ small hitboxes would be great.

    Or mexibeams.  Viva los caballeros del zodiaco!
    """

    player1stats = {'beat': player1.has_beaten(session), 'lostto': player1.lost_to(session)}
    player2stats = {'beat': player2.has_beaten(session), 'lostto': player1.lost_to(session)}

    player1_bet_rating = 0
    player2_bet_rating = 0

    messages = {
        'favorp1': [],
        'favorp2': [],
        'warnings': [],
        'similar': [],
    }

    for p1_beat in player1stats['beat']:
        if p1_beat in player2stats['lostto']:
            messages['favorp1'].append('{} beat {} but {} lost to {}'.format(
                player1.name,
                p1_beat.name,
                player2.name,
                p1_beat.name,
            ))
            player1_bet_rating += 1

        if p1_beat in player2stats['beat']:
            messages['similar'].append('{} and {} beat {}'.format(
                player1.name,
                player2.name,
                p1_beat.name,
            ))

    for p1_lost in player1stats['lostto']:
        if p1_lost in player2stats['lostto']:
            messages['similar'].append('{} and {} lost to {}'.format(
                player1.name,
                player2.name,
                p1_lost.name,
            ))

        if p1_lost in player2stats['beat']:
            messages['favorp2'].append('{} beat {} but {} lost to {}'.format(
                player2.name,
                p1_lost.name,
                player1.name,
                p1_lost.name,
            ))
            player2_bet_rating += 1

    p1_wins = player1.win_count()
    p2_wins = player2.win_count()

    p1_ratio = player1.win_loss_ratio()
    p2_ratio = player2.win_loss_ratio()

    if p1_ratio == 'undefeated':
        messages['warnings'].append('{} is undefeated'.format(player1.name))

    if p2_ratio == 'undefeated':
        messages['warnings'].append('{} is undefeated'.format(player2.name))

    if player1.rating < 1450 and player2.rating < 1450:
        messages['warnings'].append('{} and {} are both below 1450 rating'.format(player1.name, player2.name))

    if p1_wins < 5:
        messages['warnings'].append('{} has less than 5 wins'.format(player1.name))

    if p2_wins < 5:
        messages['warnings'].append('{} has less than 5 wins'.format(player2.name))

    if len(player1.matches) > 3 and len(player2.matches) > 3:
        if p1_ratio > (p2_ratio + 0.5):
            messages['favorp1'].append('{} has a higher win/loss ratio than {}'.format(player1.name, player2.name))
            player1_bet_rating += 1
        elif p2_ratio > (p1_ratio + 0.5):
            messages['favorp2'].append('{} has a higher win/loss ratio than {}'.format(player2.name, player1.name))
            player2_bet_rating += 1
        else:
            messages['similar'].append('{} and {} have a similar win/loss ratio'.format(player1.name, player2.name))

    if player1.rating > (player2.rating + 50):
        messages['favorp1'].append('{} has a higher rating than {}'.format(player1.name, player2.name))
        player1_bet_rating += 3
    elif player2.rating > (player1.rating + 50):
        messages['favorp2'].append('{} has a higher rating than {}'.format(player2.name, player1.name))
        player2_bet_rating += 3
    else:
        messages['warnings'].append('{} and {} have a similar rating'.format(player1.name, player2.name))

    return messages, player1_bet_rating, player2_bet_rating
