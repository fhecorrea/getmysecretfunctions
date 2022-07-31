import logging

import azure.functions as func
from fastapi import FastAPI #, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from routers import secrets, users
from os import getenv
#from models import ConnectionManager

app = FastAPI(title="Get my secret API", debug=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(secrets.router)
app.include_router(users.router)

def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    logging.info('Main HTTP trigger function processed a request.')
    return func.AsgiMiddleware(app).handle(req)
