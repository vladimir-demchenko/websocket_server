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
