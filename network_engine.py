
import math
import networkx as nx


class NetworkEngine:
    def __init__(self, transmission_range=220):
        self.transmission_range = transmission_range

        # Node IDs and their positions on the simulation canvas
        self.positions = {
            0: (150, 150),
            1: (350, 100),
            2: (550, 180),
            3: (300, 320),
            4: (600, 350),
        }

        self.graph = nx.Graph()
        self.queue_capacity = 3
        self.congested_nodes = set()

        self.packet_stats = {
            "sent": 0,
            "received": 0,
            "lost": 0,
            "total_hops": 0,
            "total_delay": 0.0,
            "routing_overhead": 0,
        }

        self.update_topology()

    def update_topology(self):
        """Create wireless links between nodes within range."""
        self.graph.clear()
        self.graph.add_nodes_from(self.positions.keys())

        nodes = list(self.positions.keys())

        for i, a in enumerate(nodes):
            for b in nodes[i + 1:]:
                x1, y1 = self.positions[a]
                x2, y2 = self.positions[b]

                distance = math.hypot(x2 - x1, y2 - y1)

                if distance <= self.transmission_range:
                    self.graph.add_edge(
                        a, b, distance=distance
                    )

    def find_route(self, source, destination):
        """Find a minimum-hop route through connected nodes."""
        if source not in self.graph or destination not in self.graph:
            return None

        try:
            return nx.shortest_path(
                self.graph, source, destination
            )
        except nx.NetworkXNoPath:
            return None

    
    def find_route_by_distance(self, source, destination):
        """Find the route with the lowest total link distance."""
        if source not in self.graph or destination not in self.graph:
            return None

        try:
            return nx.shortest_path(
                self.graph,
                source,
                destination,
                weight="distance",
            )
        except nx.NetworkXNoPath:
            return None        

    
    def get_routing_table(self, source):
        """Build a routing table using shortest paths from a node."""
        if source not in self.graph:
            raise ValueError("Unknown source node")

        table = {}

        for destination in self.graph.nodes:
            if destination == source:
                continue

            route = self.find_route(source, destination)

            if route is None:
                table[destination] = {
                    "next_hop": None,
                    "hops": None,
                }
            else:
                table[destination] = {
                    "next_hop": route[1],
                    "hops": len(route) - 1,
                }

        return table        

    
    def find_route_aodv(self, source, destination):
        """Simplified on-demand route discovery."""
        if source not in self.graph or destination not in self.graph:
            return None

        # Simulate a Route Request (RREQ) reaching
        # every node in the source's connected component.
        reachable = nx.node_connected_component(
            self.graph, source
        )
        self.packet_stats["routing_overhead"] += len(reachable)

        if destination not in reachable:
            return None

        # Simulate a Route Reply (RREP) travelling back.
        route = nx.shortest_path(
            self.graph, source, destination
        )
        self.packet_stats["routing_overhead"] += len(route) - 1

        return route        

    def send_packet(self, source, destination, ttl=10, protocol="shortest_path"):
        """Simulate sending one packet through the network."""
        self.packet_stats["sent"] += 1

        if source == destination:
            self.packet_stats["lost"] += 1
            return {
                "delivered": False,
                "reason": "Source and destination must differ",
                "route": [],
                "hops": 0,
                "delay_ms": 0.0,
            }

        
        if protocol == "aodv":
            route = self.find_route_aodv(source, destination)
        elif protocol == "shortest_path":
            route = self.find_route(source, destination)
        elif protocol == "distance":
            route = self.find_route_by_distance(source, destination)
        else:
            raise ValueError("Unknown routing protocol")

        if route is None:
            self.packet_stats["lost"] += 1
            return {
                "delivered": False,
                "reason": "No route available",
                "route": [],
                "hops": 0,
                "delay_ms": 0.0,
            }

        hops = len(route) - 1
        
        # Simulate packet dropping at congested intermediate nodes
        congested = [
            node for node in route[1:-1]
            if node in self.congested_nodes
        ]

        if congested:
            self.packet_stats["lost"] += 1
            return {
                "delivered": False,
                "reason": f"Congestion at node {congested[0]}",
                "route": route,
                "hops": len(route) - 1,
                "delay_ms": 0.0,
            }


        if hops > ttl:
            self.packet_stats["lost"] += 1
            return {
                "delivered": False,
                "reason": "Packet TTL exceeded",
                "route": route,
                "hops": hops,
                "delay_ms": 0.0,
            }

        # Simplified delay model: 10 ms processing/transmission
        # delay per hop, plus propagation delay based on distance.
        delay_ms = 0.0

        for a, b in zip(route, route[1:]):
            distance = self.graph[a][b]["distance"]
            delay_ms += 10.0 + distance / 200.0

        self.packet_stats["received"] += 1
        self.packet_stats["total_hops"] += hops
        self.packet_stats["total_delay"] += delay_ms

        return {
            "delivered": True,
            "reason": "Packet delivered",
            "route": route,
            "hops": hops,
            "delay_ms": round(delay_ms, 2),
        }

    def get_metrics(self):
        """Return network performance measurements."""
        stats = self.packet_stats
        sent = stats["sent"]
        received = stats["received"]

        return {
            "packets_sent": sent,
            "packets_received": received,
            "packets_lost": stats["lost"],
            "pdr_percent": round(
                received / sent * 100, 2
            ) if sent else 0.0,
            "packet_loss_percent": round(
                stats["lost"] / sent * 100, 2
            ) if sent else 0.0,
            "average_hops": round(
                stats["total_hops"] / received, 2
            ) if received else 0.0,
            "average_delay_ms": round(
                stats["total_delay"] / received, 2
            ) if received else 0.0,
            "routing_overhead": stats["routing_overhead"],
        }

    
    def move_node(self, node, x, y):
        """Move a node and rebuild wireless links."""
        if node not in self.positions:
            return False

        self.positions[node] = (x, y)
        self.update_topology()
        return True

    def set_transmission_range(self, new_range):
        """Change wireless transmission range."""
        if new_range <= 0:
            raise ValueError("Transmission range must be positive")

        self.transmission_range = new_range
        self.update_topology()

    def get_network_status(self):
        """Report network connectivity."""
        components = list(nx.connected_components(self.graph))

        return {
            "node_count": self.graph.number_of_nodes(),
            "link_count": self.graph.number_of_edges(),
            "connected": nx.is_connected(self.graph),
            "components": [sorted(c) for c in components],
        }   

    
    def set_congestion(self, node, congested=True):
        """Simulate a node with a full packet queue."""
        if node not in self.positions:
            raise ValueError("Unknown node")

        if congested:
            self.congested_nodes.add(node)
        else:
            self.congested_nodes.discard(node)     


     
    def reset(self):
        """Restore initial positions and clear experiment statistics."""
        self.positions = {
            0: (150, 150),
            1: (350, 100),
            2: (550, 180),
            3: (300, 320),
            4: (600, 350),
        }

        self.congested_nodes.clear()

        self.packet_stats = {
            "sent": 0,
            "received": 0,
            "lost": 0,
            "total_hops": 0,
            "total_delay": 0.0,
            "routing_overhead": 0,
        }

        self.update_topology()       

    
    def get_network_snapshot(self):
        """Return network data for the GUI to visualize."""
        links = []

        for a, b, data in self.graph.edges(data=True):
            links.append({
                "source": a,
                "target": b,
                "distance": round(data["distance"], 2),
            })

        return {
            "positions": self.positions.copy(),
            "links": links,
            "status": self.get_network_status(),
            "metrics": self.get_metrics(),
            "congested_nodes": sorted(self.congested_nodes),
        }