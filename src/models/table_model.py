from typing import Any, Optional
from PySide6.QtCore import Qt, QAbstractTableModel
import pandas as pd

class SmartTableModel(QAbstractTableModel):
    def __init__(self, df: Optional[pd.DataFrame] = None, num_mode: str = "excel", num_col_index: int = 0):
        super().__init__()
        self._df = df if df is not None else pd.DataFrame()
        self._filtered_df = self._df.copy()
        self.num_mode = num_mode
        self.num_col_index = num_col_index

    def rowCount(self, parent=None) -> int:
        return len(self._filtered_df)

    def columnCount(self, parent=None) -> int:
        return len(self._filtered_df.columns)

    def data(self, index, role=Qt.DisplayRole) -> Any:
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            if index.column() == self.num_col_index and self.num_mode == "order":
                return str(index.row() + 1)
            return str(self._filtered_df.iloc[index.row(), index.column()])
        return None

    def sort(self, column: int, order: Qt.SortOrder) -> None:
        self.beginResetModel()
        ascending = order == Qt.AscendingOrder
        col_name = self._df.columns[column]
        if column == self.num_col_index and col_name.lower().strip() in ["excel #", "№"]:
            try:
                self._df[col_name] = pd.to_numeric(self._df[col_name], errors="coerce")
            except Exception:
                pass
            self._df.sort_values(by=col_name, ascending=ascending, inplace=True, kind="mergesort")
            self._df[col_name] = self._df[col_name].astype(str)
        else:
            self._df.sort_values(by=col_name, ascending=ascending, inplace=True, kind="mergesort")
        self._filtered_df = self._df.copy()
        self.endResetModel()

    def headerData(self, section: int, orientation: Qt.Orientation, role=Qt.DisplayRole) -> Any:
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if section == self.num_col_index:
                    if self.num_mode == "order":
                        return "№ (порядок)"
                    elif "Excel #" in self._df.columns:
                        return "Excel #"
                    elif "№" in self._df.columns:
                        return "№"
                    else:
                        return str(self._df.columns[section])
                return str(self._df.columns[section])
            return str(section + 1)
        return None

    def setData(self, index, value: Any, role=Qt.EditRole) -> bool:
        if role == Qt.EditRole:
            self._df.iloc[index.row(), index.column()] = value
            self.dataChanged.emit(index, index)
            return True
        return False

    def flags(self, index) -> Qt.ItemFlags:
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def get_dataframe(self) -> pd.DataFrame:
        return self._df.copy()

    def set_dataframe(self, df: pd.DataFrame) -> None:
        self.beginResetModel()
        self._df = df.copy()
        self._filtered_df = df.copy()
        if "Excel #" in df.columns:
            self.num_col_index = df.columns.get_loc("Excel #")
        elif "№" in df.columns:
            self.num_col_index = df.columns.get_loc("№")
        else:
            self.num_col_index = 0
        self.endResetModel()

    def get_column_data(self, column_index: int) -> pd.Series:
        return self._df.iloc[:, column_index]