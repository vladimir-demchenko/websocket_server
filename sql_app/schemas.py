from pydantic import BaseModel


class ProxyBase(BaseModel):
    proxy_id: str
    url: str
    change_ip: str


class ProxyCreate(ProxyBase):
    pass


class Proxy(ProxyBase):
    id: int
    when_change: float
    taken: bool
    browser_api: str
    city_id: str
    targetClicks: int
    clicks: int

    class Config:
        from_attributes = True


class BrowserApi(BaseModel):
    browser_api: str


class ConfigClickBase(BaseModel):
    api_key: str
    url: str


class ConfigClickCreate(ConfigClickBase):
    pass


class ConfigClickUpdate(ConfigClickBase):
    pause: bool
    interval: str


class ConfigClick(ConfigClickBase):
    id: int
    pause: bool
    interval: str

    class Config:
        from_attributes = True


class CityBase(BaseModel):
    id: str
    name: str


class CityCreate(CityBase):
    pass


class City(CityBase):
    startField: int
    currentField: int
    taken: bool
    counter: int

    class Config:
        from_attributes = True


class ClicksBase(BaseModel):
    interval: str
    city_id: str
    click_value: float


class ClicksCreate(ClicksBase):
    pass


class Clicks(ClicksBase):
    id: int
    city: City

    class Config:
        from_attributes = True


class IntervalBase(BaseModel):
    time: str
    target: int


class IntervalCreate(IntervalBase):
    pass


class Interval(IntervalBase):
    id: int
    isIncrease: bool
    weekDayStart: int
    weekDatEnd: int
    increaseClick: int

    class Config:
        from_attributes = True
