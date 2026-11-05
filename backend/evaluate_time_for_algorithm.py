import cProfile, pstats
from RouteCalculation import calculateOptimizedRoute
from route_setup import getBaseRoute

start, end = (-73.8, 40.4), (-28.0, 38.6)  
base = getBaseRoute(start, end)

with cProfile.Profile() as pr:
    calculateOptimizedRoute(base, start, end, "2026-11-04T00:00")

stats = pstats.Stats(pr)
stats.sort_stats("cumulative").print_stats(25)  