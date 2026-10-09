
# MANET-Viz Backend Integration Guide

## Import and initialize

from network_engine import NetworkEngine

engine = NetworkEngine()

## Get network information

snapshot = engine.get_network_snapshot()

positions = snapshot["positions"]
links = snapshot["links"]
status = snapshot["status"]
metrics = snapshot["metrics"]

## Send a packet

result = engine.send_packet(
    source=0,
    destination=4,
    protocol="shortest_path"
)

# Supported protocols:
# "shortest_path", "distance", "aodv"

# Useful result fields:
# result["delivered"]
# result["route"]
# result["hops"]
# result["delay_ms"]
# result["reason"]

## Move a node

engine.move_node(4, 700, 400)

## Change transmission range

engine.set_transmission_range(300)

## Set or clear congestion

engine.set_congestion(1, True)
engine.set_congestion(1, False)

## Get performance metrics

metrics = engine.get_metrics()

## Reset the network

engine.reset()