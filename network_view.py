
import math
import networkx as nx

from PySide6.QtWidgets import (
    QWidget, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem,
    QGraphicsLineItem, QComboBox, QPushButton, QLabel,
    QVBoxLayout, QHBoxLayout
)
from PySide6.QtGui import QBrush, QPen
from PySide6.QtCore import Qt, QTimer, QPointF


class NetworkView(QWidget):
    def __init__(self):
        super().__init__()

        self.positions = {
            0: (150, 150), 1: (350, 100), 2: (550, 180),
            3: (300, 320), 4: (600, 350),
        }
        self.transmission_range = 220
        self.graph = nx.Graph()

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setMinimumSize(800, 450)

        self.source = QComboBox()
        self.destination = QComboBox()
        for node in self.positions:
            self.source.addItem(f"N{node}", node)
            self.destination.addItem(f"N{node}", node)
        self.destination.setCurrentIndex(4)

        self.send_button = QPushButton("Send Packet")
        self.status = QLabel("Select source and destination.")

        controls = QHBoxLayout()
        controls.addWidget(QLabel("Source:"))
        controls.addWidget(self.source)
        controls.addWidget(QLabel("Destination:"))
        controls.addWidget(self.destination)
        controls.addWidget(self.send_button)

        layout = QVBoxLayout(self)
        layout.addLayout(controls)
        layout.addWidget(self.view)
        layout.addWidget(self.status)

        self.send_button.clicked.connect(self.send_packet)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.move_packet)
        self.route = []
        self.route_index = 0
        self.packet = None

        self.draw_network()

    def draw_network(self):
        self.scene.clear()
        self.graph.clear()
        self.graph.add_nodes_from(self.positions)

        for a in self.positions:
            for b in self.positions:
                if a >= b:
                    continue
                x1, y1 = self.positions[a]
                x2, y2 = self.positions[b]
                if math.hypot(x2-x1, y2-y1) <= self.transmission_range:
                    self.graph.add_edge(a, b)

        for a, b in self.graph.edges:
            x1, y1 = self.positions[a]
            x2, y2 = self.positions[b]
            self.scene.addItem(QGraphicsLineItem(x1, y1, x2, y2))

        for node, (x, y) in self.positions.items():
            circle = QGraphicsEllipseItem(x-20, y-20, 40, 40)
            circle.setBrush(QBrush(Qt.GlobalColor.cyan))
            circle.setPen(QPen(Qt.GlobalColor.darkBlue, 2))
            self.scene.addItem(circle)
            text = self.scene.addText(f"N{node}")
            text.setPos(x-12, y+22)

    def send_packet(self):
        source = self.source.currentData()
        destination = self.destination.currentData()

        if source == destination:
            self.status.setText("Choose different source and destination.")
            return

        try:
            self.route = nx.shortest_path(
                self.graph, source, destination
            )
        except nx.NetworkXNoPath:
            self.status.setText("Packet failed: no route available.")
            return

        self.route_index = 0
        x, y = self.positions[source]
        self.packet = self.scene.addEllipse(
            x-7, y-7, 14, 14,
            QPen(Qt.GlobalColor.red),
            QBrush(Qt.GlobalColor.red)
        )
        self.status.setText(
            "Packet route: " + " → ".join(f"N{n}" for n in self.route)
        )
        self.timer.start(500)

    def move_packet(self):
        if self.route_index >= len(self.route)-1:
            self.timer.stop()
            self.status.setText("Packet delivered successfully!")
            return

        self.route_index += 1
        node = self.route[self.route_index]
        x, y = self.positions[node]
        self.packet.setRect(x-7, y-7, 14, 14)