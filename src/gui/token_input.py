

# Token Input GUI
from src.constants import SelfbotData
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox
)

class TokenInput(QWidget):
    def __init__(self, data: SelfbotData):
        super().__init__()
        self.init_ui()
        self._data_ref = data

    def init_ui(self):
        self.setWindowTitle("Enter a Discord Token")
        self.setGeometry(100, 100, 300, 150)
        layout = QVBoxLayout()
        self.label = QLabel("Enter your token: ")
        self.token_input = QLineEdit(self)
        self.token_input.setEchoMode(QLineEdit.Password)
        self.save_button = QPushButton("Enter", self)
        self.save_button.clicked.connect(self.save_token)
        layout.addWidget(self.label)
        layout.addWidget(self.token_input)
        layout.addWidget(self.save_button)
        self.setLayout(layout)

    def save_token(self):
        token = self.token_input.text()
        if not token:
            QMessageBox.warning(self, "Error", "You must enter a token.")
            return
        self._data_ref.token = token
        QMessageBox.information(self, "Success", "Token has been saved successfully.")