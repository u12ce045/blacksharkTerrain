Python Developer: Test Assignment
=================================

The test assignment is a small REST-API server. It is using FastAPI, SQLAlchemy,
and an SQLite database. When implementing the following tasks, imagine that this
is actually a large project, running on a huge PostgreSQL database, using cloud
blob storage, and replicated to 100s of container instances in a Kubernetes cluster.


## Project structure

A quick overview of the project structure:

* `data/`: contains the main database and some blobs inside `data/tile/`
* `libs/`: contains some business logic and utility functions
* `models/`: the database models: _Terrain_ and _TerrainTile_
* `routes/`: the REST routes for our FastAPI server
* `scripts/`: setup scripts, in case you need to recreate the main database and the blobs in `data/tile`
* `tests/`: unit tests for routes and business logic
* `main.py`: for running the server

In order to run the project, just run `python main.py`.
This will start a server at port 8080.
You can access an automatically generated documentation of the REST API at http://localhost:8080/docs.

The main database contains two _Terrain_ entries and three _TerrainTile_ entries.

We have used poetry (https://python-poetry.org/) in order to manage our dependencies.
You can find the dependencies inside `pyproject.toml`, if you'd like to use a
package manager other than poetry.

Please note: we have only verified that this code works on Linux machines. We will do
verification of your solution on Linux machines as well.


## Assignment

Please develop your application, like you would do when working inside a team: use git,
do proper commits, branches, merge your branches etc. Your submission will be judged not
only on the functions themselves, but also on other criteria, like e.g. communication,
documentation, commits, code quality, structure, robustness, fault tolerance etc. As you
will discover, the focus of this assignment is not on computer science knowledge, but on
clean code and principles of clean architecture. Keep that in mind, as you move forward.

So please make sure that you are writing code with production grade quality and
show us your best side :o)

If you need to make assumptions, because the task description is not clear enough,
make sure you document your assumptions somewhere. If you need to install additional
Python packages, then please either use poetry or add them manually to `pyproject.toml`. 

### Deliveries

Please merge everything back to master, as we will look at your result in the master branch.

Then, create a ZIP or tarball of the entire project directory (including `.git` and other
dot files), but please exclude the virtual environment itself and any cache directories
(e.g. `__pycache__`) or IDE configuration files.

### Available time

Please send us your solution to the assignment within 48 hours.


## Tasks

### Task 1: Speed up /terrain endpoint

We got reports from our customers that the `/terrain` endpoint is unbearably slow
in larger installations. Also, our colleague looking after the database told us
that the endpoint is a terrible performance hog.
Please improve the speed of the endpoint.


### Task 2: Stability of /terrain endpoint

Every once in a while we are seeing errors from the `/terrain` endpoint in our logs.
We are sure that the logic of the function is correct. Most of the time errors occur
when there is a high request volume for that endpoint, so we assume that either there
are intermittent network outages in our cloud or sometimes we are running out of
available database connections. Please make the endpoint more robust to such failures.
In addition, it would be nice, if the endpoint would return proper HTTP status codes,
if - for whatever reason - it is unable to service a request.


### Task 3: Fix /terrain/tile/{id}/stats endpoint

Our quality assurance team has raised an issue that our stats endpoint is not up to our
usual quality standards. Please fix the error.


### Task 4: Code smells

Our system architect has raised concerns about the `tile_statistics()` function.
Looking at the unit tests, it is clear that the function is mixing different concerns.
Maybe you can refactor a bit, in order to improve the function and its unit tests.


### Task 5: Extend to URL based access

Right now, access to terrain tile blobs is done through the local filesystem.
We got a new requirement that we should be able to handle foreign tiles which are
referenced by a URL. Please implement this functionality by allowing URLs in the
_TerrainTile_ object in addition to file paths. How you adapt the data model is up
to you. Make the necessary changes across the codebase where needed.


### Task 6: Terrain pyramid

For caching and performance purposes, we need to store a terrain pyramid for each Terrain.
Basically, it is zooming out of the terrain using a defined metric. For example, if the
metric is *maximum()*, given the terrain below, the pyramid would be constructed as follows:

Original terrain:

|  . |  . |  . |  . |  . |  . |  . |
|----|----|----|----|----|----|----|
|  1 | 41 | 37 | 12 |  0 | 66 | 36 |
|  3 | 62 | 23 |  7 |  2 | 31 | 21 |
| 87 | 12 | 34 | 32 | 34 |  7 | 12 |
|  5 |  3 | 13 | 74 | 53 | 15 |  1 |
| 15 |  0 | 17 | 41 | 59 | 21 |  0 |

Zoom out one level:

|  . |  . |  . |  . |
|----|----|----|----|
| 62 | 37 | 66 | 36 |
| 87 | 74 | 53 | 12 |
| 15 | 41 | 59 |  0 |

Zoom out two levels:

|  . |  . |
|----|----|
| 87 | 66 |
| 41 | 59 |

Zoom out three levels:

|  . |
|----|
| 87 |

The requirement is to construct the terrain pyramid until it culminates in a single element.
In the example above this took 3 zoom steps, but might it take a different number of steps
depending on the terrain size. Currently, the only requirement is for the *maximum* metric,
but we foresee future requirements, where this metric is some defined function that might
do all sorts of calculations as part of the zoom step.

Please note that we are talking about *terrains* not single terrain tiles. Given that the
TerrainTiles have X and Y coordinates, it is possible to build the pyramid not for single tiles,
but for all tiles within a Terrain. Imagine the tiles being placed in a grid at their
specified X/Y position and do the zooming for this grid.

Define your own storage layout for the pyramid and adapt the data model if necessary.

Add an endpoint for querying different zoom levels; the endpoint should do the pyramid
calculation on the fly, if there is no cached version, and then store the calculated version.
Subsequent requests should then directly return the cached version.

---

Not difficult enough? And still have time?

Consider this bonus task: do zooming of a terrain *without* loading all related TerrainTiles
at once. The reason being that we might have so many TerrainTiles in a given Terrain that
they no longer fit into memory.
