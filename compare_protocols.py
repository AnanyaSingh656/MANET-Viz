
import csv
from network_engine import NetworkEngine


def run_experiment(protocol, packet_count=20):
    engine = NetworkEngine(transmission_range=500)

    for _ in range(packet_count):
        engine.send_packet(0, 4, protocol=protocol)

    metrics = engine.get_metrics()
    metrics["protocol"] = protocol
    return metrics


results = [
    run_experiment("shortest_path"),
    run_experiment("aodv"),
]

columns = [
    "protocol",
    "packets_sent",
    "packets_received",
    "packets_lost",
    "pdr_percent",
    "packet_loss_percent",
    "average_hops",
    "average_delay_ms",
    "routing_overhead",
]

with open("experiment_results.csv", "w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=columns)
    writer.writeheader()
    writer.writerows(results)

print("Experiment comparison:")
for result in results:
    print(result)

print("\nSaved results to experiment_results.csv")