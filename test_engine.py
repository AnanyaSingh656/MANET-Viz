
from network_engine import NetworkEngine

engine = NetworkEngine()

print("Wireless links:", list(engine.graph.edges()))

result = engine.send_packet(0, 4)
print("\nPacket result:", result)

print("\nNetwork metrics:")
for name, value in engine.get_metrics().items():
    print(f"{name}: {value}")