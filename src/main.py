import sys
import os

src_path = os.path.abspath(os.path.dirname(__file__))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from ui.Main.main_window import MainWindow
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QFile, QTextStream
from PySide6.QtGui import QFont, QFontDatabase

def load_stylesheet():
    file = QFile(":/style/styles/main.qss")
    if not file.exists():
        print("QSS файл не найден: :/style/styles/main.qss")
    if file.open(QFile.ReadOnly | QFile.Text):
        return QTextStream(file).readAll()
    return ""

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Устанавливаем по умолчанию шрифт Segoe UI или Arial
    # Проверяем доступные шрифты в системе
    available_fonts = QFontDatabase.families()
    
    if "Segoe UI" in available_fonts:
        font = QFont("Segoe UI", 10)
    elif "Arial" in available_fonts:
        font = QFont("Arial", 10)
    else:
        # Используем системный шрифт по умолчанию
        font = QFont()
        font.setPointSize(10)
    
    app.setFont(font)
    
    app.setStyleSheet(load_stylesheet())

    window = MainWindow()
    window.show()

    sys.exit(app.exec())