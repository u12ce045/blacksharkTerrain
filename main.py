"""Copyright (C) 2015-2020 Blackshark.ai GmbH. All Rights reserved. www.blackshark.ai"""
import logging
from argparse import ArgumentParser

from fastapi import FastAPI
from uvicorn import run

from routes.terrain import terrain_router

_logger = logging.getLogger("backend")

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--port", type=int, required=False, default=8080)
    parser.add_argument("--host", type=str, required=False, default="127.0.0.1")
    args = parser.parse_args()

    server = FastAPI()
    server.include_router(terrain_router(), prefix="/terrain", tags=["terrain"])

    _logger.info("Server starting up")
    run(server, port=args.port, host=args.host)
