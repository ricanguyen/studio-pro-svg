import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, 
                             QVBoxLayout, QFrame, QPushButton, QGraphicsView, 
                             QGraphicsScene, QGraphicsRectItem, QGraphicsEllipseItem, 
                             QGraphicsLineItem, QGraphicsItem, QLabel, QFileDialog)
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
        # Bật/tắt khả năng tương tác dựa trên chế độ Select
        for item in self.scene.items():
            item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, mode == "select")
            item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, mode == "select")

    def change_color(self, color_hex):
        for item in self.scene.selectedItems():
            # Đường thẳng không có màu nền (Brush), chỉ có màu viền (Pen)
            if isinstance(item, QGraphicsLineItem):
                pen = item.pen()
                pen.setColor(QColor(color_hex))
                item.setPen(pen)
            elif hasattr(item, 'setBrush'):
                item.setBrush(QBrush(QColor(color_hex)))

    def clear_canvas(self):
        self.scene.clear()

    def export_svg(self, file_path):
        with open(file_path, "w") as f:
            f.write(f'<svg width="800" height="600" xmlns="http://www.w3.org/2000/svg">\n')
            f.write(f'  <rect width="100%" height="100%" fill="#1E1E1E"/>\n')
            
            for item in self.scene.items():
                if isinstance(item, QGraphicsRectItem):
                    r = item.rect()
                    color = item.brush().color().name()
                    f.write(f'  <rect x="{r.x()}" y="{r.y()}" width="{r.width()}" height="{r.height()}" fill="{color}" stroke="#4BBEFF" stroke-width="2"/>\n')
                elif isinstance(item, QGraphicsEllipseItem):
                    r = item.rect()
                    color = item.brush().color().name()
                    f.write(f'  <ellipse cx="{r.x() + r.width()/2}" cy="{r.y() + r.height()/2}" rx="{r.width()/2}" ry="{r.height()/2}" fill="{color}" stroke="#4BBEFF" stroke-width="2"/>\n')
                elif isinstance(item, QGraphicsLineItem):
                    l = item.line()
                    color = item.pen().color().name()
                    f.write(f'  <line x1="{l.x1()}" y1="{l.y1()}" x2="{l.x2()}" y2="{l.y2()}" stroke="{color}" stroke-width="2"/>\n')
            
            f.write('</svg>')

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
                if self.mode == "line":
                    self.current_item.setLine(QLineF(self.start_point, self.start_point))
                self.current_item.setPen(pen)
                self.current_item.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable | QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
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

        # 1. Toolbar
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
        toolbar_layout.addWidget(create_tool("Line", "line")) # Thêm lại nút Line
        
        btn_clear = QPushButton("Clear")
        btn_clear.clicked.connect(lambda: self.canvas.clear_canvas())
        toolbar_layout.addWidget(btn_clear)
        
        main_layout.addWidget(self.toolbar)

        # 2. Canvas
        self.canvas = PaintCanvas()
        main_layout.addWidget(self.canvas, stretch=1)

        # 3. Properties Panel
        self.properties = QFrame()
        self.properties.setFixedWidth(240)
        self.properties.setStyleSheet("background-color: #2D2D2D; border-left: 1px solid #3F3F3F;")
        prop_layout = QVBoxLayout(self.properties)
        
        btn_save = QPushButton("SAVE SVG")
        btn_save.setFixedHeight(40)
        btn_save.setStyleSheet("background-color: #4BBEFF; color: black; font-weight: bold; border-radius: 5px;")
        btn_save.clicked.connect(self.save_file)
        prop_layout.addWidget(btn_save)
        
        prop_layout.addWidget(QLabel("<b style='color:white'>COLOR PALETTE</b>"))
        colors = ["#FF5555", "#50FA7B", "#F1FA8C", "#BD93F9", "#FF79C6"]
        for c in colors:
            btn = QPushButton(); btn.setFixedHeight(30)
            btn.setStyleSheet(f"background-color: {c}; border-radius: 3px;")
            btn.clicked.connect(lambda ch, color=c: self.canvas.change_color(color))
            prop_layout.addWidget(btn)
        
        prop_layout.addStretch()
        main_layout.addWidget(self.properties)

    def save_file(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Drawing", "", "SVG Files (*.svg)")
        if file_path:
            self.canvas.export_svg(file_path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SVGPaintApp()
    window.show()
    sys.exit(app.exec())