from sqlalchemy import Boolean, Column, ForeignKey, String, Integer, Float
from sqlalchemy.orm import relationship

from .database import Base


class Proxy(Base):
    __tablename__ = 'proxies'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    proxy_id = Column(Integer)
    url = Column(String)
    taken = Column(Boolean, default=False)
    city_id = Column(ForeignKey('cities.id'))
    city = relationship('City', back_populates='proxy')


class Config(Base):
    __tablename__ = 'configs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    api_key = Column(String)
    url = Column(String)
    interval = Column(String)
    delay = Column(Integer, default=0)
    threads = Column(Integer, default=2)


class City(Base):
    __tablename__ = 'cities'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    short_name = Column(String)
    city_value = Column(Float, default=0)
    startField = Column(Integer, default=0)
    currentField = Column(Integer, default=0)
    taken = Column(Boolean, default=False)
    counter = Column(Integer, default=0)
    proxy = relationship('Proxy', back_populates='city')


class Clicks(Base):
    __tablename__ = 'clicks'

    id = Column(Integer, autoincrement=True, primary_key=True)
    city_id = Column(ForeignKey("cities.id"))
    interval = Column(String)
    click_value = Column(Float)
    city = relationship("City",)


class Interval(Base):
    __tablename__ = 'intervals'

    id = Column(Integer, autoincrement=True, primary_key=True)
    time = Column(String)
    target = Column(Integer)
