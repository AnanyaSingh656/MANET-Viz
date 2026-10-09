
from network_engine import NetworkEngine

engine = NetworkEngine()

print("=== SHORTEST-PATH ROUTING ===")
result1 = engine.send_packet(0, 4, protocol="shortest_path")
print(result1)

print("\n=== AODV-STYLE ROUTING ===")
result2 = engine.send_packet(0, 4, protocol="aodv")
print(result2)

print("\n=== COMPARISON ===")
print(engine.get_metrics())