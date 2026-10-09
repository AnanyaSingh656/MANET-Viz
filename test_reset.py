
from network_engine import NetworkEngine

engine = NetworkEngine()

engine.send_packet(0, 4)
engine.move_node(4, 1000, 700)

print("Before reset:", engine.get_metrics())

engine.reset()

print("After reset:", engine.get_metrics())
print("Network:", engine.get_network_status())
print("Packet:", engine.send_packet(0, 4))