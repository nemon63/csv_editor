from PyQt5.QtCore import Qt, QSortFilterProxyModel, QRegExp, QModelIndex
from PyQt5.QtGui import QColor
import re

class MySortFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.search_pattern = ""
        self.highlight_enabled = True
        self.invert_filter = False
        self._filter_words = None
        self._use_and = True
        # Режим сортировки: "default", "lexicographic", "alphabetical", "length"
        self.sort_mode = "default"

    def set_extended_filter(self, words, use_and):
        self._filter_words = words
        self._use_and = use_and
        self.invalidateFilter()

    def set_highlight_enabled(self, enabled: bool):
        self.highlight_enabled = enabled
        self.invalidate()

    def set_invert_filter(self, enabled: bool):
        self.invert_filter = enabled
        self.invalidateFilter()

    def setFilterRegExp(self, regExp):
        super().setFilterRegExp(regExp)
        self.search_pattern = regExp.pattern()
        self.invalidateFilter()

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.BackgroundRole and self.highlight_enabled and self.search_pattern:
            source_index = self.mapToSource(index)
            text = self.sourceModel().data(source_index, Qt.DisplayRole)
            highlight_color = QColor("#FFC107")
            if text and re.search(self.search_pattern, text, re.IGNORECASE):
                return highlight_color.lighter(140)
        return super().data(index, role)

    def filterAcceptsRow(self, sourceRow: int, sourceParent: QModelIndex) -> bool:
        if self._filter_words is not None and len(self._filter_words) > 0:
            return self._extended_filterAcceptsRow(sourceRow, sourceParent)
        else:
            if self.filterRegExp().isEmpty():
                return True
            model = self.sourceModel()
            found = False
            for col in [0, 1]:
                index = model.index(sourceRow, col, sourceParent)
                data = model.data(index, Qt.DisplayRole)
                if data and self.filterRegExp().indexIn(str(data)) != -1:
                    found = True
                    break
            return (not found) if self.invert_filter else found

    def _extended_filterAcceptsRow(self, sourceRow, sourceParent):
        model = self.sourceModel()
        row_text = []
        for c in range(model.columnCount()):
            idx = model.index(sourceRow, c, sourceParent)
            val = model.data(idx, Qt.DisplayRole)
            if val:
                row_text.append(str(val))
        row_joined = " ".join(row_text).lower()
        if self._use_and:
            return all(w.lower() in row_joined for w in self._filter_words)
        else:
            return any(w.lower() in row_joined for w in self._filter_words)

    def lessThan(self, left, right):
        left_data = self.sourceModel().data(left, Qt.DisplayRole)
        right_data = self.sourceModel().data(right, Qt.DisplayRole)
        # Сортировка по длине строки
        if self.sort_mode == "length":
            return len(str(left_data)) < len(str(right_data))
        # Сортировка по алфавиту (без учёта регистра)
        elif self.sort_mode == "alphabetical":
            return str(left_data).lower() < str(right_data).lower()
        # Лексикографическая сортировка (с учётом регистра)
        elif self.sort_mode == "lexicographic":
            return str(left_data) < str(right_data)
        else:
            try:
                left_val = float(left_data)
                right_val = float(right_data)
                return left_val < right_val
            except (ValueError, TypeError):
                return str(left_data) < str(right_data)
