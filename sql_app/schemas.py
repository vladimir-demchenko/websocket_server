from pydantic import BaseModel


class ProxyBase(BaseModel):
    proxy_id: str
    url: str
    change_ip: str


class ProxyCreate(ProxyBase):
    pass


class Proxy(ProxyBase):
    id: int
    when_change: int
    taken: bool
    browser_api: str
    city_id: str

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


class ConfigClick(ConfigClickBase):
    id: int
    pause: bool

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
