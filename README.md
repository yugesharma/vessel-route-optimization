# Vessel Route Optimization

A weather-routing web app for ships. Pick two points on the ocean and a departure time; it returns the route that minimises a blend of fuel cost, time cost and distance, using the current 7-day wave and wind forecast, and draws the search on the map as it runs.

## What it does

- Finds a land-avoiding reference route between any two sea points, then searches a 300 nm corridor around it for a cheaper one.
- Runs a time-dependent A\* search over the 0.25° NOAA GEFS-Wave forecast grid (3-hourly, 7 days). Each move picks a heading and one of five speeds (6 to 14 kn), so the route can slow down, speed up or go around bad weather.
- Prices every leg with a vessel model: Holtrop-Mennen calm-water resistance, added resistance in waves (SNNM, ITTC 7.5-04-01-01.1) and wind resistance (Park et al. 2024), converted to engine power and fuel burned.
- Rejects legs the ship cannot sail: waves above the operating limit (8 m significant height) or power above 90 % of engine MCR.
- Streams explored nodes and the current best path to the browser over a WebSocket, and shows the wave forecast as a map overlay with a forecast-hour slider.
- Reports distance, time, fuel and average speed for the optimised route next to the reference route.

The vessel is the KVLCC2 tanker (320 m), a standard published hull. Fuel prices and time-charter rates are defaults in the code.

## How it works

```
start, end, departure time
   -> reference sea route (searoute)
   -> corridor polygon (300 nm buffer) + bounding box
   -> crop the global forecast and sea mask to the box
   -> valid nodes: inside corridor AND sea AND wave data at every step
   -> A* over (grid node, 3 h time bin) states
        edge cost = distance + fuel cost + time cost, from the vessel model and the weather at both ends of the leg
        heuristic = geodesic distance x cheapest calm-water cost per nm
   -> backtrack -> legs with speed, heading, arrival time and fuel
```

The state includes arrival time because the cost of leaving a node depends on when the ship gets there. Wave and wind resistance are floored at zero, so no leg is cheaper than calm water and the heuristic never overestimates.

`backend/PROJECT.md` has the full design: conventions, data structures, cost formulas and known gaps.

## Stack

| Part | Tools |
|---|---|
| Backend | Python, FastAPI, WebSockets, xarray, cfgrib, NumPy, shapely, pyproj, searoute |
| Frontend | React, TypeScript, Vite, Leaflet (react-leaflet) |
| Data | NOAA GEFS-Wave 0.25° (NOMADS), control member: wave height, period, direction, wind speed, wind direction |
| Tests | pytest |

## Run it

Requirements: Python 3.14+, [uv](https://docs.astral.sh/uv/), Node.js.

**Backend**

```bash
cd backend
uv sync
echo "GEOAPIFY_API_KEY=your_key" > .env    # used for place-name search
uv run fastapi dev main.py                 # http://localhost:8000
```

The backend needs a 0.25° sea mask at `backend/data/geographicData/sea_mask_0.25deg.nc` (the `data/` folder is not in the repo).

On first start each day the backend downloads the latest 00z forecast (57 GRIB2 files), combines them into one NetCDF file and renders the wave overlays. This takes a few minutes; later starts reuse the files.

**Frontend**

```bash
cd frontend
npm install
npm run dev                                # http://localhost:5173
```

Click the map (or search by name) to set the start and end points, choose a departure time inside the forecast window, and press generate.

## API

| Endpoint | Purpose |
|---|---|
| `GET /baseRoute` | Reference sea route between two points (GeoJSON) |
| `POST /optimizedRoute` | Optimised route as a list of legs |
| `WS /ws/route` | Same search, streaming progress then the result |
| `GET /geocode` | Place name to coordinates |
| `GET /overlays` | Forecast date and valid hours of the wave overlays |

## Tests

```bash
cd backend
uv run pytest
```

- Calm-water resistance matches the published Holtrop-Mennen worked example within 1 %.
- Wave added resistance calculations match the ones in the research paper for correctness.
- A leg above 90 % MCR is rejected; negative added wave resistance is floored at zero.
- Wind resistance is positive in a head wind, negative in a following wind and symmetric port/starboard; a tailwind never makes a leg cheaper than calm water.
- A\* on a small grid goes straight in calm weather and routes around a block of high waves.

## Limitations

- One generic hull and one forecast member; no currents.
- Weather is taken at the nearest forecast step, and voyages longer than 7 days reuse the last step.
- Routes crossing the antimeridian (180°) are not supported.

## References

- Holtrop, J. and Mennen, G.G.J. (1982). An approximate power prediction method.
- ITTC Recommended Procedure 7.5-04-01-01.1 (2024), Appendix G: SNNM added resistance in waves.
- Park et al. (2024). J. Mar. Sci. Eng. 12, 1694: wind resistance coefficients.
- SIMMAN 2014: KVLCC2 particulars.
