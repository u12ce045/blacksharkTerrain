"""
Database models related to Terrain and its tiles
"""
from __future__ import annotations

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean,JSON
from sqlalchemy.orm import relationship, RelationshipProperty

from .database import Base


class Terrain(Base):
    """
    Parent entity for a set of TerrainTiles, where each tile has the same dimension
    """

    __tablename__ = "terrain"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, default="no name")
    # inverse relationships
    tiles: RelationshipProperty[TerrainTile] = relationship("TerrainTile", back_populates="terrain")


class TerrainTile(Base):
    """
    Terrain tiles are rectangular areas that store the time needed to cross from
    one point to the next in minutes.
    Tiles must not overlap and are positioned into a larger grid by pos_x and pos_y.
    XY origin (0,0) of this larger grid is in upper left corner.
    The tile data itself is stored in a numpy array at the given path and
    contains positive values from 0..100.
    """

    __tablename__ = "terrain_tile"

    id = Column(Integer, primary_key=True)
    path = Column(String, nullable=False)  # relative to data/ directory
    is_remote = Column(Boolean, default=False, nullable=False)  # New field for URL 
    pos_x = Column(Integer, nullable=False)
    pos_y = Column(Integer, nullable=False)
    terrain_id = Column(Integer, ForeignKey("terrain.id"), nullable=False)
    terrain: RelationshipProperty[Terrain] = relationship("Terrain", back_populates="tiles")

class TerrainPyramid(Base):
    __tablename__ = "terrain_pyramid"

    id = Column(Integer, primary_key=True)
    terrain_id = Column(Integer, ForeignKey("terrain.id"), nullable=False)
    zoom_level = Column(Integer, nullable=False)
    metric = Column(String, nullable=False)
    values = Column(JSON, nullable=False)  
    path = Column(String, nullable=False)  # relative to data/ directory
    is_remote = Column(Boolean, default=False, nullable=False)  # New field for URL 
    pos_x = Column(Integer, nullable=False)
    pos_y = Column(Integer, nullable=False)
    terrain: RelationshipProperty[Terrain] = relationship("Terrain", back_populates="tiles")
   

