from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .sql_app import crud, models, schemas
from .sql_app.database import SessionLocal, engine

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


@app.post('/proxies/', response_model=schemas.Proxy)
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


@app.put('/proxies/{proxy_id}', response_model=schemas.Proxy)
def update_proxy(proxy_id: int, proxy: schemas.ProxyCreate, db: Session = Depends(get_db)):
    return crud.update_proxy(db=db, proxy=proxy, id=proxy_id)


@app.post('/config', response_model=schemas.ConfigClick)
def create_config(config: schemas.ConfigClickCreate, db: Session = Depends(get_db)):
    return crud.create_config(db=db, config=config)


@app.put('/config/{config_id}', response_model=schemas.ConfigClick)
def update_config(config_id: int, config: schemas.ConfigClickUpdate, db: Session = Depends(get_db)):
    return crud.update_config(db=db, config=config, config_id=config_id)


@app.get('/configs', response_model=list[schemas.ConfigClick])
def get_configs(db: Session = Depends(get_db)):
    return crud.get_configs(db=db)


@app.get('/config')
def get_config(db: Session = Depends(get_db)):
    return crud.get_config(db=db, config_id=1)


@app.get('/const')
def get_const():
    return crud.get_const()


@app.post('/const/{id}')
def update_const(id: str):
    return crud.update_const(id=id)


@app.post('/click/{proxy_id}')
def click(proxy_id: int, db: Session = Depends(get_db)):
    return crud.click(db=db, proxy_id=proxy_id)


@app.get('/tets')
def test():
    return crud.test()


@app.put('/browser_api/{proxy_id}')
def update_browser(proxy_id: int, browser_api: schemas.BrowserApi, db: Session = Depends(get_db)):
    return crud.update_browser_config(db=db, proxy_id=proxy_id, browser_api=browser_api)
