import os
import logging

from sqlalchemy import Column
from sqlalchemy import Boolean
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy import Float
from sqlalchemy import and_
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import backref
from sqlalchemy.orm import aliased
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm.exc import NoResultFound

from salty_stats.rating_system import rank_match


Base = declarative_base()


log = logging.getLogger(__name__)


def create_session_class():
    db_filename = os.path.join(os.path.dirname(__file__), 'salty.db')
    engine = create_engine('sqlite:///{}'.format(db_filename))
    session_factory = sessionmaker(bind=engine)
    return scoped_session(session_factory)


class Character(Base):
    __tablename__ = 'character'

    character_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    rating = Column(Float, nullable=False)

    matches = association_proxy('match_players', 'match')

    def __init__(self, name):
        self.name = name

    @classmethod
    def get_or_create(cls, session, name):
        try:
            found = session.query(cls).filter_by(name=name).one()
        except NoResultFound:
            log.debug('Character.get_or_create("{}") = Not Found'.format(name))
            pass
        else:
            log.debug('Character.get_or_create("{}") = Found'.format(name))
            return found

        created = cls(name=name)
        session.add(created)

        return created

    def lost_to(self, session):
        my_matches = aliased(MatchPlayer)
        opponent_matches = aliased(MatchPlayer)
        opponent = aliased(Character)

        query = session.query(opponent).select_from(Character)
        query = query.join(my_matches, Character.character_id == my_matches.character_id)
        query = query.join(opponent_matches, and_(my_matches.match_id == opponent_matches.match_id, opponent_matches.character_id != Character.character_id))
        query = query.join(opponent, opponent_matches.character_id == opponent.character_id)
        query = query.filter(Character.character_id == self.character_id)
        query = query.filter(my_matches.won == False)
        query = query.distinct()

        return query.all()

    def has_beaten(self, session):
        my_matches = aliased(MatchPlayer)
        opponent_matches = aliased(MatchPlayer)
        opponent = aliased(Character)

        query = session.query(opponent).select_from(Character)
        query = query.join(my_matches, Character.character_id == my_matches.character_id)
        query = query.join(opponent_matches, and_(my_matches.match_id == opponent_matches.match_id, opponent_matches.character_id != Character.character_id))
        query = query.join(opponent, opponent_matches.character_id == opponent.character_id)
        query = query.filter(Character.character_id == self.character_id)
        query = query.filter(my_matches.won == True)
        query = query.distinct()

        return query.all()

    @property
    def wins_list(self):
        return [x for x in self.match_players if x.won]

    @property
    def win_count(self):
        return len(self.wins_list)

    @property
    def losses_list(self):
        return [x for x in self.match_players if not x.won]

    @property
    def loss_count(self):
        return len(self.losses_list)

    @property
    def undefeated(self):
        return self.loss_count == 0

    @property
    def total_matches(self):
        return len(self.matches)

    @property
    def win_loss_ratio(self):
        win_count = self.win_count
        loss_count = self.loss_count

        if loss_count == 0:
            return 'undefeated'

        return float(win_count) / float(loss_count)


class MatchPlayer(Base):
    __tablename__ = 'match_player'
    match_player_id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey('match.match_id'), nullable=False)
    character_id = Column(Integer, ForeignKey('character.character_id'), nullable=False)
    bettors = Column(Integer, nullable=False)
    won = Column(Boolean, nullable=False)

    character = relationship(Character, backref=backref('match_players'))
    match = relationship('Match', backref=backref('characters'))

    def __init__(self, match=None, character=None, bettors=0, won=False):
        self.match = match
        self.character = character
        self.bettors = bettors
        self.won = won


class Match(Base):
    __tablename__ = 'match'

    match_id = Column(Integer, primary_key=True)
    winner_id = Column(Integer, ForeignKey('character.character_id'), nullable=False)
    duration = Column(Integer, nullable=False)
    bettors = Column(Integer, nullable=False)

    winner = relationship('Character', backref=backref('wins', order_by=match_id.desc()))

    @classmethod
    def get_or_create(cls, session, match_details):
        try:
            found = session.query(cls).filter_by(match_id=match_details['matchid']).one()
        except NoResultFound:
            log.debug('Match.get_or_create("{}") = Not Found'.format(match_details['matchid']))
            pass
        else:
            log.debug('Match.get_or_create("{}") = Found'.format(match_details['matchid']))
            return (found, False)

        match = Match()
        match.match_id = match_details['matchid']
        match.bettors = match_details['bettors']
        match.duration = match_details['duration']

        match.winner = Character.get_or_create(session, match_details['winner'])
        player1 = MatchPlayer(
            match,
            Character.get_or_create(session, match_details['player1']),
            match_details['player1_bets'],
            match_details['player1'] == match_details['winner'],
        )

        player2 = MatchPlayer(
            match,
            Character.get_or_create(session, match_details['player2']),
            match_details['player2_bets'],
            match_details['player2'] == match_details['winner'],
        )

        loser = player1.character if match_details['winner'] == match_details['player1'] else player2.character

        rank_match(match.winner, loser)

        session.add(player1)
        session.add(player2)
        session.add(match)

        return (match, True)
