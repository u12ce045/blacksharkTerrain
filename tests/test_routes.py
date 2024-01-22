"""Copyright (C) 2015-2020 Blackshark.ai GmbH. All Rights reserved. www.blackshark.ai"""
# pylint: disable = unused-argument
from unittest import TestCase

from fastapi import FastAPI
from fastapi.testclient import TestClient

# Server for end-2-end testing responses with TestClient
from models.database import DatabaseSession
from models.terrain import Terrain, TerrainTile
from routes.terrain import terrain_router

server = FastAPI()
server.include_router(terrain_router(), prefix="/terrain")
client = TestClient(server)


def test_terrain_collection(database: None, check: TestCase) -> None:
    """
    Test whether terrain collection endpoint returns proper list of terrain entries
    """
    with DatabaseSession() as session:
        t1 = Terrain(name="first")
        t2 = Terrain(name="second")
        tt = TerrainTile(path="a/b/c", terrain=t1, pos_x=3, pos_y=4)
        session.add_all([t1, t2, tt])
        session.commit()

        response = client.get("/terrain/")
        assert response.status_code == 200
        check.assertEqual(
            response.json(),
            [{"id": t1.id, "name": t1.name, "tile_count": 1}, {"id": t2.id, "name": t2.name, "tile_count": 0}],
        )
