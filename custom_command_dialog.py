from typing import Dict

from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QHBoxLayout, QPushButton


class CustomCommandDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Custom yt-dlp Options")
        layout = QVBoxLayout(self)

        form = QFormLayout()
        self.limit_rate = QLineEdit()
        self.proxy = QLineEdit()
        self.cookies = QLineEdit()
        self.user_agent = QLineEdit()
        form.addRow("--limit-rate (e.g. 5M)", self.limit_rate)
        form.addRow("--proxy", self.proxy)
        form.addRow("--cookies", self.cookies)
        form.addRow("--user-agent", self.user_agent)
        layout.addLayout(form)

        buttons = QHBoxLayout()
        cancel = QPushButton("Cancel")
        ok = QPushButton("Apply")
        buttons.addStretch(1)
        buttons.addWidget(cancel)
        buttons.addWidget(ok)
        layout.addLayout(buttons)

        cancel.clicked.connect(self.reject)
        ok.clicked.connect(self.accept)

    def values(self) -> Dict[str, str]:
        return {
            "limit_rate": self.limit_rate.text().strip(),
            "proxy": self.proxy.text().strip(),
            "cookies": self.cookies.text().strip(),
            "user_agent": self.user_agent.text().strip(),
        }




