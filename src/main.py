import sys
import os

# Добавляем путь к директории src в системные пути
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from views.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    try:
        with open("resources/styles/main.qss", "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except Exception as e:
        print(f"Не удалось загрузить стили: {e}")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()