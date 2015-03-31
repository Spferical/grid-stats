import os
import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)


class UserLog(Base):
    __tablename__ = 'userlog'
    id = Column(Integer, primary_key=True)
    time = Column(DateTime())
    squares = Column(Integer)
    units = Column(Integer)
    farms = Column(Integer)
    cities = Column(Integer)
    bank = Column(Integer)
    user_id = Column(Integer, ForeignKey('user.id'))


def create_database():
    Base.metadata.create_all(engine)


def add_data(players):
    session = Session()
    for player in players:
        # get the user in database
        query = session.query(User).filter_by(name=player['name'])
        try:
            user = query.one()
        except NoResultFound:
            # user is not in database yet
            # create a new user
            user = User(name=player['name'])
            session.add(user)
            # commit the user to the database, thereby giving him an id
            session.commit()

        # then add the time series data
        user_log = UserLog(
            time=datetime.datetime.now(),
            squares=player['squares'],
            units=player['units'],
            farms=player['farms'],
            cities=player['cities'],
            bank=player['bank'],
            user_id=user.id)
        session.add(user_log)

        # commit and close the session
        session.commit()
        session.close()


# connect to database
engine = create_engine('sqlite:///stats.db')
Session = sessionmaker(bind=engine)
