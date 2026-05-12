import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, 
                             QVBoxLayout, QFrame, QPushButton, QGraphicsView, 
                             QGraphicsScene, QGraphicsRectItem, QGraphicsEllipseItem, 
                             QGraphicsLineItem, QGraphicsItem)
from PyQt6.QtCore import Qt, QRectF, QLineF
from PyQt6.QtGui import QPen, QColor, QBrush

class PaintCanvas(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene(0, 0, 800, 600)
        self.setScene(self.scene)
        self.setBackgroundBrush(QBrush(QColor("#1E1E1E")))
        
        self.mode = "select" # Chế độ mặc định là chọn
        self.current_item = None
        self.start_point = None

    def set_mode(self, mode):
        self.mode = mode
        # Nếu ở chế độ Select, cho phép tương tác với các item
        # Nếu ở chế độ Vẽ, tạm thời tắt tương tác để không bị vướng khi kéo chuột vẽ mới
        for item in self.scene.items():
            item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, mode == "select")
            item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, mode == "select")

    def mousePressEvent(self, event):
        if self.mode == "select":
            super().mousePressEvent(event) # Chạy xử lý mặc định của thư viện (chọn/kéo)
        elif event.button() == Qt.MouseButton.LeftButton:
            self.start_point = self.mapToScene(event.pos())
            pen = QPen(QColor("#4BBEFF"), 2)
            
            if self.mode == "rect":
                self.current_item = QGraphicsRectItem()
            elif self.mode == "ellipse":
                self.current_item = QGraphicsEllipseItem()
            elif self.mode == "line":
                self.current_item = QGraphicsLineItem()
            
            if self.current_item:
                self.current_item.setPen(pen)
                # Cho phép hình mới vẽ có thể được chọn và di chuyển sau này
                self.current_item.setFlags(
                    QGraphicsItem.GraphicsItemFlag.ItemIsSelectable | 
                    QGraphicsItem.GraphicsItemFlag.ItemIsMovable
                )
                self.scene.addItem(self.current_item)

    def mouseMoveEvent(self, event):
        if self.mode == "select":
            super().mouseMoveEvent(event)
        elif self.current_item and self.start_point:
            end_point = self.mapToScene(event.pos())
            if self.mode == "line":
                self.current_item.setLine(QLineF(self.start_point, end_point))
            else:
                rect = QRectF(self.start_point, end_point).normalized()
                self.current_item.setRect(rect)

    def mouseReleaseEvent(self, event):
        if self.mode == "select":
            super().mouseReleaseEvent(event)
        self.current_item = None
        self.start_point = None

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
        
        def create_btn(text, mode):
            btn = QPushButton(text)
            btn.setFixedSize(50, 50)
            btn.setStyleSheet("background-color: #3D3D3D; color: white; border-radius: 5px;")
            btn.clicked.connect(lambda: self.canvas.set_mode(mode))
            return btn

        toolbar_layout.addWidget(create_btn("Sel", "select")) # Nút chọn
        toolbar_layout.addWidget(create_btn("Rect", "rect"))
        toolbar_layout.addWidget(create_btn("Circ", "ellipse"))
        toolbar_layout.addWidget(create_btn("Line", "line"))
        
        main_layout.addWidget(self.toolbar)
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