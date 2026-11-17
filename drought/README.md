# Drought indexes per department and month

This folder turns a drought grid into a table with one value per department of
Cameroon and per month.

The value is an **area-weighted mean**: every grid square counts by the share of
the department that lies inside it. This also works for departments that are
smaller than one grid square, like Mfoundi.

## Files

| File | What it is |
|---|---|
| `grid_to_departments.py` | the functions. This is the file to use in your own code. |
| `department_means.ipynb` | explains the method step by step, runs it for SPEI1 and SPI1, checks the result and saves the CSV |

## How to use the functions

```python
import xarray as xr
import geopandas as gpd
from grid_to_departments import make_weights, department_means

# the grid: one file per month, stacked along time
spei = xr.open_mfdataset("PATH/TO/GRID/SPEI1_*.nc", combine="nested", concat_dim="time")

# the departments: the shared file in this repo
departments = gpd.read_file("../data/boundaries/cmr_adm2_58.geojson")

weights = make_weights(spei, departments)            # once per grid
table = department_means(spei, "SPEI1", weights)     # once per index
```

`from grid_to_departments import ...` works when your notebook or script is in
this folder. Otherwise, copy the file next to your code.

| Function | Takes | Returns |
|---|---|---|
| `make_weights(ds, departments)` | the grid, the departments table | one row per piece of a grid square inside a department: `lat`, `lon`, `shapeName`, `area_km2`, `weight` |
| `department_means(ds, var, weights)` | the grid, the name of its data variable (for example `"SPEI1"`), the weights | one row per department and month: `shapeName`, `time`, and the index |

The weights depend only on the grid and the borders. If several indexes are on
the same grid (SPI1 and SPEI1 are), compute the weights once and use them for all.

## How it works

1. **Squares:** every grid point is the centre of a square. The size of the
   squares is read from the grid.
2. **Cut:** the squares are cut along the department borders (`overlay`). Each
   piece keeps the `lat` and `lon` of its square.
3. **Weights:** the area of every piece is measured in an equal-area projection
   (EPSG:6933). weight = area of the piece / area of its department, so the
   weights of one department add up to 1.
4. **Mean:** every piece gets the value of its square, values are multiplied by
   the weights and added up per department and month.

**Missing values:** if some squares of a department have no value in a month,
the sum is divided by the weights of the squares that do have one. If none have
a value, the result is `NaN`.

## Data needed

The grid files are **not** in the repo. They are monthly files from ERA5–Drought,
on a 0.25 degree grid, cut to the box 13.5 N, 1.25 N, 8 E, 16.5 E:

- dataset: https://cds.climate.copernicus.eu/datasets/derived-drought-historical-monthly
- reference period of the indexes: 1991 to 2020
- used here: SPEI1 and SPI1, January 1996 to December 2025 (360 files each)

Before you run the notebook, set the three paths in the cell **File paths** at
the top of the notebook:

| Path | What it is | Default |
|---|---|---|
| `GRID_DIR` | folder with the grid files | `../../../data/raw` (change this) |
| `BOUNDARIES_FILE` | the department borders in this repo | `../data/boundaries/cmr_adm2_58.geojson` (no need to change) |
| `OUTPUT_DIR` | folder for the final CSV, outside the repo | `../../../data/processed` (change this) |

The paths are relative to the notebook. `..` means one folder up.

The department borders are in `../data/boundaries/` (see the README there).

## Result

`department_means.ipynb` writes a CSV with one row per department and month and
the columns `shapeName`, `time`, `SPEI1`, `SPI1`: 58 departments x 360 months =
20,880 rows. The CSV is not in the repo, because the repo ignores `*.csv`.

Checks done in the notebook: 58 departments, 360 months for every department and
no month twice, weights of every department add up to 1, and a plot of one
department over time.

## Known limits

- **EDDI is not included yet**, because the data is not there yet.
- **SPI1 has 8 missing values** (February 2019 in seven northern departments,
  December 2008 in Faro). In those months no square of the department had a value.
- **Little data:** a mean is given as long as at least one square of the
  department has a value. 66 SPI1 results are based on less than half of their
  department, all in the north.
- **Extreme values** are kept as they are in the files. Some department means
  are far outside the usual range of -3 to 3 (down to -8.2).

## Credits

### Drought data

**Data:** ERA5–Drought, produced by the European Centre for Medium-Range Weather
Forecasts (ECMWF) for the Copernicus Climate Change Service, from the Climate
Data Store:
https://cds.climate.copernicus.eu/datasets/derived-drought-historical-monthly

> Keune, J., Di Giuseppe, F., Barnard, C., Damasio da Costa, E., and Wetterhall, F.
> (2025): ERA5–Drought: Global drought indices based on ECMWF reanalysis.
> Scientific Data 12, 616. https://doi.org/10.1038/s41597-025-04896-y

Contains modified Copernicus Climate Change Service information (2026).

**Licence:** Creative Commons Attribution 4.0 International (CC BY 4.0),
https://creativecommons.org/licenses/by/4.0/, as stated in the grid files.

**Changes:** the grid values are not used as they are. They were turned into
area-weighted means per department and month, and SPEI1 and SPI1 were merged
into one table. The CSV made by the notebook therefore contains modified data.

### Department borders

geoBoundaries (Runfola et al., 2020), CC BY 4.0. Modified: two departments
merged. Full credit in `../data/boundaries/README.md`.

### When you share or use the results

Give this credit wherever the CSV or anything made from it is shared or shown:

- **With the CSV:** name both sources, the licence, and that the values are
  department means computed from the original grids.
- **In a report:** cite both papers and say in the data section what was done.
- **Under a map or plot:** "Data: ERA5–Drought (Keune et al., 2025);
  boundaries: geoBoundaries (Runfola et al., 2020)".
