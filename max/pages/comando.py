from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

class Comando(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel("Comando")
        label.setStyleSheet("font-size: 18px; color: white;")
        layout.addWidget(label)
        self.setLayout(layout)