
from network_engine import NetworkEngine

engine = NetworkEngine(transmission_range=220)

print("=== BEFORE MOVEMENT ===")
print("Network:", engine.get_network_status())
print("Packet:", engine.send_packet(0, 4))

print("\n=== MOVE NODE 4 FAR AWAY ===")
engine.move_node(4, 1000, 700)

print("Network:", engine.get_network_status())
print("Packet:", engine.send_packet(0, 4))

print("\n=== INCREASE TRANSMISSION RANGE ===")
engine.set_transmission_range(1000)

print("Network:", engine.get_network_status())
print("Packet:", engine.send_packet(0, 4))

print("\n=== FINAL METRICS ===")
print(engine.get_metrics())