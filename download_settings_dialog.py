from typing import Dict, List

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QSpinBox, QLineEdit, QHBoxLayout, QPushButton, QListWidget, QListWidgetItem, QAbstractItemView
)


SPONSORBLOCK_CATEGORIES = [
    "sponsor",
    "selfpromo",
    "interaction",
    "intro",
    "outro",
    "preview",
    "music_offtopic",
]


class DownloadSettingsDialog(QDialog):
    def __init__(self, current: Dict[str, str] | None = None, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Download Settings")
        layout = QVBoxLayout(self)

        form = QFormLayout()
        self.speed_limit = QLineEdit()
        self.concurrent = QSpinBox()
        self.concurrent.setRange(1, 16)
        self.cookies = QLineEdit()
        self.user_agent = QLineEdit()
        form.addRow("Speed limit (e.g. 5M)", self.speed_limit)
        form.addRow("Concurrent fragments", self.concurrent)
        form.addRow("Cookies file", self.cookies)
        form.addRow("User agent", self.user_agent)
        layout.addLayout(form)

        self.sb_list = QListWidget()
        self.sb_list.setSelectionMode(QAbstractItemView.MultiSelection)
        for cat in SPONSORBLOCK_CATEGORIES:
            item = QListWidgetItem(cat)
            self.sb_list.addItem(item)
        layout.addWidget(self.sb_list)

        if current:
            self.speed_limit.setText(current.get("speed_limit", ""))
            try:
                self.concurrent.setValue(int(current.get("concurrent", 4)))
            except Exception:
                pass
            self.cookies.setText(current.get("cookies", ""))
            self.user_agent.setText(current.get("user_agent", ""))
            selected = set(current.get("sb_categories", []))
            for i in range(self.sb_list.count()):
                it = self.sb_list.item(i)
                if it.text() in selected:
                    it.setSelected(True)

        buttons = QHBoxLayout()
        cancel = QPushButton("Cancel")
        ok = QPushButton("Save")
        buttons.addStretch(1)
        buttons.addWidget(cancel)
        buttons.addWidget(ok)
        layout.addLayout(buttons)

        cancel.clicked.connect(self.reject)
        ok.clicked.connect(self.accept)

    def values(self) -> Dict[str, str | List[str]]:
        cats: List[str] = [it.text() for it in self.sb_list.selectedItems()]
        return {
            "speed_limit": self.speed_limit.text().strip(),
            "concurrent": str(self.concurrent.value()),
            "cookies": self.cookies.text().strip(),
            "user_agent": self.user_agent.text().strip(),
            "sb_categories": cats,
        }


