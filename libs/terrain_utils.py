"""
Basic utilities for handling terrain tiles
"""
from pathlib import Path
from typing import List

import numpy as np
import requests
from io import BytesIO
from pydantic import BaseModel,Field

from models.database import DatabaseSession
from models.terrain import TerrainTile

tile_base_path = Path(__file__).parent / ".." / "data"


class TileStatistics(BaseModel):
    """
    Response model for tile statistics, also used as FastAPI response
    """

    pos_x: int = Field(..., description="The X coordinate of the tile's position.")
    pos_y: int = Field(..., description="The Y coordinate of the tile's position.")
    width: int = Field(..., description="The width of the tile.")
    height: int = Field(..., description="The height of the tile.")
    average: float = Field(..., description="The average value of the tile data.")
    max_per_row: List[float] = Field(..., description="Maximum values per row in the tile data.")
    min_per_col: List[float] = Field(..., description="Minimum values per column in the tile data.")


def tile_statistics(tile_id: int) -> TileStatistics:
    """
    Calculates basic statistics on TerrainTile
    """
    with DatabaseSession() as session:
        tile = session.query(TerrainTile).get(tile_id)
        if tile.is_remote:
            response = requests.get(tile.path)
            response.raise_for_status()
            data = np.load(BytesIO(response.content))
        else:
            data = np.load(tile_base_path / tile.path)

    shape = np.shape(data)
    return TileStatistics(
        pos_x=tile.pos_x,
        pos_y=tile.pos_y,
        width=shape[0],
        height=shape[1],
        average=np.average(data),
        max_per_row=data.max(axis=1).tolist(),
        min_per_col=data.min(axis=0).tolist(),
    )
