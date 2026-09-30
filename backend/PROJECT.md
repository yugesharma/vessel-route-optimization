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
| `speeds` | candidate speeds through water | `[6, 8, 10, 12, 14]` kn |
| `timeBinSize` | time-bin width (h) | 3 (= forecast step) |
| `fuelTimeWeight` | fuel vs time weight, 0..1 | user parameter ("Fuel vs. Time" slider); default 0.5 |
| `distanceWeight` | weight on raw distance (per nm) | user parameter ("Distance Weight" slider); default 1.0 |
| `priceFuel`, `priceTime` | $/tonne, $/hour | not used yet (see §7, cost scale) |
| `sfoc` | specific fuel consumption | 175 g/kWh (assumed) |
| `eta` | overall propulsive efficiency | 0.70 (assumed) |
| `mcrKw` | engine maximum continuous rating | 27000 kW (assumed); a leg needing more than 90 % of it is infeasible |
| `wWave`, `wWind` | 0..1 resistance toggles | not implemented; the frontend's wind/wave sliders are sent but unused |

## 5. Components

### 5.1 Vessel response model

Given speed, heading and weather for one leg, return fuel burned.

```
R_total = R_calm + max(0, R_wave)                           [N]  (R_wind not implemented yet)
P_E     = R_total * V_ms / 1000                             [kW, effective power]
P_B     = P_E / eta                                         [kW, brake power]
fuelKg  = P_B * sfoc * timeH / 1000
```

If `P_B > 0.9 * mcrKw` the leg is infeasible: `legFuel` returns `None` and the move is skipped.

- **R_calm**: Holtrop-Mennen, `calmWaterResistance(V, waterTemp, vessel)` in `calmWaterResistance.py`.
- **R_wave**: SNNM (ITTC 7.5-04-01-01.1 Rev 08 2024, App. G.3), all headings. Inputs: significant wave height, wave period, relative wave heading (`waveDir − heading`), ship dimensions incl. waterline entrance/run lengths `LE`/`LR` (estimated from Holtrop if unknown), speed. May be slightly negative in stern-quarter/following seas; `legFuel` floors it at 0 so no leg costs less than calm water, which keeps the heuristic admissible. Equation taken from the standard.
- **R_wind** (not implemented yet): `0.5 * rho_air * C_D * A_front * V_app² * cos(theta_app)`. Apparent wind = true wind vector − ship velocity vector; `theta_app` is the apparent wind angle off the bow (negative resistance for a tailwind).
- Speed through water = speed over ground (no currents). Speed is a prescribed choice, so there is no speed-loss model.

`Vessel` needs two added fields: `frontalWindageArea`, `windDragCoeff`.

### 5.2 Reference path and corridor (`classes/route.py` `Route`, `classes/navGrid.py` `NavGrid`)

`Route.getBaseRoute()` → `searoute` GeoJSON Feature. `NavGrid.buildCorridor(baseRoute, bufferNm=300)`: reproject the LineString EPSG:4326 → EPSG:3857 (meters), buffer by `bufferNm * 1852`, reproject back. Buffering in degrees would give an uneven physical width. `getCorridorBoundingBox()` returns `leftlon, rightlon, toplat, bottomlat` from the polygon's raw bounds (lon -180..180). The corridor test is done for the whole grid at once in `buildGrid` with `shapely.contains_xy`.

### 5.3 Landmask

A boolean raster (`True` = sea) aligned to the GEFS-Wave grid, stored at `data/geographicData/sea_mask_0.25deg.nc`. `GeographicDataService.getSeaMask(bbox)` crops it per query to `seaMask`; `buildGrid` uses it directly (raises if its grid differs from the weather grid).

### 5.4 Weather data

- **Source**: NOMADS `filter_gefs_wave_0p25.pl`, control member `c00`, one file per forecast step, `lev_surface=on`, **global** (no subregion). Downloaded once per forecast cycle (per-step GRIBs in `data/weatherData/steps_{date}/`, skipped if already present) and combined into `data/weatherData/weather_{date}_7day.nc`, so a query makes no API calls. Refresh when a new cycle is published. At load time, normalise the longitude axis to -180..180 and sort it, so it matches the corridor polygon and a crop is a plain slice. Per query, the corridor bounding box crops the global dataset into in-memory numpy arrays (`weatherField`). Variables (all on the same 0.25° grid):

| NOMADS variable | Dataset name | Meaning |
|---|---|---|
| `HTSGW` | `swh` | significant wave height |
| `PERPW` | `perpw` | peak wave period |
| `DIRPW` | `dirpw` | primary wave direction |
| `WIND` | `ws` | 10 m wind speed |
| `WDIR` | `wdir` | 10 m wind direction |

- **Time axis**: `FORECAST_HOURS = [0, 3, …, 168]` — 3-hourly, 7 days, 57 steps. (GEFS-Wave goes to f384, 6-hourly after f240; only the first 7 days are downloaded.) Lookups search the step hours rather than dividing by a fixed step.
- **Lookup (simplification, no interpolation)**: `weatherAt(node, t)` (`EnvironmentDataService`) returns the values at the node itself (nodes sit on grid points) at the valid hour nearest to `t`, clamped to the last step if the voyage outlasts the forecast. It indexes the cropped numpy arrays by integer position. Do not call `ds.sel(..., method="nearest")` inside the search: the search does this lookup thousands of times per query, and label-based xarray selection is far slower than an array index. Directions are used as-is, so no circular averaging.
- **Edge weather**: an edge A→B uses the weather at its start node A at the departure time.

### 5.5 Search grid: the implicit graph

No graph object is built or stored.
- **Nodes** are `(row, col)` indices into the cropped weather arrays. Integer indices make exact dictionary keys and make the weather lookup a direct array index. `nodeToCoordinates(node)` reads the arrays' coordinate axes.
- **Valid nodes** = corridor test AND sea AND wave data present at every step. Built once per query as a set.
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
| `globalWeather` | xarray Dataset, global 0.25°, all variables and steps, on disk | `getWeatherForecast` (once per cycle) | `cropWeather` |
| `weatherField` | cropped xarray Dataset; plus `arrays` (per variable numpy `[step, row, col]`), `stepHours`, `validHours` | `cropWeather` (once per query) | `weatherAt`, `buildGrid` |
| `seaMask` | bool DataArray `[row, col]`, `True` = sea, cropped to the bbox | `getSeaMask` (once per query) | `buildGrid` |
| `validNodes` | set of `(row, col)` | `buildGrid` | `neighbors`, `snapToNode` |
| `openList` | binary heap (`heapq`) of `(f, counter, g, h, node, arrivalTime)`, ordered by `f = g + h`; `counter` breaks ties | `aStar` (seed push, then pushes during expansion) | `aStar` (pop = cheapest `f`) |
| `bestCost` | `(node, timeBin)` → lowest `g` found so far | `aStar` on each accepted move | `aStar` comparison and stale check |
| `parents` | `(node, timeBin)` → `(prevKey, speedKn, headingDeg, distNm, timeH, arrivalTime, g, fuelKg)`; start maps to `None` | `aStar`, written together with `bestCost` | `reconstructPath` |
| `costMin` | float: minimum possible cost per nm | `setup` (once per query) | `heuristic` |

`g` = cost so far. `h` = estimated remaining cost. `bestCost` and `parents` are always written together, so a cost never sits with the wrong parent.

### 6.3 Functions

**Grid and geometry**

| Function | Parameters | Returns | Does |
|---|---|---|---|
| `NavGrid.buildGrid` | `seaMask`, `weatherField` | `validNodes` | Keeps nodes that are inside the corridor, sea, and have wave data at every step. |
| `NavGrid.nodeToCoordinates` | `node` | `(lat, lon)` | Reads the coordinate axes. |
| `NavGrid.snapToNode` | `point` (`[lon, lat]`) | `node` | Nearest valid node (linear scan); used for start and goal. |
| `geod.inv` (pyproj, WGS84) | `lonA, latA, lonB, latB` | `(azimuth, backAzimuth, m)` | Geodesic distance and initial bearing A→B; used by `neighbors` and `heuristic`. |

**Weather**

| Function | Parameters | Returns | Does |
|---|---|---|---|
| `getWeatherForecast` | `weatherDir` | path to the stored dataset | Returns today's combined file if present; otherwise `downloadWeatherData` (one global file per step, five variables) then `combineWeatherForecast` (concat on step, longitude normalised to -180..180, saved as NetCDF). Run once per cycle. |
| `EnvironmentDataService.cropWeather` | `globalWeather`, `bbox` | `weatherField` | Slices the global dataset to `bbox` and converts to numpy arrays. Once per query, no network. |
| `EnvironmentDataService.weatherAt` | `node`, `t` | `{Hs, Tp, waveDir, windSpeed, windDir}` | Nearest step to `t` (clamped), values at `node`. |
| `EnvironmentDataService.getCycleStart` | — | `datetime64` | Valid time of step 0 (the cycle start). |

**Vessel**

| Function | Parameters | Returns | Does |
|---|---|---|---|
| `calmWaterResistance` | `V, waterTemp, vessel` | `R_calm` (N) | Holtrop-Mennen, in `calmWaterResistance.py`. |
| `waveAddedResistance` | `vessel, Hs, Tp, relWaveHeading, speedMs` | `N` | SNNM, all headings, in `waveAddedResistance.py`. |
| `windResistance` | `vessel, windSpeedMs, windDirFrom, headingDeg, speedMs` | `N` | Apparent-wind drag; may be negative. Not implemented yet. |
| `Vessel.legFuel` | `speedKn, headingDeg, timeH, weather` | `fuelKg` or `None` | Applies the section 5.1 formulas; `None` if the leg needs more than 90 % MCR. |
| `Vessel.calmWaterFuelPerNM` | `speedKn` | kg/nm | Calm-water fuel per nautical mile; used for `costMin`. |

**Search**

| Function | Parameters | Returns | Does |
|---|---|---|---|
| `setup` | `startPoint, endPoint, dateTime, speeds, distanceWeight, fuelTimeWeight, timeBinSize` | `route, navGrid, environmentDataService, startNode, endNode, t0, costMin` | Setup steps of 6.4. |
| `calculateRoute` | `startPoint, endPoint, dateTime, distanceWeight, fuelTimeWeight` | `(route, legs)`; `legs` is `None` if no route | `setup` → `aStar` → `reconstructPath`. Sets `speeds` and `timeBinSize`. |
| `timeBin` | `t0, t, binSize` | `int` | Bin index. |
| `neighbors` | `node, departureTime, navGrid, speeds` | list of moves `(nextNode, speedKn, headingDeg, distNm, timeH, arrivalTime)` | Generates legal moves only: 8 cells × speeds, skipping invalid nodes and land-clipping diagonals. No cost here. `arrivalTime = departureTime + distNm / speedKn`. |
| `edgeCost` | `node, move, departureTime, vsl, environmentDataService, distanceWeight, fuelTimeWeight` | `(cost, fuelKg)` or `None` | Looks up weather at `node` for `departureTime`, computes fuel with `legFuel`, then blends (formula below). `None` if the leg is infeasible. |
| `heuristic` | `node, goal, navGrid, costMin` | cost units | Geodesic nm × `costMin`. Admissible: `R_wave` is floored at 0 and wind is not modelled, so no leg costs less than calm water. |
| `aStar` | `start, goal, t0, vsl, speeds, navGrid, environmentDataService, costMin, timeBinSize, distanceWeight, fuelTimeWeight` | `(goalKey, g, parents)` or `(None, None, None)` | The search loop (6.4). |
| `reconstructPath` | `parents, goalKey, navGrid, t0` | list of points | Backtracks (6.6). |
| `summarizeRoute` | `legs` | totals | Sums distance, fuel and time. Not written yet. |

**Edge cost (v1, single scenario)**

Current code (raw units, see §7 "cost scale"):

```
timeH   = distNm / speedKn
cost    = distanceWeight * distNm
        + fuelTimeWeight       * fuelKg
        + (1 - fuelTimeWeight) * timeH
```

Target (priced, not implemented yet):

```
cost    = distanceWeight * distNm
        + fuelTimeWeight       * (fuelKg / 1000) * priceFuel
        + (1 - fuelTimeWeight) * timeH * priceTime
```

### 6.4 Algorithm flow

**Setup, once per query**
1. Corridor polygon and bounding box from the reference path.
2. `cropWeather(globalWeather, bbox)`.
3. `buildGrid` → `validNodes`.
4. `snapToNode` the start and end points → `startNode`, `goalNode`.
5. `t0 = (dateTime − getCycleStart())` in hours.
6. `costMin` (6.5).
7. Seed: push `(h(start), 0, 0, h(start), startNode, t0)`; `bestCost[(startNode, 0)] = 0`; `parents[(startNode, 0)] = None`.

**Loop**, while `openQueue` is not empty:
1. Pop the entry with the lowest `f`. Compute `key = (node, timeBin(arrivalTime))`.
2. **Stale check**: if `g > bestCost[key]`, skip. A cheaper way to this key was found after this entry was pushed.
3. **Goal check**: if `node == goalNode`, stop and return this key. The queue yields lowest `f` first and `h` never overestimates, so the first goal state popped is optimal (up to the time-bin approximation).
4. For each move from `neighbors(node, arrivalTime, …)`:
   - `edgeCost(node, move, arrivalTime, …)` → `(cost, fuelKg)`; if `None` (infeasible), skip the move
   - `g2 = g + cost`; `key2 = (move.nextNode, timeBin(move.arrivalTime))`
   - **Comparison**: if `key2` is not in `bestCost` or `g2 < bestCost[key2]`: set `bestCost[key2] = g2`, set `parents[key2]` to the leg record, push `(g2 + h2, counter, g2, h2, move.nextNode, move.arrivalTime)`. Otherwise discard the move; it never enters the queue.

If the queue empties, there is no route inside the corridor.

Heap entries cannot be edited, so a cheaper find pushes a new entry and leaves the old one to be skipped by the stale check.

### 6.5 Heuristic

```
fuelPerNm(v) = calmWaterFuelPerNM(v) = P_B_calm(v) * sfoc / 1000 / v     [kg per nm; v in knots, P_B_calm in kW]
costPerNm(v) = distanceWeight + fuelTimeWeight * fuelPerNm(v) + (1 - fuelTimeWeight) / v
costMin      = min over speeds of costPerNm(v)
h(node)      = geodesicNm(node, goal) * costMin
```

`costPerNm` must use the same formula as `edgeCost`, divided by distance.

- Never overestimates: the geodesic is the shortest possible distance, and the cheapest calm-water cost per nm is a floor because `R_wave` is floored at 0 in `legFuel`.
- **Caveat**: when `R_wind` is added, a tailwind can make it negative. Either clamp it at 0 or lower `costMin` by the largest possible tailwind saving. Otherwise `h` can overestimate and A* may return a non-optimal route.
- Weather does not appear in `h`, so `h` is valid for any forecast.

### 6.6 Getting the route

1. Start at the goal key.
2. Read `parents[key]`. It holds the leg that led here and `prevKey`.
3. Move to `prevKey`; repeat until the record is `None` (the start).
4. Reverse the collected legs.

Each point: `{lat, lon, speedKn, headingDeg, arrivalTime, distNm, timeH, fuelKg}` — `lat/lon` from `nodeToCoordinates`, `speedKn`/`headingDeg` are what was used to reach that point from the previous one. The first point is the start: `speedKn`/`headingDeg` `None`, distance/time/fuel 0, `arrivalTime = t0`.

`summarizeRoute` (not written yet) gives:

```
distance     = sum(distNm)
totalTimeH   = sum(timeH)
totalFuel    = sum(fuelKg) / 1000            [tonnes]
averageSpeed = distance / totalTimeH         [kn]
```

**API**: `POST /route` returns `{basicRoute, optimizedRoute}` — `basicRoute` is the `searoute` GeoJSON Feature, `optimizedRoute` is the point list above (or `null` if no route). The frontend draws `basicRoute` in blue and `optimizedRoute` (`[lat, lon]` per point) in green; the distance and duration shown are still `basicRoute`'s.

## 7. Known gaps

- **Antimeridian**: corridors crossing 180° are not handled. With the longitude axis normalised to -180..180, the Greenwich crossing (West Africa → Turkey) is now a plain slice, but a corridor that straddles ±180° would still need two slices and a split polygon.
- **Memory**: the global dataset is about 1.2 GB as float32 (721 × 1440 points × 5 variables × 57 steps). Keep it on disk and open it lazily; only the per-query crop goes into memory.
- **Forecast cycle selection (deferred)**: `DATE_STRING` is today's *local* date and the download assumes today's 00z cycle is complete. Before NOMADS finishes publishing (a few hours after 00z UTC) the download fails with a 404 part-way through; partial steps stay on disk and resume next run. Planned fix:
  1. Compute the cycle date in UTC (`datetime.now(timezone.utc)`), not local time; on EDT the local date lags UTC from 20:00 to midnight.
  2. Pick the newest *complete* 00z cycle: one request for the last step (f168); if it's missing, fall back to the previous day (reuse the combined file on disk if present).
  3. Warn when the voyage runs past the forecast end.

  `t0 = departure − cycle start` is done. The frontend's `datetime-local` value has no timezone and is treated as UTC; an empty date gives `t0 = NaN` and the search fails.
  06z/12z/18z cycles are out of scope until fresher weather matters.
- **Point order**: the API receives `[lat, lon]`; `main.py` swaps to `[lon, lat]` before `calculateRoute`, which is what `searoute` and `snapToNode` expect.
- **Voyage longer than the forecast** (168 h): weather is clamped to the last step.
- **Cost scale**: the current `edgeCost` adds fuel in kg to time in hours. Fuel per nm is ~1000× time per nm, so fuel dominates and the slowest speed nearly always wins; the Fuel vs. Time slider has little effect. The priced formula (6.3) fixes this.
- **Time-bin approximation**: same-bin arrivals are merged, so optimality is up to the bin width.
- **Nearest-step weather**: cost changes in steps at forecast-time boundaries.
- **Old download code**: the f000/`HTSGW`-only path (`downloadWaveData`, `saveData`, `convertGribToPng`, module-level `getWeatherData` and `cropWeather`) is still in `environmentDataService.py`; `GET /` calls it.
