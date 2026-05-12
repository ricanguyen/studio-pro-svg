import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QFrame, QLabel
from PyQt6.QtCore import Qt

class SVGPaintApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Studio Pro - SVG Paint")
        self.resize(1100, 700)

        # 1. Widget tổng và Layout ngang chính
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0) # Sát viền
        main_layout.setSpacing(0)

        # 2. Cột trái: Toolbar (Thanh công cụ)
        self.toolbar = QFrame()
        self.toolbar.setFixedWidth(70)
        self.toolbar.setStyleSheet("background-color: #2D2D2D; border-right: 1px solid #3F3F3F;")
        main_layout.addWidget(self.toolbar)

        # 3. Vùng giữa: Canvas (Nơi vẽ hình)
        self.canvas_area = QFrame()
        self.canvas_area.setStyleSheet("background-color: #1E1E1E;")
        canvas_label = QLabel("CANVAS AREA", self.canvas_area)
        canvas_label.setStyleSheet("color: #555555; font-weight: bold;")
        main_layout.addWidget(self.canvas_area, stretch=1) # Chiếm toàn bộ chỗ trống còn lại

        # 4. Cột phải: Properties (Chỉnh thông số)
        self.properties_panel = QFrame()
        self.properties_panel.setFixedWidth(240)
        self.properties_panel.setStyleSheet("background-color: #2D2D2D; border-left: 1px solid #3F3F3F;")
        main_layout.addWidget(self.properties_panel)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = SVGPaintApp()
    demo.show()
    sys.exit(app.exec())