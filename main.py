
import sys

from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import Qt

from network_view import NetworkView

app = QApplication(sys.argv)

window = QMainWindow()
window.setWindowTitle("MANET-Viz | Packet Routing")

# Give the dashboard enough space
window.resize(1400, 900)
window.setMinimumSize(1100, 750)

window.setCentralWidget(NetworkView())
window.show()

sys.exit(app.exec())