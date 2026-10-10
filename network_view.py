
import math

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QBrush, QPen, QFont
from PySide6.QtWidgets import (
    QWidget, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem,
    QComboBox, QPushButton, QLabel, QVBoxLayout, QHBoxLayout,
    QGridLayout, QGroupBox, QSlider, QTextEdit, QMessageBox, QFrame
)

from network_engine import NetworkEngine


class NodeItem(QGraphicsEllipseItem):
    """A draggable network node."""

    def __init__(self, node_id, x, y, moved_callback):
        super().__init__(-19, -19, 38, 38)

        self.node_id = node_id
        self.moved_callback = moved_callback

        self.setPos(x, y)
        self.setBrush(QBrush(Qt.GlobalColor.cyan))
        self.setPen(QPen(Qt.GlobalColor.white, 2))
        self.setFlag(
            QGraphicsEllipseItem.GraphicsItemFlag.ItemIsMovable, True
        )
        self.setFlag(
            QGraphicsEllipseItem.GraphicsItemFlag.ItemIsSelectable, True
        )
        self.setZValue(2)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)

        if self.moved_callback:
            self.moved_callback(
                self.node_id,
                self.pos().x(),
                self.pos().y()
            )


class NetworkView(QWidget):

    def __init__(self):
        super().__init__()

        # Use the existing backend engine
        self.engine = NetworkEngine()

        self.node_items = {}
        self.packet_item = None
        self.route = []
        self.route_index = 0
        self.packet_result = None

        self.setMinimumSize(1050, 680)

        self.setStyleSheet("""
            QWidget {
                background: #101827;
                color: #e6edf7;
                font-size: 12px;
            }

            
            QGroupBox {
                border: 1px solid #34445c;
                border-radius: 9px;
                margin-top: 18px;
                padding: 12px 8px 8px 8px;
                font-weight: bold;
                color: #9ec5fe;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 12px;
                top: 0px;
                padding: 0 6px;
                background-color: #101827;
            }

            QComboBox, QTextEdit {
                background: #0b1220;
                border: 1px solid #34445c;
                border-radius: 5px;
                padding: 5px;
                color: #e6edf7;
            }

            QPushButton {
                background: #147d92;
                border: 0;
                border-radius: 5px;
                padding: 8px 10px;
                font-weight: bold;
            }

            QPushButton:hover {
                background: #1b9bb2;
            }

            QSlider::groove:horizontal {
                height: 6px;
                background: #34445c;
                border-radius: 3px;
            }

            QSlider::handle:horizontal {
                background: #56d6c9;
                width: 14px;
                margin: -5px 0;
                border-radius: 7px;
            }
        """)

        # ---------------- HEADER ----------------

        title = QLabel("MANET-Viz")
        title.setFont(QFont("Arial", 22, QFont.Weight.Bold))

        subtitle = QLabel(
            "Mobile ad hoc network routing simulator"
        )
        subtitle.setStyleSheet("color: #9aaec8;")

        self.network_status = QLabel()
        self.network_status.setAlignment(
            Qt.AlignmentFlag.AlignRight |
            Qt.AlignmentFlag.AlignVCenter
        )

        header = QHBoxLayout()
        title_layout = QVBoxLayout()
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        header.addLayout(title_layout)
        header.addStretch()
        header.addWidget(self.network_status)

        # ---------------- METRICS ----------------

        self.metric_labels = {}
        metric_grid = QGridLayout()

        metric_specs = [
            ("PACKETS SENT", "packets_sent"),
            ("DELIVERED", "packets_received"),
            ("PACKETS LOST", "packets_lost"),
            ("DELIVERY RATIO", "pdr_percent"),
            ("AVERAGE HOPS", "average_hops"),
            ("AVERAGE DELAY", "average_delay_ms"),
        ]

        for index, (label_text, key) in enumerate(metric_specs):
            card = QFrame()
            card.setStyleSheet("""
                QFrame {
                    background: #1a2638;
                    border: 1px solid #34445c;
                    border-radius: 8px;
                }
            """)

            card_layout = QVBoxLayout(card)

            name = QLabel(label_text)
            name.setStyleSheet(
                "color: #9db6d4; font-size: 10px; "
                "font-weight: bold; border: 0;"
            )

            value = QLabel("0")
            value.setFont(QFont("Arial", 18, QFont.Weight.Bold))
            value.setStyleSheet("border: 0;")

            card_layout.addWidget(name)
            card_layout.addWidget(value)

            self.metric_labels[key] = value
            metric_grid.addWidget(card, index // 3, index % 3)

        # ---------------- NETWORK CANVAS ----------------

        topology_box = QGroupBox("NETWORK TOPOLOGY")
        topology_layout = QVBoxLayout(topology_box)

        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(0, 0, 820, 470)

        
        self.view = QGraphicsView(self.scene)
        self.view.setMinimumSize(0, 0)

        self.view.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.view.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.view.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        self.view.setSizePolicy(
            self.view.sizePolicy().Policy.Expanding,
            self.view.sizePolicy().Policy.Expanding
        )




        self.view.setStyleSheet("""
            QGraphicsView {
                background: #0e1726;
                border: 1px solid #34445c;
                border-radius: 6px;
            }
        """)

        topology_layout.addWidget(self.view)

        hint = QLabel(
            "Drag a node to change its position. Links update on release."
        )
        hint.setStyleSheet("color: #9aaec8;")
        topology_layout.addWidget(hint)

        # ---------------- SIMULATION CONTROLS ----------------

        controls_box = QGroupBox("SIMULATION CONTROLS")
        controls = QVBoxLayout(controls_box)

        self.source = QComboBox()
        self.destination = QComboBox()
        self.protocol = QComboBox()

        for node in self.engine.positions:
            self.source.addItem(f"N{node}", node)
            self.destination.addItem(f"N{node}", node)

        if self.destination.count() > 1:
            self.destination.setCurrentIndex(1)

        self.protocol.addItem(
            "Shortest path (minimum hops)", "shortest_path"
        )
        self.protocol.addItem(
            "Distance-based routing", "distance"
        )
        self.protocol.addItem(
            "Simplified AODV", "aodv"
        )

        controls.addWidget(QLabel("Source node"))
        controls.addWidget(self.source)

        controls.addWidget(QLabel("Destination node"))
        controls.addWidget(self.destination)

        controls.addWidget(QLabel("Routing approach"))
        controls.addWidget(self.protocol)

        self.send_button = QPushButton("Send Packet")
        self.send_button.clicked.connect(self.send_packet)
        controls.addWidget(self.send_button)

        # Transmission range
        controls.addSpacing(8)
        controls.addWidget(QLabel("Transmission range"))

        range_row = QHBoxLayout()

        self.range_slider = QSlider(Qt.Orientation.Horizontal)
        self.range_slider.setRange(80, 350)
        self.range_slider.setValue(
            int(self.engine.transmission_range)
        )

        self.range_value = QLabel(
            f"{self.engine.transmission_range} units"
        )

        self.range_slider.valueChanged.connect(self.change_range)

        range_row.addWidget(self.range_slider, 1)
        range_row.addWidget(self.range_value)

        controls.addLayout(range_row)

        # Congestion control
        controls.addWidget(QLabel("Congestion node"))

        self.congestion_node = QComboBox()
        self.congestion_node.addItem("No congestion", None)

        for node in self.engine.positions:
            self.congestion_node.addItem(f"N{node}", node)

        self.congestion_node.currentIndexChanged.connect(
            self.change_congestion
        )

        controls.addWidget(self.congestion_node)

        # Reset
        self.reset_button = QPushButton("Reset Simulation")
        self.reset_button.setStyleSheet(
            "QPushButton { background: #37465c; }"
        )
        self.reset_button.clicked.connect(self.reset_simulation)

        controls.addWidget(self.reset_button)
        controls.addStretch()

        # ---------------- EVENT LOG ----------------

        log_box = QGroupBox("EVENT LOG")
        log_layout = QVBoxLayout(log_box)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumHeight(105)

        log_layout.addWidget(self.log)

        # ---------------- MAIN LAYOUT ----------------

        main_row = QHBoxLayout()
        main_row.addWidget(topology_box, 3)
        main_row.addWidget(controls_box, 1)

        layout = QVBoxLayout(self)
        layout.addLayout(header)
        layout.addLayout(metric_grid)
        layout.addLayout(main_row, 1)
        layout.addWidget(log_box)

        # ---------------- PACKET ANIMATION ----------------

        self.timer = QTimer(self)
        self.timer.setInterval(400)
        self.timer.timeout.connect(self.animate_packet)

        self.log_event(
            "Simulation ready. Select endpoints and send a packet."
        )

        self.redraw_network()
        self.refresh_metrics()

    # =====================================================
    # NETWORK VISUALIZATION
    # =====================================================

    def log_event(self, message):
        self.log.append(message)

    
    def resizeEvent(self, event):
        super().resizeEvent(event)

        if hasattr(self, "view") and hasattr(self, "scene"):
            self.view.fitInView(
                self.scene.sceneRect(),
                Qt.AspectRatioMode.KeepAspectRatio
            )


    def redraw_network(self):
        self.scene.clear()
        self.node_items.clear()
        self.packet_item = None

        snapshot = self.engine.get_network_snapshot()

        # Draw wireless links
        for link in snapshot["links"]:
            source = link["source"]
            destination = link["target"]

            x1, y1 = self.engine.positions[source]
            x2, y2 = self.engine.positions[destination]

            self.scene.addLine(
                x1, y1, x2, y2,
                QPen(Qt.GlobalColor.gray, 2)
            )

        # Draw nodes
        for node, (x, y) in self.engine.positions.items():
            item = NodeItem(
                node, x, y, self.node_moved
            )

            if node in self.engine.congested_nodes:
                item.setBrush(QBrush(Qt.GlobalColor.red))

            self.scene.addItem(item)
            self.node_items[node] = item

            label = self.scene.addText(f"N{node}")
            label.setDefaultTextColor(Qt.GlobalColor.white)
            label.setPos(x - 12, y + 22)
            label.setZValue(3)

        status = snapshot["status"]

        if status["connected"]:
            connection_text = "Connected"
        else:
            connection_text = (
                f"{len(status['components'])} components"
            )

        self.network_status.setText(
            f"●  {status['node_count']} nodes  ·  "
            f"{status['link_count']} links  ·  "
            f"{connection_text}"
        )

        self.network_status.setStyleSheet(
            "color: #56d6c9; padding: 7px; "
            "background: #153b3a; border-radius: 7px;"
        )

    # =====================================================
    # MOBILITY
    # =====================================================

    def node_moved(self, node, x, y):
        self.engine.move_node(node, x, y)

        self.log_event(
            f"Moved N{node}; wireless links recalculated."
        )

        self.redraw_network()

    # =====================================================
    # TRANSMISSION RANGE
    # =====================================================

    def change_range(self, value):
        self.range_value.setText(f"{value} units")

        self.engine.set_transmission_range(value)

        self.redraw_network()

    # =====================================================
    # CONGESTION
    # =====================================================

    def change_congestion(self, _index):
        selected = self.congestion_node.currentData()

        self.engine.congested_nodes.clear()

        if selected is not None:
            self.engine.set_congestion(selected, True)
            self.log_event(f"Congestion enabled at N{selected}.")
        else:
            self.log_event("Congestion cleared.")

        self.redraw_network()

    # =====================================================
    # SEND PACKET THROUGH BACKEND
    # =====================================================

    def send_packet(self):
        if self.timer.isActive():
            self.timer.stop()

        source = self.source.currentData()
        destination = self.destination.currentData()

        if source == destination:
            QMessageBox.warning(
                self,
                "Invalid endpoints",
                "Choose different source and destination nodes."
            )
            return

        result = self.engine.send_packet(
            source,
            destination,
            protocol=self.protocol.currentData()
        )

        self.packet_result = result
        self.route = result.get("route", [])
        self.route_index = 0

        self.refresh_metrics()

        if not result["delivered"]:
            self.log_event(
                f"Packet N{source} → N{destination} failed: "
                f"{result['reason']}."
            )

            if self.route:
                self.show_route(self.route, failed=True)

            return

        route_text = " → ".join(
            f"N{node}" for node in self.route
        )

        self.log_event(
            f"Packet N{source} → N{destination}: {route_text}"
        )

        self.log_event(
            f"Delivered in {result['hops']} hops; "
            f"simulated delay {result['delay_ms']} ms."
        )

        self.show_route(self.route, failed=False)

    # =====================================================
    # PACKET ANIMATION
    # =====================================================

    def show_route(self, route, failed=False):
        self.redraw_network()

        if not route:
            return

        self.route = route
        self.route_index = 0

        x, y = self.engine.positions[route[0]]

        color = (
            Qt.GlobalColor.red
            if failed
            else Qt.GlobalColor.yellow
        )

        self.packet_item = self.scene.addEllipse(
            x - 7, y - 7, 14, 14,
            QPen(color),
            QBrush(color)
        )

        self.packet_item.setZValue(5)

        if len(route) > 1:
            self.timer.start()

    def animate_packet(self):
        if (
            self.packet_item is None
            or self.route_index >= len(self.route) - 1
        ):
            self.timer.stop()

            if (
                self.packet_result
                and self.packet_result["delivered"]
            ):
                self.log_event(
                    "Packet animation complete: delivered successfully."
                )

            return

        self.route_index += 1
        node = self.route[self.route_index]

        x, y = self.engine.positions[node]

        self.packet_item.setRect(
            x - 7, y - 7, 14, 14
        )

    # =====================================================
    # METRICS
    # =====================================================

    def refresh_metrics(self):
        metrics = self.engine.get_metrics()

        values = {
            "packets_sent": str(metrics["packets_sent"]),
            "packets_received": str(metrics["packets_received"]),
            "packets_lost": str(metrics["packets_lost"]),
            "pdr_percent": f"{metrics['pdr_percent']:.1f}%",
            "average_hops": f"{metrics['average_hops']:.1f}",
            "average_delay_ms": (
                f"{metrics['average_delay_ms']:.1f} ms"
            ),
        }

        for key, value in values.items():
            self.metric_labels[key].setText(value)

    # =====================================================
    # RESET
    # =====================================================

    def reset_simulation(self):
        self.timer.stop()

        self.engine.reset()

        self.range_slider.blockSignals(True)
        self.range_slider.setValue(
            int(self.engine.transmission_range)
        )
        self.range_slider.blockSignals(False)

        self.range_value.setText(
            f"{self.engine.transmission_range} units"
        )

        self.congestion_node.blockSignals(True)
        self.congestion_node.setCurrentIndex(0)
        self.congestion_node.blockSignals(False)

        self.route = []
        self.packet_result = None

        self.redraw_network()
        self.refresh_metrics()

        self.log_event(
            "Simulation reset. Positions and packet statistics restored."
        )