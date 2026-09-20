# Voyage Router v1 — Single-Forecast A* Router

A weather-routing tool: given two points on the ocean, find the route that minimises a blend of distance, fuel and time, using one deterministic weather forecast. Search core is A* over a time-dependent state space. `PROJECT.md` remains the full design; this file is the buildable v1 slice.

## 1. Scope

**In v1**
- Land-avoiding reference path (`searoute`) buffered into a corridor polygon.
- One weather member (GEFS-Wave control member `c00`), cropped to the corridor.
- Vessel response model (Holtrop-Mennen + added wave resistance + wind resistance → fuel).
- Landmask.
- A* over the corridor grid with the edge cost from a single scenario.
- One solve from start to destination.

**Deferred to v2**
- The 10-member ensemble and CVaR aggregation of edge costs.
- Plan-consistency penalty against a previous route.
- Forecast uncertainty cone.
- Receding-horizon and event-triggered replanning (v1 solves once over the whole voyage).

**Constraints (unchanged)**: no real vessel data (one generic hull), no external benchmarking claims, any origin/destination on the globe, no regulatory-cost objective.

## 2. Pipeline

```
start, end
   -> searoute reference path (LineString)
   -> corridor polygon (buffer) + bounding box
   -> crop the global GEFS-Wave cache (control member, all steps) to the bounding box, in memory
   -> build grid nodes: inside corridor AND sea  (valid nodes)
   -> A* over (node, time) states; edge cost from the vessel model + weather
   -> backtrack parent records -> route legs -> totals
```

## 3. Conventions

| Item | Convention |
|---|---|
| API points | `[lat, lon]` (Leaflet order, as sent by the frontend) |
| `searoute` points | `[lon, lat]` — swap before calling |
| Grid node longitude | -180..180 (the dataset's longitude axis is normalised at load), same as the corridor polygon, landmask and output |
| Speed | knots in the search; `m/s` for Holtrop (`V_ms = kn × 0.514444`) |
| Distance | nautical miles |
| Time `t` | hours since the forecast cycle time |
| Directions | degrees true; weather directions are "coming from" |
| Resistance / power | N / kW |

## 4. Parameters

| Name | Meaning | Default / note |
|---|---|---|
| `bufferNm` | corridor half-width | 300 |
| `gridSpacing` | node spacing | 0.25° (the native GEFS-Wave grid) |
| `speeds` | candidate speeds through water | 5 values across the vessel's service range |
| `binHours` | time-bin width | 3 (= forecast step); 1–3 |
| `alpha` | fuel vs time weight, 0..1 | user parameter |
| `wDist` | weight on raw distance ($/nm) | 0 initially; experimental |
| `priceFuel`, `priceTime` | $/tonne, $/hour | representative constants |
| `sfoc` | specific fuel consumption | ~190 g/kWh |
| `eta` | overall propulsive efficiency | assumed constant, tunable |
| `wWave`, `wWind` | 0..1 resistance toggles | 1 |

## 5. Components

### 5.1 Vessel response model

Given speed, heading and weather for one leg, return fuel burned.

```
R_total = R_calm + wWave * R_wave + wWind * R_wind          [N]
P_E     = R_total * V_ms / 1000                             [kW, effective power]
P_B     = P_E / eta                                         [kW, brake power]
fuelKg  = P_B * sfoc * timeH / 1000
```

- **R_calm**: Holtrop-Mennen, `totalResistance(...)` in `CalmWaterResistance.py`, driven by a `Vessel`.
- **R_wave**: STAWAVE-2 (ISO 15016). Inputs: significant wave height, wave period, relative wave heading (`waveDir − heading`), ship dimensions, speed. Always ≥ 0. Equation taken from the standard.
- **R_wind**: `0.5 * rho_air * C_D * A_front * V_app² * cos(theta_app)`. Apparent wind = true wind vector − ship velocity vector; `theta_app` is the apparent wind angle off the bow (negative resistance for a tailwind).
- Speed through water = speed over ground (no currents). Speed is a prescribed choice, so there is no speed-loss model.

`Vessel` needs two added fields: `frontalWindageArea`, `windDragCoeff`.

### 5.2 Reference path and corridor (implemented in `classes.py`, `Route`)

`getBaseRoute()` → `searoute` GeoJSON Feature. `getCorridorPolygon(bufferNm)`: reproject the LineString EPSG:4326 → EPSG:3857 (meters), buffer by `bufferNm * 1852`, reproject back. Buffering in degrees would give an uneven physical width. `getCorridorBoundingBox()` returns `leftlon, rightlon` (`% 360`), `toplat, bottomlat`. The `% 360` was for the NOMADS filter; with the global cache, crop using the polygon's raw `min/max` lon (-180..180) instead. `isInsideCorridor(lon, lat)` is a point-in-polygon test.

### 5.3 Landmask

A boolean raster (`True` = sea) aligned to the GEFS-Wave grid, rasterized once from Natural Earth or GSHHG land polygons and cached to disk. `isSea(node)` is an array lookup.

### 5.4 Weather data

- **Source**: NOMADS `filter_gefs_wave_0p25.pl`, control member `c00`, one file per forecast step, `lev_surface=on`, **global** (no subregion). Downloaded once per forecast cycle and stored on disk as a single xarray-readable dataset (NetCDF/Zarr), so a query makes no API calls. Refresh when a new cycle is published. At load time, normalise the longitude axis to -180..180 and sort it, so it matches the corridor polygon and a crop is a plain slice. Per query, the corridor bounding box crops the global dataset into in-memory numpy arrays (`weatherField`). Variables (all on the same 0.25° grid):

| Variable | Meaning |
|---|---|
| `HTSGW` | significant wave height |
| `PERPW` | peak wave period |
| `DIRPW` | primary wave direction |
| `WIND` | 10 m wind speed |
| `WDIR` | 10 m wind direction |

- **Time axis**: `validHours = [0, 3, …, 240, 246, 252, …, 384]` — 3-hourly to f240, then 6-hourly. Not uniform, so lookups search this list rather than dividing by a fixed step.
- **Lookup (simplification, no interpolation)**: `weatherAt(node, t)` returns the values at the node itself (nodes sit on grid points) at the valid hour nearest to `t`, clamped to the last step if the voyage outlasts the forecast. It indexes the cropped numpy arrays by integer position. Do not call `ds.sel(..., method="nearest")` inside the search: the search does this lookup thousands of times per query, and label-based xarray selection is far slower than an array index. Directions are used as-is, so no circular averaging.
- **Edge weather**: an edge A→B uses the weather at its start node A at the departure time.

### 5.5 Search grid: the implicit graph

No graph object is built or stored.
- **Nodes** are `(row, col)` indices into the cropped weather arrays. Integer indices make exact dictionary keys and make the weather lookup a direct array index. `nodeToLatLon(node)` reads the arrays' coordinate axes.
- **Valid nodes** = corridor test AND sea. Built once per query as a set.
- **Edges** exist only as the output of `neighbors()`: 8 adjacent cells × `len(speeds)` speeds (~40 moves per node). Edge cost depends on departure time, so a stored edge list would be meaningless.
- A diagonal move also requires both flanking cells to be sea, so an edge cannot clip a land corner.

## 6. Search

### 6.1 State, key, time bins

- **State** = `(node, arrival time)`. Node alone is not enough: the cost of leaving a node depends on when you leave (the forecast changes), so an early expensive arrival can beat a late cheap one. Plain node-keyed Dijkstra/A* would discard the wrong one.
- Speed is a free choice, so arrival times are continuous and states would almost never coincide. **Time bins** make "visited" meaningful:

```
timeBin(t) = floor((t - t0) / binHours)
key        = (node, timeBin(arrival))
```

- Two arrivals at the same node in the same bin are treated as the same situation; the cheaper survives. Arrivals in different bins are never compared, so both survive.
- The **exact** arrival time is still stored in the queue entry and parent record and is used for weather lookup and further expansion. Only the key uses the bin.
- Wider bins: faster, coarser. Narrower: more accurate, more states.

### 6.2 Data structures

| Structure | Key → value / contents | Filled by | Read by |
|---|---|---|---|
| `globalWeather` | xarray Dataset, global 0.25°, all variables and valid hours, on disk | `downloadGlobalWeather` (once per cycle) | `cropWeather` |
| `weatherField` | per variable: numpy array `[step, row, col]` cropped to the corridor, plus `validHours`, lat/lon axes | `cropWeather` (once per query) | `weatherAt` |
| `landMask` | bool array `[row, col]`, `True` = sea | built once from coastline data | `isSea`, `buildGrid` |
| `validNodes` | set of `(row, col)` | `buildGrid` | `neighbors`, `snapToNode` |
| `openQueue` | binary heap (`heapq`) of `(f, counter, g, node, arrivalTime)`, ordered by `f = g + h`; `counter` is an increasing int that breaks ties | `aStar` (seed push, then pushes during expansion) | `aStar` (pop = cheapest `f`) |
| `bestCost` | `(node, timeBin)` → lowest `g` found so far | `aStar` on each accepted move | `aStar` comparison and stale check |
| `parent` | `(node, timeBin)` → `{prevKey, speedKn, headingDeg, distNm, timeH, fuelKg, arrivalTime, g}`; start maps to `None` | `aStar`, written together with `bestCost` | `reconstructPath` |
| `cMin` | float: minimum possible cost per nm | `minCostPerNm` (once per query) | `heuristic` |

`g` = cost so far. `h` = estimated remaining cost. `bestCost` and `parent` are always written together, so a cost never sits with the wrong parent.

### 6.3 Functions

**Grid and geometry**

| Function | Parameters | Returns | Does |
|---|---|---|---|
| `buildGrid` | `corridorPolygon`, `weatherField`, `landMask` | `validNodes` | Keeps nodes that are inside the corridor (longitude converted to -180..180) and sea. |
| `nodeToLatLon` | `node`, `weatherField` | `(lat, lon)` | Reads the coordinate axes. |
| `snapToNode` | `lat`, `lon`, `validNodes`, `weatherField` | `node` | Nearest valid node; used for start and goal. |
| `isSea` | `node`, `landMask` | `bool` | Array lookup. |
| `haversineNm` | `latA, lonA, latB, lonB` | `nm` | Great-circle distance. |
| `bearingDeg` | `latA, lonA, latB, lonB` | `deg true` | Initial bearing A→B. |

**Weather**

| Function | Parameters | Returns | Does |
|---|---|---|---|
| `downloadGlobalWeather` | `cycleDate`, `validHours` | path to the stored dataset | Downloads one global file per step for the five variables, combines them into one dataset with the longitude axis normalised to -180..180, saves to disk. Run once per cycle. Replaces the current f000/HTSGW-only download. |
| `cropWeather` | `globalWeather`, `bbox` | `weatherField` | Slices the global dataset to `bbox` and converts to numpy arrays. Once per query, no network. |
| `weatherAt` | `node`, `t`, `weatherField` | `{Hs, Tp, waveDir, windSpeed, windDir}` | Nearest valid hour to `t` (clamped), values at `node`. |

**Vessel**

| Function | Parameters | Returns | Does |
|---|---|---|---|
| `totalResistance` | see `CalmWaterResistance.py` | `R_calm` (N) | Holtrop-Mennen. Exists. |
| `addedWaveResistance` | `vessel, Hs, Tp, relWaveHeading, speedMs` | `N` | STAWAVE-2. New; named to avoid clashing with Holtrop's `waveResistance`. |
| `windResistance` | `vessel, windSpeedMs, windDirFrom, headingDeg, speedMs` | `N` | Apparent-wind drag; may be negative. New. |
| `legFuel` | `vessel, speedKn, headingDeg, timeH, weather` | `fuelKg` | Applies the section 5.1 formulas. New. |

**Search**

| Function | Parameters | Returns | Does |
|---|---|---|---|
| `timeBin` | `t, t0, binHours` | `int` | Bin index. |
| `neighbors` | `node, departureTime, validNodes, landMask, speeds, weatherField` | list of moves `{nextNode, speedKn, headingDeg, distNm, arrivalTime}` | Generates legal moves only: 8 cells × speeds, skipping invalid nodes and land-clipping diagonals. No cost here. `arrivalTime = departureTime + distNm / speedKn`. |
| `edgeCost` | `node, move, departureTime, vessel, weatherField, params` | `(cost, fuelKg, timeH)` | Looks up weather at `node` for `departureTime`, computes fuel with `legFuel`, then blends (formula below). |
| `minCostPerNm` | `vessel, speeds, params` | `cMin` | Cheapest calm-water cost per nm across `speeds`. |
| `heuristic` | `node, goal, cMin, weatherField` | cost units | `haversineNm(node, goal) * cMin`. |
| `aStar` | `startNode, goalNode, t0, validNodes, vessel, weatherField, params` | goal key or `None` | The search loop (6.4). |
| `reconstructPath` | `parent, goalKey` | list of legs | Backtracks (6.6). |
| `summarizeRoute` | `legs` | totals, sets `Route` attributes | Sums distance, fuel and time. |

**Edge cost (v1, single scenario)**

```
timeH   = distNm / speedKn
cost    = wDist * distNm
        + alpha       * (fuelKg / 1000) * priceFuel
        + (1 - alpha) * timeH * priceTime
```

### 6.4 Algorithm flow

**Setup, once per query**
1. Corridor polygon and bounding box from the reference path.
2. `cropWeather(globalWeather, bbox)`.
3. `buildGrid` → `validNodes`.
4. `snapToNode` the start and end points → `startNode`, `goalNode`.
5. `cMin = minCostPerNm(...)`.
6. Seed: push `(h(start), 0, 0, startNode, t0)`; `bestCost[(startNode, 0)] = 0`; `parent[(startNode, 0)] = None`.

**Loop**, while `openQueue` is not empty:
1. Pop the entry with the lowest `f`. Compute `key = (node, timeBin(arrivalTime))`.
2. **Stale check**: if `g > bestCost[key]`, skip. A cheaper way to this key was found after this entry was pushed.
3. **Goal check**: if `node == goalNode`, stop and return this key. The queue yields lowest `f` first and `h` never overestimates, so the first goal state popped is optimal (up to the time-bin approximation).
4. For each move from `neighbors(node, arrivalTime, …)`:
   - `(cost, fuelKg, timeH) = edgeCost(node, move, arrivalTime, …)`
   - `g2 = g + cost`; `key2 = (move.nextNode, timeBin(move.arrivalTime))`
   - **Comparison**: if `key2` is not in `bestCost` or `g2 < bestCost[key2]`: set `bestCost[key2] = g2`, set `parent[key2]` to the leg record, push `(g2 + h(move.nextNode), counter, g2, move.nextNode, move.arrivalTime)`. Otherwise discard the move; it never enters the queue.

If the queue empties, there is no route inside the corridor.

Heap entries cannot be edited, so a cheaper find pushes a new entry and leaves the old one to be skipped by the stale check.

### 6.5 Heuristic

```
fuelPerNm(v) = P_B_calm(v) * sfoc / 1e6 / v         [tonnes per nm; v in knots, P_B_calm in kW]
costPerNm(v) = wDist + alpha * priceFuel * fuelPerNm(v) + (1 - alpha) * priceTime / v
cMin         = min over speeds of costPerNm(v)
h(node)      = haversineNm(node, goal) * cMin
```

- Never overestimates: great-circle is the shortest possible distance, and the cheapest calm-water cost per nm is a floor because wave resistance is ≥ 0.
- **Caveat**: a tailwind can make `R_wind` negative. Either clamp `R_wind` at 0 or lower `cMin` by the largest possible tailwind saving. Otherwise `h` can overestimate and A* may return a non-optimal route.
- Weather does not appear in `h`, so `h` is valid for any forecast.

### 6.6 Getting the route

1. Start at the goal key.
2. Read `parent[key]`. It holds the leg that led here and `prevKey`.
3. Move to `prevKey`; repeat until `parent` is `None` (the start).
4. Reverse the collected legs.

Each leg: `{lat, lon, speedKn, arrivalTime, distNm, timeH, fuelKg}` — `lat/lon` from `nodeToLatLon`, `speedKn` is the speed used to reach that point from the previous one. `summarizeRoute` gives:

```
distance     = sum(distNm)
totalTimeH   = sum(timeH)
totalFuel    = sum(fuelKg) / 1000            [tonnes]
averageSpeed = distance / totalTimeH         [kn]
```

These populate `Route.distance`, `Route.totalFuel`, `Route.averageSpeed` and the position list `Route.optimizedRute` (spelled that way in `classes.py`). Positions go to the frontend as `[lat, lon]`.

## 7. Known gaps

- **Antimeridian**: corridors crossing 180° are not handled. With the longitude axis normalised to -180..180, the Greenwich crossing (West Africa → Turkey) is now a plain slice, but a corridor that straddles ±180° would still need two slices and a split polygon.
- **Memory**: the global dataset is about 2 GB as float32 (721 × 1440 points × 5 variables × 105 steps). Keep it on disk and open it lazily; only the per-query crop goes into memory.
- **Stale cache**: query results are only as current as the last downloaded cycle. Store the cycle time with the dataset and use it as the reference for `t`.
- **`Route` point order**: `getBaseRoute()` passes `startPoint`/`endPoint` straight to `searoute`, which needs `[lon, lat]`; the API sends `[lat, lon]`.
- **Voyage longer than the forecast** (384 h): weather is clamped to the last step.
- **Time-bin approximation**: same-bin arrivals are merged, so optimality is up to the bin width.
- **Nearest-step weather**: cost changes in steps at forecast-time boundaries.
- **Existing download code** (`utils.py`) pulls only global f000 `HTSGW`; it must be replaced by `downloadGlobalWeather`.
