import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, 
                             QHBoxLayout, QVBoxLayout, QFrame, QPushButton, QLabel)
from PyQt6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Studio Pro - SVG Paint")
        self.resize(1200, 800)

        # 1. Tạo Widget chính và Layout nằm ngang (HBox)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 2. Cột trái: TOOLBAR
        self.toolbar = QFrame()
        self.toolbar.setFixedWidth(60)
        self.toolbar.setStyleSheet("background-color: #252526; border-right: 1px solid #3c3c3c;")
        main_layout.addWidget(self.toolbar)

        # 3. Vùng giữa: CANVAS
        self.canvas_area = QFrame()
        self.canvas_area.setStyleSheet("background-color: #1e1e1e;")
        canvas_layout = QVBoxLayout(self.canvas_area)
        canvas_layout.addWidget(QLabel("Canvas Area", alignment=Qt.AlignmentFlag.AlignCenter))
        main_layout.addWidget(self.canvas_area, stretch=1) # stretch=1 để vùng này tự giãn nở

        # 4. Cột phải: PROPERTIES
        self.properties_panel = QFrame()
        self.properties_panel.setFixedWidth(240)
        self.properties_panel.setStyleSheet("background-color: #252526; border-left: 1px solid #3c3c3c;")
        main_layout.addWidget(self.properties_panel)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())