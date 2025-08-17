from typing import List
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QListWidget,
    QDialogButtonBox,
    QListWidgetItem,
)
from PySide6.QtCore import Qt


class SubtitleDialog(QDialog):
    """
    A dialog for selecting available subtitle languages.
    """

    def __init__(
        self, available: List[str], selected: List[str], parent=None
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Select Subtitles")
        self.setMinimumWidth(300)

        self._layout = QVBoxLayout(self)
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.MultiSelection)
        self._layout.addWidget(self.list_widget)

        for lang in available:
            item = QListWidgetItem(lang)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            is_checked = lang in selected
            item.setCheckState(Qt.Checked if is_checked else Qt.Unchecked)
            self.list_widget.addItem(item)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self._layout.addWidget(self.button_box)

        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

    def selected(self) -> List[str]:
        """Return a list of the checked language codes."""
        langs = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.checkState() == Qt.Checked:
                langs.append(item.text())
        return langs

