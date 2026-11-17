# Cameroon department boundaries (admin 2)

`cmr_adm2_58.geojson` holds the borders of the 58 departments of Cameroon.
Everyone in the project should use this file, so that our tables match.

## What is in the file

| Column | Meaning |
|---|---|
| `shapeName` | Department name, without accents (for example `Mfoundi`, `Mbere`) |
| `geometry` | Border of the department (Polygon or MultiPolygon) |

- 58 rows, one per department
- Coordinate system: WGS84 (EPSG:4326), longitude and latitude in degrees
- Use `shapeName` as the department key. The file has no official codes.

## How to load it

```python
import geopandas as gpd

departments = gpd.read_file("data/boundaries/cmr_adm2_58.geojson")
```

## Source

- geoBoundaries, Cameroon, level ADM2, boundaries representative of 2016
- Original file: `geoBoundaries-CMR-ADM2.geojson` (the full version, not the simplified one)
- Downloaded from
  https://data.humdata.org/dataset/geoboundaries-admin-boundaries-for-cameroon
- Original data source named by geoBoundaries: Open Africa,
  https://africaopendata.org/dataset/cameroon-maps

## What was changed

The original file has 60 rows for 58 departments. Two departments are stored
as two separate pieces each (a large one and a very small one of 1 to 3 km²):

- Ndian
- Sanaga-Maritime

Changes made with geopandas:

1. Merged the rows with the same `shapeName` into one shape (`dissolve`), 60 rows → 58.
   The two departments above are now of type MultiPolygon.
2. Kept only the columns `shapeName` and `geometry`. The columns `shapeISO`,
   `shapeID`, `shapeGroup` and `shapeType` were dropped: they were empty, the same
   in every row, or no longer meaningful after merging.

The borders themselves were not changed or simplified.

The script `clean_boundaries.py` in this folder does these two steps. To make the
file again from the original download:

```
python clean_boundaries.py geoBoundaries-CMR-ADM2.geojson cmr_adm2_58.geojson
```

## Credits

**Data:** administrative boundaries courtesy of geoBoundaries,
https://www.geoboundaries.org

> Runfola D, Anderson A, Baier H, Crittenden M, Dowker E, Fuhrig S, et al. (2020)
> geoBoundaries: A global database of political administrative boundaries.
> PLoS ONE 15(4): e0231866. https://doi.org/10.1371/journal.pone.0231866

**Original source** named by geoBoundaries: Open Africa,
https://africaopendata.org/dataset/cameroon-maps

**Licence:** Creative Commons Attribution 4.0 International (CC BY 4.0),
https://creativecommons.org/licenses/by/4.0/, as stated in the metadata of the
download. (The HDX page lists the Open Database License instead. Both require
this credit.)

**Changes:** this file is modified. The two pieces of Ndian and of
Sanaga-Maritime were merged (60 rows to 58), and only the columns `shapeName`
and `geometry` were kept. See "What was changed" above.

**If you use this file**, for example in a report, slides or a map, credit
geoBoundaries and cite the paper above. A short credit under a map is enough:
"Boundaries: geoBoundaries (Runfola et al., 2020)".
