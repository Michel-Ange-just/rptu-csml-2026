"""Turn a drought grid into one value per department and month.

The value is an area-weighted mean: every grid square counts by the share
of the department that lies inside it.

How to use it:

    import xarray as xr
    import geopandas as gpd
    from grid_to_departments import make_weights, department_means

    spei = xr.open_mfdataset("data/raw/SPEI1_*.nc", combine="nested", concat_dim="time")
    departments = gpd.read_file("repo/rptu-csml-2026/data/boundaries/cmr_adm2_58.geojson")

    weights = make_weights(spei, departments)             # once per grid
    table = department_means(spei, "SPEI1", weights)      # once per index
"""

import geopandas as gpd
from shapely.geometry import box


def to_square(ds, half):
    """Step A: make one square around every grid point.

    ds   - the grid dataset, with the coordinates "lat" and "lon"
    half - half the side of one square, in degrees

    Returns a table with one row per square: lat, lon, geometry.
    """
    # three lists that grow together: position i in each list belongs to square i
    latitudes = []
    longitudes = []
    boxes = []

    # every latitude combined with every longitude is one grid point
    for lat in ds["lat"].values:
        for lon in ds["lon"].values:
            latitudes.append(lat)
            longitudes.append(lon)
            # box takes the edges in this order: west, south, east, north
            boxes.append(box(lon - half, lat - half, lon + half, lat + half))

    # EPSG:4326 - longitude and latitude in degrees
    return gpd.GeoDataFrame({"lat": latitudes, "lon": longitudes}, geometry=boxes, crs="EPSG:4326")


def make_weights(ds, departments):
    """Steps A, B and C: find the weight of every grid square in every department.

    ds          - the grid dataset, with the coordinates "lat" and "lon"
    departments - table of the departments, with the columns "shapeName" and "geometry"

    Returns a table with one row per piece (one square inside one department):
    lat, lon, shapeName, area_km2, weight.
    The weights of one department add up to 1.

    The weights depend only on the grid and the borders, not on the month or
    the index. Compute them once and use them for SPI, SPEI and EDDI.
    """
    # the grid points are one square apart, so half of that distance is half a square
    # (0.125 degrees for a 0.25 degree grid); read from the grid, so other grids work too
    lats = ds["lat"].values
    half = abs(lats[1] - lats[0]) / 2

    # step A: one square per grid point
    cells = to_square(ds, half)

    # step B: cut the squares along the department borders
    pieces = gpd.overlay(cells, departments, how="intersection")

    # step C: area of every piece, measured in an equal-area system (EPSG:6933, metres)
    pieces["area_km2"] = pieces.to_crs("EPSG:6933").area / 1e6

    # total area of the department, written into every row of that department
    total = pieces.groupby("shapeName")["area_km2"].transform("sum")

    # share of the department that lies in this piece
    pieces["weight"] = pieces["area_km2"] / total

    return pieces[["lat", "lon", "shapeName", "area_km2", "weight"]]


def department_means(ds, var, weights):
    """Step D: the area-weighted mean per department and month.

    ds      - the grid dataset
    var     - name of the data variable in ds, for example "SPEI1" or "SPI1"
    weights - the table from make_weights, made for the same grid

    Returns a table with one row per department and month: shapeName, time, var.
    If a department has no data at all in a month, the value is NaN.
    """
    # the grid as a table: one row for every square in every month
    values = ds[var].to_dataframe().reset_index()

    # every piece gets the value of its square, once for each month
    joined = weights.merge(values, on=["lat", "lon"])

    # value of the square times the weight of the piece
    joined["weighted"] = joined[var] * joined["weight"]

    # the weight counts only where the square has a value, otherwise 0
    joined["valid_weight"] = joined["weight"].where(joined[var].notna(), 0)

    # one group per department and month, add up both columns
    sums = joined.groupby(["shapeName", "time"])[["weighted", "valid_weight"]].sum().reset_index()

    # divide by the weights that were really used; 0 / 0 gives NaN, which means "no data"
    sums[var] = sums["weighted"] / sums["valid_weight"]

    return sums[["shapeName", "time", var]]
