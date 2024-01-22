"""
Quick and dirty script to set up a new database
"""
from sqlalchemy import create_engine

from models.database import Base, db_connection_str, DatabaseSession
from models.terrain import Terrain, TerrainTile

db_engine = create_engine(db_connection_str)
Base.metadata.create_all(db_engine)

terrain1 = Terrain(name="wonderland")
terrain2 = Terrain(name="dreamscape")
tile1_1 = TerrainTile(path="tile/01_02_03.npy", pos_x=2, pos_y=3, terrain=terrain1)
tile1_2 = TerrainTile(path="tile/01_08_05.npy", pos_x=8, pos_y=5, terrain=terrain1)
tile2_1 = TerrainTile(path="tile/02_17_05.npy", pos_x=17, pos_y=5, terrain=terrain2)

with DatabaseSession() as session:
    session.add_all([terrain1, terrain2, tile1_1, tile1_2, tile2_1])
    session.commit()
