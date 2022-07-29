"""
    Script criado apenas para fins de teste.
    A ser removido nos deploys mais adiante...
    TODO: Remover isto!
"""
import logging
from os import getenv
from fastapi import APIRouter, Request, Response

router = APIRouter(prefix="/misc")

@router.get("/{example_text}")
async def get_test(req: Request, example_text: str):
    logging.info('Test route in misc endpoint received a request.')
    return { 
        "result": "Tested!",
        "sent_text": example_text,
        "envvar": getenv('OUTRO_VAR') }