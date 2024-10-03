from pydantic import BaseModel


class CityBase(BaseModel):
    name: str
    short_name: str


class CityCreate(CityBase):
    pass

class CityUpdate(CityBase):
    city_value: float

class City(CityBase):
    id: int
    startField: int
    currentField: int
    city_value: float
    taken: bool
    counter: int

    class Config:
        from_attributes = True


class ResetCity(BaseModel):
    interval: str

class ProxyBase(BaseModel):
    url: str
    name: str
    city_id: int


class ProxyCreate(ProxyBase):
    pass


class ProxyUpdate(ProxyBase):
    proxy_id: int


class Proxy(ProxyBase):
    id: int
    taken: bool
    proxy_id: int
    city: City

    class Config:
        from_attributes = True


class BrowserApi(BaseModel):
    browser_api: str


class ConfigClickBase(BaseModel):
    api_key: str
    url: str
    delay: int
    interval: str


class ConfigClickCreate(ConfigClickBase):
    pass


class ConfigClickUpdate(ConfigClickBase):
    delay: int
    interval: str
    threads: int


class ConfigClick(ConfigClickBase):
    id: int
    threads: int

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
