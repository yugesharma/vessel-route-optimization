import cProfile, pstats
from RouteCalculation import calculateOptimizedRoute
from route_setup import getBaseRoute
from datetime import date

start, end = (-74.2676, 36.9850), (-4.6582, 36.1734)  
base = getBaseRoute(start, end)

with cProfile.Profile() as pr:
    calculateOptimizedRoute(base, start, end, f"{date.today()}T00:00")

stats = pstats.Stats(pr)
stats.sort_stats("cumulative").print_stats(25)  