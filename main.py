import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from network_view import NetworkView

app = QApplication(sys.argv)
window = QMainWindow()
window.setWindowTitle("MANET-Viz | Packet Routing")
window.resize(1000, 650)
window.setCentralWidget(NetworkView())
window.show()
sys.exit(app.exec())