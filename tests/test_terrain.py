"""
Tests for the list/terrain_utils module
"""
# pylint: disable = unused-argument
from pathlib import Path
from tempfile import NamedTemporaryFile

import numpy as np

from libs.terrain_utils import tile_statistics, tile_base_path
from models.database import DatabaseSession
from models.terrain import Terrain, TerrainTile


def test_tile_statistics_basics(database: None) -> None:
    """
    Test whether basic tile statistics work
    """
    with DatabaseSession() as session, NamedTemporaryFile(dir=tile_base_path) as tt_file:
        t = Terrain(name="first")
        tt = TerrainTile(path=Path(tt_file.name).name, terrain=t, pos_x=3, pos_y=4)
        session.add(t)
        session.add(tt)
        session.commit()
        arr = np.identity(5)
        np.save(tt_file, arr, allow_pickle=False)
        tt_file.seek(0)

        stats = tile_statistics(tt.id)
        assert stats.pos_x == 3
        assert stats.pos_y == 4
        assert stats.width == 5
        assert stats.height == 5
        assert stats.max_per_row == [1] * 5
        assert stats.min_per_col == [0] * 5


def test_tile_statistics_min_max(database: None) -> None:
    """
    Test minimum and maximum values for tile statistic
    """
    with DatabaseSession() as session, NamedTemporaryFile(dir=tile_base_path) as tt_file:
        t = Terrain(name="first")
        tt = TerrainTile(path=Path(tt_file.name).name, terrain=t, pos_x=3, pos_y=4)
        session.add(t)
        session.add(tt)
        session.commit()
        arr = np.ones(shape=(5, 5))
        arr[1, 1] = 4
        arr[3, 3] = -4
        arr[4, 4] = 0
        np.save(tt_file, arr, allow_pickle=False)
        tt_file.seek(0)

        stats = tile_statistics(tt.id)
        assert stats.max_per_row == [1, 4, 1, 1, 1]
        assert stats.min_per_col == [1, 1, 1, -4, 0]
