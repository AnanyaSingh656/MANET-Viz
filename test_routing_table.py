
from network_engine import NetworkEngine

engine = NetworkEngine()

for node, entry in engine.get_routing_table(0).items():
    print(f"Destination {node}: {entry}")