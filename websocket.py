from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv, find_dotenv

from .sql_app import crud, models, schemas
from .sql_app.database import SessionLocal, engine

load_dotenv(find_dotenv())

models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@app.get("/")
async def root():
    return {"message": "Hello world"}


@app.post('/proxies/')
def create_proxy(proxy: schemas.ProxyCreate, db: Session = Depends(get_db)):
    return crud.create_proxy(db=db, proxy=proxy)


@app.get('/proxies/', response_model=list[schemas.Proxy])
def get_proxies(db: Session = Depends(get_db)):
    proxies = crud.get_proxies(db=db)
    return proxies


@app.get('/proxies/{proxy_id}', response_model=schemas.Proxy)
def get_proxy(proxy_id: int, db: Session = Depends(get_db)):
    return crud.get_proxy(db=db, proxy_id=proxy_id)


@app.delete('/proxies/{proxy_id}')
def delete_proxy(proxy_id: int, db: Session = Depends(get_db)):
    return crud.delete_proxy(db=db, proxy_id=proxy_id)


@app.patch('/proxies/{proxy_id}', response_model=schemas.Proxy)
def update_proxy(proxy_id: int, proxy: schemas.ProxyUpdate, db: Session = Depends(get_db)):
    return crud.update_proxy(db=db, proxy=proxy, id=proxy_id)


@app.get('/proxies_random/')
def get_random_proxy(db: Session = Depends(get_db)):
    return crud.get_random_proxy(db=db)

@app.patch('/take/{client_id}')
def taken_proxy(client_id: int, db: Session = Depends(get_db)):
    return crud.take_proxy(client_id=client_id, db=db)

@app.patch('/untake/{client_id}')
def untaken_proxy(client_id:int, profile_id: int, browser_proxy_id: int, proxy_id: int, db: Session = Depends(get_db)):
    return crud.untake_proxy(client_id=client_id,profile_id=profile_id, browser_proxy_id=browser_proxy_id, proxy_id=proxy_id, db=db)


@app.post('/config', response_model=schemas.ConfigClick)
def create_config(config: schemas.ConfigClickCreate, db: Session = Depends(get_db)):
    return crud.create_config(db=db, config=config)


@app.put('/config/{config_id}', response_model=schemas.ConfigClick)
def update_config(config_id: int, config: schemas.ConfigClickUpdate, db: Session = Depends(get_db)):
    return crud.update_config(db=db, config=config, config_id=config_id)


@app.get('/configs')
def get_configs(db: Session = Depends(get_db)):
    return crud.get_configs(db=db)


@app.get('/config')
def get_config(db: Session = Depends(get_db)):
    return crud.get_config(db=db, config_id=1)


@app.delete('/config/{config_id}')
def delete_config(config_id: int, db: Session = Depends(get_db)):
    return crud.delete_config(config_id, db)

@app.post('/profile/{proxy_id}')
def click(proxy_id: int):
    return crud.create_profile(proxy_id=proxy_id)


@app.delete('/profile/{profile_id}')
def delete_profile(profile_id: int):
    return crud.delete_profile(profile_id)

@app.get('/cities')
def get_cities(db: Session = Depends(get_db)):
    return crud.get_cities(db=db)


@app.get('/cities/{city_id}')
def get_city(city_id: str, db: Session = Depends(get_db)):
    return crud.get_city(city_id=city_id, db=db)


@app.post('/cities', response_model=schemas.City)
def create_city(city: schemas.CityCreate, db: Session = Depends(get_db)):
    return crud.create_cities(db=db, city=city)

@app.patch('/cities/{city_id}', response_model=schemas.City)
def update_cities(city_id: int, city: schemas.CityUpdate, db: Session = Depends(get_db)):
    return crud.update_cities(city_id, city, db)

@app.delete('/cities/{city_id}')
def delete_city(city_id: int, db: Session = Depends(get_db)):
    return crud.delete_city(city_id, db)

@app.patch('/click/{city_id}')
def click(city_id: int, db: Session = Depends(get_db)):
    return crud.click(city_id, db)

@app.get('/intervals')
def get_interval(db: Session = Depends(get_db)):
    return crud.get_intervals(db)


@app.post('/intervals')
def create_interval(interval: schemas.IntervalCreate, db: Session = Depends(get_db)):
    return crud.create_interval(interval=interval, db=db)

@app.patch('/intervals/{interval_id}')
def update_interval(interval_id: int, interval: schemas.IntervalCreate, db: Session = Depends(get_db)):
    return crud.update_interval(interval_id, interval, db)

@app.post('/reset')
def reset(interval: schemas.ResetCity, db: Session = Depends(get_db)):
    return crud.reset_cities(interval, db)

@app.post('/reset_proxies')
def reset_proxies(db: Session = Depends(get_db)):
    return crud.reset_proxies(db)

@app.get('/test')
def test(db: Session =Depends(get_db)):
    return crud.test(db)

@app.get('/clients')
def get_clients(db: Session = Depends(get_db)):
    return crud.get_clients(db)

@app.get('/clients/{client_id}')
def get_client(client_id: int, db: Session = Depends(get_db)):
    return crud.get_client(client_id, db)

@app.delete('/clients/{client_id}')
def delete_client(client_id: int, db: Session = Depends(get_db)):
    return crud.delete_client(client_id, db)

@app.post('/clients')
def create_clients(client: schemas.ClientCreate, db: Session = Depends(get_db)):
    return crud.create_client(client=client, db=db)

@app.patch('/clients/{client_id}')
def update_clients(client_id: int, client: schemas.ClientUpdate, db: Session = Depends(get_db)):
    return crud.update_client(client_id, client, db)

@app.post('/schedule')
def schedule(now: schemas.ScheduleCheck, db: Session = Depends(get_db)):
    return crud.schedule_reset(now, db)