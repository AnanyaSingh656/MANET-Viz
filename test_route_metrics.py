
from network_engine import NetworkEngine

engine = NetworkEngine()

print("Fewest-hop route:")
print(engine.find_route(0, 4))

print("\nShortest-distance route:")
print(engine.find_route_by_distance(0, 4))