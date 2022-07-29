import logging
import json
import utils

from os import getenv
from typing import List, Union
from fastapi import APIRouter, Request, Response, status
from fastapi_microsoft_identity import AuthError, initialize, validate_scope, requires_auth, get_token_claims

from pydantic import BaseModel

class UserIn(BaseModel): # user used to registrate
    reference_id: str       # microsoft id
    name: str     # user name
    username: str # organization email a microsoft

class UserOut(BaseModel): # user list returned from server
    id: Union[str, None] = None
    name: str 
    username: str 
    reference_id: str
    registered_at: str

users = [
    { 
        "id": "abc2331a",
        "name": "Usuário Exemplo 1",
        "username": "user.example1@server.net",
        "registered_at": "2022-07-28 04:38:39"
    },
    { 
        "id": "abto2xca",
        "name": "Usuário Exemplo 2",
        "username": "user.example2@server.net",
        "registered_at": "2022-07-28 07:54:53"
    },
    { 
        "id": "abci1213",
        "name": "Usuário Exemplo 3",
        "username": "user.example3@server.net",
        "registered_at": "2022-07-28 08:42:19"
    },
    { 
        "id": "o23ofjfs",
        "name": "Usuário Exemplo 5",
        "username": "user.example5@server.net",
        "registered_at": "2022-07-28 12:25:29"
    }
]

# Script com rotas relativas ao gerenciamento de segredos
router = APIRouter(prefix="/users")
initialize(tenant_id_=getenv("TENANT_ID"), client_id_=getenv("CLIENT_ID"))

@router.post("/register", description="Registra um usuário autenticado no sistema")
async def post_secret_send(request: Request, user: UserIn, status_code=[status.HTTP_201_CREATED, status.HTTP_200_OK]):

    code = utils.check_expected_scope(request)

    if (code != 200):
        logging.info("Not authorized user to register yourself on this server.")
        return Response(status_code=code)

    user_claims = get_token_claims(request)
    
    registered_user = {
        "reference_id": user.reference_id,
        "name": user.name,
        "username": user.username
    }

    # If new user is being registered
    if (" * USUÁRIO NÃO EXISTE NA BASE DE DADOS * "):
        logging.info("User " + user_claims["name"] + " (oid: " + user_claims["oid"] + ") was registered in this server.")
        return Response(json.dumps(registered_user), status_code=status.HTTP_201_CREATED)
    
    # If user was registered before
    logging.info("User " + user_claims["name"] + " (oid: " + user_claims["oid"] + ") already registered in this server.")
    return Response(json.dumps(registered_user), status_code=status.HTTP_200_OK)


@router.get("/all", description="Lista todos os usuários registrados", response_model=List[UserOut])
@requires_auth
async def get_secret_list(request: Request, response_model=List[UserOut], status_code=status.HTTP_200_OK):

    code = utils.check_expected_scope(request)

    if (code != 200):
        logging.info("Not authorized user tried to access users list.")
        return Response(status_code=code)

    user_claims = get_token_claims(request)
    logging.info("User " + user_claims["name"] + " (oid: " + user_claims["oid"] + ") listed all registered users.")
    return users