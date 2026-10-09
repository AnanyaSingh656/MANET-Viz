from network_engine import NetworkEngine

engine = NetworkEngine(transmission_range=500)

# Force a route through node 2 by marking it congested
engine.set_congestion(2)

result = engine.send_packet(0, 4)
print("Congested packet:", result)

# Clear congestion and try again
engine.set_congestion(2, congested=False)

result = engine.send_packet(0, 4)
print("Packet after congestion clears:", result)

print("\nMetrics:", engine.get_metrics())