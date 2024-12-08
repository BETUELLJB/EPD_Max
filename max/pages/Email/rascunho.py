from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

class EmailRascunho(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel("Email Rascunho")
        label.setStyleSheet("font-size: 18px; color: white;")
        layout.addWidget(label)
        self.setLayout(layout)