
from network_engine import NetworkEngine


def run_experiment(protocol, packet_count=20):
    engine = NetworkEngine(transmission_range=500)

    for _ in range(packet_count):
        engine.send_packet(0, 4, protocol=protocol)

    metrics = engine.get_metrics()

    print(f"\nProtocol: {protocol}")
    print(f"Packets sent: {metrics['packets_sent']}")
    print(f"Packets received: {metrics['packets_received']}")
    print(f"Packets lost: {metrics['packets_lost']}")
    print(f"Packet delivery ratio: {metrics['pdr_percent']}%")
    print(f"Average hops: {metrics['average_hops']}")
    print(f"Average delay: {metrics['average_delay_ms']} ms")
    print(f"Routing overhead: {metrics['routing_overhead']}")


run_experiment("shortest_path")
run_experiment("aodv")