from sqlalchemy import Boolean, Column, ForeignKey, String, Integer, Float
from sqlalchemy.orm import relationship

from .database import Base


class Proxy(Base):
    __tablename__ = 'proxies'

    id = Column(Integer, primary_key=True, autoincrement=True)
    proxy_id = Column(String)
    url = Column(String)
    when_change = Column(Float, default=0)
    change_ip = Column(String)
    taken = Column(Boolean, default=False)
    browser_api = Column(String, default='')
    city_id = Column(String, default='')
    targetClicks = Column(Integer, default=0)
    clicks = Column(Integer, default=0)


class Config(Base):
    __tablename__ = 'configs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    pause = Column(Boolean, default=True)
    api_key = Column(String)
    url = Column(String)
    interval = Column(String)


class City(Base):
    __tablename__ = 'cities'

    id = Column(String, primary_key=True)
    name = Column(String)
    startField = Column(Integer, default=0)
    currentField = Column(Integer, default=0)
    taken = Column(Boolean, default=False)
    counter = Column(Integer, default=0)


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
    isIncrease = Column(Boolean, default=False)
    weekDayStart = Column(Integer, default=0)
    weekDatEnd = Column(Integer, default=0)
    increaseClick = Column(Integer, default=0)
