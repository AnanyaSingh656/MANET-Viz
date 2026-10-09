
from network_engine import NetworkEngine

engine = NetworkEngine(transmission_range=220)

print("=== NORMAL TRANSMISSION ===")
print(engine.send_packet(0, 4))

print("\n=== CONGESTION AT NODE 1 ===")
engine.set_congestion(1, True)
print(engine.send_packet(0, 4))

print("\n=== CLEAR CONGESTION ===")
engine.set_congestion(1, False)
print(engine.send_packet(0, 4))

print("\n=== FINAL METRICS ===")
print(engine.get_metrics())