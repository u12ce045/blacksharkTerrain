"""
Routes and data objects for querying/updating terrain information
"""
import logging
from typing import List

from fastapi import APIRouter,HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session
from tenacity import retry, stop_after_attempt, wait_fixed
from pydantic import BaseModel

from libs.terrain_utils import tile_statistics, TileStatistics
from models.database import DatabaseSession
from models.terrain import Terrain, TerrainTile,TerrainPyramid
from sqlalchemy.orm import joinedload

_logger = logging.getLogger(__name__)


class TerrainItem(BaseModel):
    """
    Response model for Terrain
    Contains some additional values that are calculated on the fly
    """

    id: int
    name: str
    tile_count: int = 0

def calculate_pyramid(terrain_id: int, metric: str) -> None:
    with Session() as session:
        # Retrieve all TerrainTiles for the given Terrain.
        tiles = session.query(TerrainTile).filter_by(terrain_id=terrain_id).all()
        
        # Assuming each tile has a uniform size and they form a rectangular grid.
        # Determine the size of the grid.
        max_x = max(tile.pos_x for tile in tiles)
        max_y = max(tile.pos_y for tile in tiles)
        grid = np.zeros((max_y + 1, max_x + 1))

        # Populate the grid with initial values from tiles.
        for tile in tiles:
            # Assuming each tile has an attribute 'value' or similar.
            grid[tile.pos_y][tile.pos_x] = tile.value

        # Apply the zooming logic.
        def zoom(grid, metric):
            # Implement the zooming logic based on the metric.
            # This is an example for the 'maximum' metric.
            new_size_y, new_size_x = (grid.shape[0] // 2, grid.shape[1] // 2)
            zoomed_grid = np.zeros((new_size_y, new_size_x))
            for i in range(new_size_y):
                for j in range(new_size_x):
                    zoomed_grid[i][j] = np.max(grid[i*2:(i+1)*2, j*2:(j+1)*2])
            return zoomed_grid

        zoom_level = 0
        while grid.size > 1:
            # Store the current level grid in the database.
            session.add(TerrainPyramid(
                terrain_id=terrain_id,
                zoom_level=zoom_level,
                metric=metric,
                values=grid.tolist()  # Convert numpy array to list for storage
            ))
            session.commit()

            # Zoom the grid for the next level.
            grid = zoom(grid, metric)
            zoom_level += 1

        # Store the final single-element grid.
        session.add(TerrainPyramid(
            terrain_id=terrain_id,
            zoom_level=zoom_level,
            metric=metric,
            values=grid.tolist()
        ))
        session.commit()



def terrain_router() -> APIRouter:
    router = APIRouter()

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def _get_terrains(session):
        return session.query(Terrain).options(joinedload(Terrain.tiles)).all()

    @router.get("/", response_model=List[TerrainItem])
    async def _route_terrain_collection() -> List[TerrainItem]:
        try:
            with DatabaseSession() as session:
                terrains = _get_terrains(session)
                result = []
                for terrain in terrains:
                    tile_count = session.query(TerrainTile).filter_by(terrain=terrain).count()
                    result.append(TerrainItem(id=terrain.id, name=terrain.name, tile_count=tile_count))
                return result
        except OperationalError as e:
            _logger.error(f"Database error: {e}")
            raise HTTPException(status_code=503, detail="Service temporarily unavailable")
        except Exception as e:
            _logger.error(f"Unexpected error: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
    
    @router.get("/tile/{tile_id}/stats")
    def _route_pass(tile_id: int) -> TileStatistics:
        #return tile_statistics(tile_id)
        data = tile_statistics(tile_id)
        formatted_data = {
        "Tile Information": 
        {
            "Position": {"X": data.pos_x, "Y": data.pos_y},
            "Dimensions": {"Width": data.width, "Height": data.height}},
            "Statistics": {
                "Average Value": round(data.average, 2),
                "Max Values per Row": data.max_per_row,
                "Min Values per Column": data.min_per_col}}

        return JSONResponse(content=jsonable_encoder(formatted_data))
    
    @app.get("/terrain/{terrain_id}/pyramid/{zoom_level}")
    async def get_terrain_pyramid(terrain_id: int, zoom_level: int, metric: str = "maximum"):
        # Check if the pyramid for this terrain, zoom level, and metric exists
        pyramid = session.query(TerrainPyramid).filter_by(
            terrain_id=terrain_id,
            zoom_level=zoom_level,
            metric=metric
            ).first()

        if not pyramid:
            # Calculate and store the pyramid
            calculate_pyramid(terrain_id, metric)
            # Query again for the newly stored pyramid
            pyramid = session.query(TerrainPyramid).filter_by(
                terrain_id=terrain_id,
                zoom_level=zoom_level,
                metric=metric
                ).first()

        return pyramid.values

    return router
