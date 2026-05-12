import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, 
                             QVBoxLayout, QFrame, QPushButton, QGraphicsView, 
                             QGraphicsScene, QGraphicsRectItem, QGraphicsEllipseItem, 
                             QGraphicsLineItem, QGraphicsItem, QLabel)
from PyQt6.QtCore import Qt, QRectF, QLineF
from PyQt6.QtGui import QPen, QColor, QBrush

class PaintCanvas(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene(0, 0, 800, 600)
        self.setScene(self.scene)
        self.setBackgroundBrush(QBrush(QColor("#1E1E1E")))
        self.mode = "select"
        self.current_item = None
        self.start_point = None

    def set_mode(self, mode):
        self.mode = mode
        for item in self.scene.items():
            item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, mode == "select")
            item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, mode == "select")

    def change_color(self, color_hex):
        # Đổi màu cho tất cả các hình đang được chọn
        for item in self.scene.selectedItems():
            if isinstance(item, (QGraphicsRectItem, QGraphicsEllipseItem)):
                item.setBrush(QBrush(QColor(color_hex)))

    def mousePressEvent(self, event):
        if self.mode == "select":
            super().mousePressEvent(event)
        elif event.button() == Qt.MouseButton.LeftButton:
            self.start_point = self.mapToScene(event.pos())
            pen = QPen(QColor("#4BBEFF"), 2)
            if self.mode == "rect": self.current_item = QGraphicsRectItem()
            elif self.mode == "ellipse": self.current_item = QGraphicsEllipseItem()
            elif self.mode == "line": self.current_item = QGraphicsLineItem()
            
            if self.current_item:
                self.current_item.setPen(pen)
                self.current_item.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable | QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
                self.scene.addItem(self.current_item)

    def mouseMoveEvent(self, event):
        if self.mode == "select": super().mouseMoveEvent(event)
        elif self.current_item and self.start_point:
            end_point = self.mapToScene(event.pos())
            if self.mode == "line": self.current_item.setLine(QLineF(self.start_point, end_point))
            else: self.current_item.setRect(QRectF(self.start_point, end_point).normalized())

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.current_item = None

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

        # 1. Toolbar (Trái)
        self.toolbar = QFrame()
        self.toolbar.setFixedWidth(70)
        self.toolbar.setStyleSheet("background-color: #2D2D2D; border-right: 1px solid #3F3F3F;")
        toolbar_layout = QVBoxLayout(self.toolbar)
        def create_tool(txt, m):
            btn = QPushButton(txt); btn.setFixedSize(50, 50)
            btn.setStyleSheet("background-color: #3D3D3D; color: white; border-radius: 5px;")
            btn.clicked.connect(lambda: self.canvas.set_mode(m)); return btn
        toolbar_layout.addWidget(create_tool("Sel", "select"))
        toolbar_layout.addWidget(create_tool("Rect", "rect"))
        toolbar_layout.addWidget(create_tool("Circ", "ellipse"))
        
        main_layout.addWidget(self.toolbar)

        # 2. Canvas (Giữa)
        self.canvas = PaintCanvas()
        main_layout.addWidget(self.canvas, stretch=1)

        # 3. Properties Panel (Phải)
        self.properties = QFrame()
        self.properties.setFixedWidth(240)
        self.properties.setStyleSheet("background-color: #2D2D2D; border-left: 1px solid #3F3F3F;")
        prop_layout = QVBoxLayout(self.properties)
        prop_layout.addWidget(QLabel("<b style='color:white'>FILL COLOR</b>"))
        
        # Tạo các nút màu mẫu
        colors = ["#FF5555", "#50FA7B", "#F1FA8C", "#BD93F9", "#FF79C6"]
        for c in colors:
            btn = QPushButton()
            btn.setFixedHeight(30)
            btn.setStyleSheet(f"background-color: {c}; border-radius: 3px;")
            btn.clicked.connect(lambda checked, color=c: self.canvas.change_color(color))
            prop_layout.addWidget(btn)
        
        prop_layout.addStretch()
        main_layout.addWidget(self.properties)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SVGPaintApp()
    window.show()
    sys.exit(app.exec())