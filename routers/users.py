import logging
import json

import utils

from datetime import datetime
from os import getenv
from typing import List, Union
from fastapi import APIRouter, Request, Response, status
from fastapi_microsoft_identity import AuthError, initialize, validate_scope, requires_auth, get_token_claims

from pydantic import BaseModel
from database import DatabaseConnection

class UserIn(BaseModel): # user used to registrate
    id: str       # microsoft id
    name: str     # user name
    username: str # organization email a microsoft

class UserOut(BaseModel): # user list returned from server
    id: str
    name: str 
    username: str 
    registered_at: str

# Script com rotas relativas ao gerenciamento de segredos
router = APIRouter(prefix="/users")
db = DatabaseConnection()
initialize(tenant_id_=getenv("TENANT_ID"), client_id_=getenv("CLIENT_ID"))

@router.post("/register", description="Registra um usuário autenticado no sistema")
async def post_register_user(request: Request, user: UserIn, status_code=[status.HTTP_201_CREATED, status.HTTP_200_OK]):

    code = utils.check_expected_scope(request)

    if (code != 200):
        logging.info("Not authorized user to register yourself on this server.")
        return Response(status_code=code)

    user_claims = get_token_claims(request)
    
    registered_user = {
        "id": user.id,
        "name": user.name,
        "username": user.username,
        "registered_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    user = db.get_item_by_id("Users", registered_user['id'])
    #logging.debug("Found user: ", user)
    
    # If new user is being registered
    if (user == None):
        logging.info("User " + user_claims["name"] + " (oid: " + user_claims["oid"] + ") was registered in this server.")
        user = db.create_item("Users", registered_user)
        #logging.debug("Created user: ", user)
        return Response(json.dumps(user), status_code=status.HTTP_201_CREATED)
    
    # If user was registered before
    logging.info("User " + user_claims["name"] + " (oid: " + user_claims["oid"] + ") already registered in this server.")
    return Response(json.dumps(user), status_code=status.HTTP_200_OK)


@router.get("/all", description="Lista todos os usuários registrados", response_model=List[UserOut])
@requires_auth
async def get_list_registered_users(request: Request, response_model=List[UserOut], status_code=status.HTTP_200_OK):

    code = utils.check_expected_scope(request)

    if (code != 200):
        logging.info("Not authorized user tried to access users list.")
        return Response(status_code=code)

    user_claims = get_token_claims(request)
    logging.info("User " + user_claims["name"] + " (oid: " + user_claims["oid"] + ") listed all registered users.")

    users = db.query("Users", 
        'SELECT * FROM Users as u WHERE u.id != @uid',
        [
            {
                "name": '@uid',
                "value": "{0}.{1}".format(user_claims["oid"], user_claims["tid"])
            }
        ]
    )
    return list(users)