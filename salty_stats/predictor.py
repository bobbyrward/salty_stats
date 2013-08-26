

LOWER_LOSS_THRESHOLD_WARNING = 5
LOWER_WIN_THRESHOLD_WARNING = 5
INITIAL_RATING_LEVEL = 1450

RATING_DIFF_TIER_3 = 200
RATING_DIFF_TIER_2 = 100
RATING_DIFF_TIER_1 = 50


class Prediction(object):
    message_dict = {
        'xbeatylost': {
            'template': '{x} beat {z} but {y} lost to {z}',
            'severity': 'minor'
        },
        'xandyundefeated': {
            'template': '{x} and {y} are both undefeated',
            'severity': 'major',
        },
        'xundefeated': {
            'template': '{x} is undefeated',
            'severity': 'major',
        },
        'xltlosses': {
            'template': '{x} has less than 5 losses',
            'severity': 'major',
        },
        'xltwins': {
            'template': '{x} has less than 5 wins',
            'severity': 'major',
        },
        'xandyinitialrating': {
            'template': '{x} and {y} are at or below initial rating',
            'severity': 'major',
        },
        'xltmatches': {
            'template': '{x} has less than or equal to 10 matches total',
            'severity': 'major',
        },
        'xhigherratio': {
            'template': '{x} has a higher win/loss ratio',
            'severity': 'minor',
        },
        'xhigherrating3': {
            'template': '{x} has a much higher rating',
            'severity': 'critical',
        },
        'xhigherrating2': {
            'template': '{x} has a higher rating',
            'severity': 'major',
        },
        'xhigherrating1': {
            'template': '{x} has a slightly higher rating',
            'severity': 'minor',
        },
        'similarrating': {
            'template': 'Both have a similar rating',
            'severity': 'major',
        },
    }

    favor_category_rating = {
        'minor': 1,
        'major': 3,
        'critical': 5,
    }

    def __init__(self, session, player1, player2):
        self.session = session
        self.player1 = player1
        self.player2 = player2
        self.bet = ''
        self.stats = {}
        self.confidence = 0
        self.messages = {
            player1: [],
            player2: [],
            'warnings': [],
            'similar': [],
        }
        self.bet_rating = {
            player1: 0,
            player2: 0,
        }

    def predict(self):
        self.compile_stats()
        self.compare_match_history()
        self.compile_warnings()
        self.compare_players()
        self.make_prediction()

    def make_prediction(self):
        p1 = self.player1
        p2 = self.player2

        if abs(self.bet_rating[p1] - self.bet_rating[p2]) > 1 and self.confidence >= 1:
            if self.bet_rating[p1] > self.bet_rating[p2]:
                self.bet = p1.name
            elif self.bet_rating[p2] > self.bet_rating[p1]:
                self.bet = p2.name
        else:
            self.bet = '???'

    def compare_players(self):
        p1 = self.player1
        p2 = self.player2

        def stat(player, stat_name):
            return self.stats[stat_name][player]

        if not stat(p1, 'undefeated') and not stat(p2, 'undefeated'):
            if stat(p1, 'total_matches') > 3 and stat(p2, 'total_matches') > 3:

                if stat(p1, 'win_ratio') > (stat(p2, 'win_ratio') + 0.5):
                    self.favor_player(p1, 'xhigherratio', x=p1.name)

                elif stat(p2, 'win_ratio') > (stat(p1, 'win_ratio') + 0.5):
                    self.favor_player(p2, 'xhigherratio', x=p2.name)

        if abs(stat(p1, 'rating') - stat(p2, 'rating')) >= RATING_DIFF_TIER_3:
            if stat(p1, 'rating') > stat(p2, 'rating'):
                self.favor_player(p1, 'xhigherrating3', x=p1.name)
            else:
                self.favor_player(p2, 'xhigherrating3', x=p2.name)

        elif abs(stat(p1, 'rating') - stat(p2, 'rating')) > RATING_DIFF_TIER_2:
            if stat(p1, 'rating') > stat(p2, 'rating'):
                self.favor_player(p1, 'xhigherrating2', x=p1.name)
            else:
                self.favor_player(p2, 'xhigherrating2', x=p2.name)

        elif abs(stat(p1, 'rating') - stat(p2, 'rating')) > RATING_DIFF_TIER_1:
            if stat(p1, 'rating') > stat(p2, 'rating'):
                self.favor_player(p1, 'xhigherrating1', x=p1.name)
            else:
                self.favor_player(p2, 'xhigherrating1', x=p2.name)

    def compile_warnings(self):
        p1 = self.player1
        p2 = self.player2

        def stat(player, stat_name):
            return self.stats[stat_name][player]

        #TODO: A lot of the warnings are redundant

        # If either/both players are undefeated add a major warning since this prediction is unstable
        if stat(p1, 'undefeated') and stat(p2, 'undefeated'):
            self.add_warning('xandyundefeated', x=p1.name, y=p2.name)

        elif stat(p1, 'undefeated') and stat(p1, 'win_count') >= LOWER_WIN_THRESHOLD_WARNING:
            self.favor_player(p1, 'xundefeated', x=p1.name)

        elif stat(p2, 'undefeated') and stat(p1, 'win_count') >= LOWER_WIN_THRESHOLD_WARNING:
            self.favor_player(p2, 'xundefeated', x=p2.name)

        # if either player is not undefeated but has less than 5 wins or losses, add a warning
        if not stat(p1, 'undefeated') and stat(p1, 'loss_count') < LOWER_LOSS_THRESHOLD_WARNING:
            if stat(p1, 'win_count') > LOWER_WIN_THRESHOLD_WARNING:
                self.favor_player(p1, 'xltlosses', x=p1.name)
            else:
                self.add_warning('xltlosses', x=p1.name)

        if not stat(p2, 'undefeated') and stat(p2, 'loss_count') < LOWER_LOSS_THRESHOLD_WARNING:
            if stat(p2, 'win_count') > LOWER_WIN_THRESHOLD_WARNING:
                self.favor_player(p2, 'xltlosses', x=p2.name)
            else:
                self.add_warning('xltlosses', x=p2.name)

        if stat(p1, 'total_matches') <= 10:
            self.add_warning('xltmatches', x=p1.name)

        if stat(p2, 'total_matches') <= 10:
            self.add_warning('xltmatches', x=p2.name)

    def compile_stats(self):
        stats = {
            'rating': lambda x: x.rating,
            'win_ratio': lambda x: x.win_loss_ratio,
            'win_count': lambda x: x.win_count,
            'loss_count': lambda x: x.loss_count,
            'total_matches': lambda x: x.total_matches,
            'defeated': lambda x: x.has_beaten(self.session),
            'defeatedby': lambda x: x.lost_to(self.session),
            'undefeated': lambda x: x.undefeated,
        }

        for stat, value_func in stats.items():
            self.stats[stat] = {
                self.player1: value_func(self.player1),
                self.player2: value_func(self.player2),
            }

    def compare_match_history(self):
        p1 = self.player1
        p2 = self.player2

        def stat(player, stat_name):
            return self.stats[stat_name][player]

        for p1_beat in stat(p1, 'defeated'):
            if p1_beat in stat(p2, 'defeatedby'):
                self.favor_player(self.player1, 'xbeatylost', x=p1.name, y=p2.name, z=p1_beat.name)

        for p1_lost in stat(p1, 'defeatedby'):
            if p1_lost in stat(p2, 'defeated'):
                self.favor_player(self.player2, 'xbeatylost', x=p2.name, y=p1.name, z=p1_lost.name)

    def add_warning(self, message, **message_kwargs):
        """Add a warning that the prediction may be unreliable
        """
        self.messages['warnings'].append(self.message_dict[message]['template'].format(**message_kwargs))
        self.confidence -= 1

    def favor_player(self, player, message, **message_kwargs):
        """Add an item favoring one player
        """
        message = self.message_dict[message]
        self.messages[player].append(message['template'].format(**message_kwargs))
        self.bet_rating[player] += self.favor_category_rating[message['severity']]
        self.confidence += 1


def predict_winner(session, player1, player2):
    prediction = Prediction(session, player1, player2)
    prediction.predict()
    return prediction
