import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, 
                             QVBoxLayout, QFrame, QPushButton, QGraphicsView, QGraphicsScene, QGraphicsRectItem)
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPen, QColor, QBrush

# 1. Lớp quản lý vùng vẽ (Canvas)
class PaintCanvas(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene(0, 0, 800, 600)
        self.setScene(self.scene)
        self.setBackgroundBrush(QBrush(QColor("#1E1E1E"))) # Màu nền canvas
        
        self.current_item = None
        self.start_point = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_point = self.mapToScene(event.pos())
            # Tạo một hình chữ nhật tạm thời
            self.current_item = QGraphicsRectItem()
            self.current_item.setPen(QPen(QColor("#4BBEFF"), 2)) # Màu viền xanh như mockup
            self.scene.addItem(self.current_item)

    def mouseMoveEvent(self, event):
        if self.current_item and self.start_point:
            end_point = self.mapToScene(event.pos())
            # Tính toán kích thước dựa trên vị trí chuột
            rect = QRectF(self.start_point, end_point).normalized()
            self.current_item.setRect(rect)

    def mouseReleaseEvent(self, event):
        self.current_item = None
        self.start_point = None

# 2. Cửa sổ chính của ứng dụng
class SVGPaintApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Studio Pro - SVG Paint")
        self.resize(1100, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Cột trái: Toolbar
        self.toolbar = QFrame()
        self.toolbar.setFixedWidth(70)
        self.toolbar.setStyleSheet("background-color: #2D2D2D; border-right: 1px solid #3F3F3F;")
        toolbar_layout = QVBoxLayout(self.toolbar)
        toolbar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        btn_rect = QPushButton("Rect") # Nút vẽ hình chữ nhật
        btn_rect.setFixedSize(50, 50)
        btn_rect.setStyleSheet("background-color: #3D3D3D; color: white; border-radius: 5px;")
        toolbar_layout.addWidget(btn_rect)
        
        main_layout.addWidget(self.toolbar)

        # Vùng giữa: Canvas chuyên dụng
        self.canvas = PaintCanvas()
        main_layout.addWidget(self.canvas, stretch=1)

        # Cột phải: Properties
        self.properties_panel = QFrame()
        self.properties_panel.setFixedWidth(240)
        self.properties_panel.setStyleSheet("background-color: #2D2D2D; border-left: 1px solid #3F3F3F;")
        main_layout.addWidget(self.properties_panel)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SVGPaintApp()
    window.show()
    sys.exit(app.exec())