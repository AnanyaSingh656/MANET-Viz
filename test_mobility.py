
from network_engine import NetworkEngine

engine = NetworkEngine()

print("BEFORE MOVEMENT")
print(engine.get_network_status())

# Move node 4 far away from the other nodes
engine.move_node(4, 950, 450)

print("\nAFTER MOVEMENT")
print(engine.get_network_status())

# Try sending a packet after the topology changes
result = engine.send_packet(0, 4)
print("\nPacket result:", result)

# Increase range and rebuild the topology
engine.set_transmission_range(500)

print("\nAFTER INCREASING RANGE")
print(engine.get_network_status())
print("Packet result:", engine.send_packet(0, 4))