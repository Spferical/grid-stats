import os
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

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
    user_id = Column(Integer, ForeignKey('user.id'))


def main():
    engine = create_engine('sqlite:///stats.db')
    Base.metadata.create_all(engine)


if __name__ == '__main__':
    main()
