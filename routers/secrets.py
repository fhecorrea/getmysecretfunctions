import logging
import utils

from os import getenv
from typing import List, Union
from fastapi import APIRouter, Request, Response, status
from fastapi_microsoft_identity import initialize, requires_auth, get_token_claims
#from models import Secret

from pydantic import BaseModel

class SecretIn(BaseModel): # here because it can't be a module...
    text: str

class SecretOut(BaseModel): # here because it can't be a module...
    id: Union[int, None] = None
    text: str
    registered_at: str

secrets = [
    { "id": 2, "text": "Exemplo 1", "registered_at": "2022-07-28 04:38:39"},
    { "id": 4, "text": "Exemplo 2", "registered_at": "2022-07-28 07:54:53"},
    { "id": 8, "text": "Exemplo 3", "registered_at": "2022-07-28 08:42:19"},
    { "id": 9, "text": "Exemplo 5", "registered_at": "2022-07-28 12:25:29"}
]

# Script com rotas relativas ao gerenciamento de segredos
router = APIRouter(prefix="/secrets")
initialize(tenant_id_=getenv("TENANT_ID"), client_id_=getenv("CLIENT_ID"))

@router.post("/send", description="Envia um segredo a um usuário determinado pelo ID")
async def post_secret_send(request: Request, secret: SecretIn, status_code=status.HTTP_204_NO_CONTENT):

    code = utils.check_expected_scope(request)

    if (code != 200):
        logging.info("Not authorized user tried to access his secrets list.")
        return Response(status_code=code)

    user_claims = get_token_claims(request)
    logging.info("User " + user_claims["name"] + " (oid: " + user_claims["oid"] + ") sent a secret to another user.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get("/list", description="Lista todos os segredos para o usuário autenticado", response_model=List[SecretOut])
@requires_auth
async def get_secret_list(request: Request, response_model=List[SecretOut], status_code=status.HTTP_204_NO_CONTENT):

    code = utils.check_expected_scope(request)

    if (code != 200):
        logging.info("Not authorized user tried to access his secrets list.")
        return Response(status_code=code)

    user_claims = get_token_claims(request)
    logging.info("User " + user_claims["name"] + " (oid: " + user_claims["oid"] + ") listed all his secrets.")
    return secrets

@router.get("/{sid}/read", description="Lê um segredo com base no ID informado, excluindo-o em seguida da base de dados", response_model=SecretOut)
@requires_auth
async def get_secret_read(request: Request, sid: int, response_model=SecretOut, status_code=status.HTTP_204_NO_CONTENT):
    
    code = utils.check_expected_scope(request)

    if (code != 200):
        logging.info("Not authorized user tried to access his secrets with ID=" + str(sid) + ".")
        return Response(status_code=code)

    user_claims = get_token_claims(request)
    logging.info("User " + user_claims["name"] + " (oid: " + user_claims["oid"] + ", from: " + user_claims["ipaddr"] + ") requested reading secret " + str(sid) + ".")
    return secrets[sid]

