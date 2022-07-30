import logging
from time import sleep
import utils

from datetime import datetime
from os import getenv
from uuid import uuid4
from typing import List, Union
from fastapi import APIRouter, Request, Response, status
from fastapi_microsoft_identity import initialize, requires_auth, get_token_claims
#from models import Secret

from pydantic import BaseModel
from database import DatabaseConnection

class SecretIn(BaseModel): # here because it can't be a module...
    text: str
    receiver_id: str
    receiver_name: str

class SecretOut(BaseModel): # here because it can't be a module...
    id: str
    text: str
    receiver_id: str
    receiver_name: str
    sender_id: str
    sender_name: str
    sent_at : str
    read_at: Union[str, None] = None

# Script com rotas relativas ao gerenciamento de segredos
router = APIRouter(prefix="/secrets")
initialize(tenant_id_=getenv("TENANT_ID"), client_id_=getenv("CLIENT_ID"))
db = DatabaseConnection()

@router.post("/send", description="Envia um segredo a um usuário determinado pelo ID")
async def post_secret_send(request: Request, secret: SecretIn, status_code=status.HTTP_204_NO_CONTENT):

    code = utils.check_expected_scope(request)

    if (code != 200):
        logging.info("Not authorized user tried to access his secrets list.")
        return Response(status_code=code)

    user_claims = get_token_claims(request)
    logging.info("User " + user_claims["name"] + " (oid: " + user_claims["oid"] + ") sent a secret to another user.")

    secret_dict = {
        "id": str(uuid4()),
        "text": secret.text,
        "receiver_id": secret.receiver_id,
        "receiver_name": secret.receiver_name,
        "sender_id": "{0}.{1}".format(user_claims["oid"], user_claims["tid"]),
        "sender_name": user_claims["name"],
        "sent_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "read_at": None
    }
    db.create_item("Secrets", secret_dict)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get("/list", description="Lista todos os segredos para o usuário autenticado", response_model=List[SecretOut])
@requires_auth
async def get_secret_list(request: Request, response_model=List[SecretOut], status_code=status.HTTP_200_OK):

    code = utils.check_expected_scope(request)

    if (code != 200):
        logging.info("Not authorized user tried to access his secrets list.")
        return Response(status_code=code)

    user_claims = get_token_claims(request)
    logging.info("User " + user_claims["name"] + " (oid: " + user_claims["oid"] + ") listed all his secrets.")

    secrets = db.query("Secrets", 
        'SELECT * FROM Secrets as s WHERE s.receiver_id = @uid AND IS_NULL(s.read_at)',
        [
            {
                "name": '@uid',
                "value": "{0}.{1}".format(user_claims["oid"], user_claims["tid"])
            }
        ]
    )
    return list(secrets)

"""
TODO: Implements individual secret reading

@router.get("/{sid}/read", description="Lê um segredo com base no ID informado, excluindo-o em seguida da base de dados", response_model=SecretOut)
@requires_auth
async def get_secret_read(request: Request, sid: int, response_model=SecretOut, status_code=status.HTTP_204_NO_CONTENT):
    
    code = utils.check_expected_scope(request)

    if (code != 200):
        logging.info("Not authorized user tried to access his secrets with ID=" + str(sid) + ".")
        return Response(status_code=code)

    user_claims = get_token_claims(request)
    logging.info("User " + user_claims["name"] + " (oid: " + user_claims["oid"] + ", from: " + user_claims["ipaddr"] + ") requested reading secret " + str(sid) + ".")

    secrets = db.query("Secrets", 
        'UPDATE Secrets as s SET s.read_at=@now WHERE s.receiver_id = @uid and s.read_at = @none',
        [
            {
                "name": '@now',
                "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                "name": '@uid',
                "value": "{0}.{1}".format(user_claims["oid"], user_claims["tid"])
            },
            {
                "name": '@none',
                "value": None
            }
        ]
    )
    return secrets[sid]
"""

@router.get("/read", description="Atualiza todos os segredos como lidos na base de dados")
@requires_auth
async def set_all_secret_read(request: Request, status_code=status.HTTP_204_NO_CONTENT):
    
    code = utils.check_expected_scope(request)

    if (code != 200):
        logging.info("Not authorized user tried to access all his secrets.")
        return Response(status_code=code)

    user_claims = get_token_claims(request)
    logging.info("User " + user_claims["name"] + " (oid: " + user_claims["oid"] + ", from: " + user_claims["ipaddr"] + ") requested reading all his secret.")

    """
    Cosmos don't support multiple update and mass delete...

    secrets = db.query("Secrets", 
        'UPDATE Secrets s SET s.read_at = @now WHERE s.receiver_id = @uid and IS_NULL(s.read_at)',
        [
            {
                "name": '@now',
                "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                "name": '@uid',
                "value": "{0}.{1}".format(user_claims["oid"], user_claims["tid"])
            }
        ]
    )

    ... below one shitty workaround for that platform limitation.
    """

    secrets = list(db.query("Secrets", 
        'SELECT * FROM Secrets as s WHERE s.receiver_id = @uid AND IS_NULL(s.read_at)',
        [
            {
                "name": '@uid',
                "value": "{0}.{1}".format(user_claims["oid"], user_claims["tid"])
            }
        ]
    ))
    
    if (len(secrets)):
        for secret in secrets:
            secret['read_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            db.replace_item("Secrets", secret)
            # ... it's because I made a system that runs in Brazil South and a database that runs US East... (facepalm)
            sleep(.5)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
