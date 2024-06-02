from sqlalchemy import Boolean, Column, ForeignKey, String, Integer

from .database import Base


class Proxy(Base):
    __tablename__ = 'proxies'

    id = Column(Integer, primary_key=True, autoincrement=True)
    proxy_id = Column(String)
    url = Column(String)
    when_change = Column(Integer, default=0)
    change_ip = Column(String)
    taken = Column(Boolean, default=False)


class Config(Base):
    __tablename__ = 'configs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    pause = Column(Boolean, default=True)
    api_key = Column(String)
    url = Column(String)
