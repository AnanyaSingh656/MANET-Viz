
from network_engine import NetworkEngine

engine = NetworkEngine()
snapshot = engine.get_network_snapshot()

print("Node positions:", snapshot["positions"])
print("\nLinks:", snapshot["links"])
print("\nNetwork status:", snapshot["status"])
print("\nMetrics:", snapshot["metrics"])
print("\nCongested nodes:", snapshot["congested_nodes"])