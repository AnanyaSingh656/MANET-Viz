
from network_engine import NetworkEngine

for protocol in ["shortest_path", "distance", "aodv"]:
    engine = NetworkEngine()
    result = engine.send_packet(0, 4, protocol=protocol)

    print(f"\nProtocol: {protocol}")
    print("Route:", result["route"])
    print("Delivered:", result["delivered"])
    print("Hops:", result["hops"])
    print("Metrics:", engine.get_metrics())