import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, 
                             QVBoxLayout, QFrame, QPushButton, QGraphicsView, 
                             QGraphicsScene, QGraphicsRectItem, QGraphicsEllipseItem, 
                             QGraphicsLineItem, QGraphicsItem, QLabel, QFileDialog)
from PyQt6.QtCore import Qt, QRectF, QLineF
from PyQt6.QtGui import QPen, QColor, QBrush, QUndoStack, QUndoCommand

# 1. Lệnh Undo cho việc THÊM hình
class AddCommand(QUndoCommand):
    def __init__(self, scene, item):
        super().__init__()
        self.scene = scene
        self.item = item
    def undo(self): self.scene.removeItem(self.item)
    def redo(self): self.scene.addItem(self.item)

# 2. Lệnh Undo cho việc ĐỔI MÀU
class ColorCommand(QUndoCommand):
    def __init__(self, item, old_brush, new_brush):
        super().__init__()
        self.item = item
        self.old_brush = old_brush
        self.new_brush = new_brush
    def undo(self): self.item.setBrush(self.old_brush)
    def redo(self): self.item.setBrush(self.new_brush)

class PaintCanvas(QGraphicsView):
    def __init__(self, undo_stack):
        super().__init__()
        self.undo_stack = undo_stack
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
        for item in self.scene.selectedItems():
            if hasattr(item, 'setBrush'):
                old_brush = item.brush()
                new_brush = QBrush(QColor(color_hex))
                # Lưu vào UndoStack để có thể nhấn Undo màu
                self.undo_stack.push(ColorCommand(item, old_brush, new_brush))

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

    def mouseMoveEvent(self, event):
        if self.mode == "select":
            super().mouseMoveEvent(event)
        elif self.current_item and self.start_point:
            end_point = self.mapToScene(event.pos())
            if isinstance(self.current_item, QGraphicsLineItem):
                self.current_item.setLine(QLineF(self.start_point, end_point))
            else:
                self.current_item.setRect(QRectF(self.start_point, end_point).normalized())
            if self.current_item.scene() is None: self.scene.addItem(self.current_item)

    def mouseReleaseEvent(self, event):
        if self.current_item and not self.mode == "select":
            self.scene.removeItem(self.current_item)
            self.undo_stack.push(AddCommand(self.scene, self.current_item))
        super().mouseReleaseEvent(event)
        self.current_item = None

class SVGPaintApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.undo_stack = QUndoStack(self)
        self.setWindowTitle("Studio Pro - SVG Paint")
        self.resize(1100, 700)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Cột trái: Toolbar
        self.toolbar = QFrame()
        self.toolbar.setFixedWidth(75)
        self.toolbar.setStyleSheet("background-color: #2D2D2D; border-right: 1px solid #3F3F3F;")
        t_layout = QVBoxLayout(self.toolbar)
        
        # Nút Undo/Redo (Giao diện mới gọn hơn)
        btn_undo = QPushButton("↺ Undo"); btn_undo.clicked.connect(self.undo_stack.undo)
        t_layout.addWidget(btn_undo)
        btn_redo = QPushButton("↻ Redo"); btn_redo.clicked.connect(self.undo_stack.redo)
        t_layout.addWidget(btn_redo)
        
        t_layout.addSpacing(20)

        def create_tool(txt, m):
            btn = QPushButton(txt); btn.setFixedSize(55, 50)
            btn.setStyleSheet("background-color: #3D3D3D; color: white; border-radius: 5px;")
            btn.clicked.connect(lambda: self.canvas.set_mode(m)); return btn
        
        t_layout.addWidget(create_tool("Select", "select"))
        t_layout.addWidget(create_tool("Rect", "rect"))
        t_layout.addWidget(create_tool("Circ", "ellipse"))
        t_layout.addWidget(create_tool("Line", "line"))
        t_layout.addStretch()
        main_layout.addWidget(self.toolbar)

        # 2. Vùng giữa: Canvas
        self.canvas = PaintCanvas(self.undo_stack)
        main_layout.addWidget(self.canvas, stretch=1)

        # 3. Cột phải: Properties Panel (BẢNG MÀU ĐÃ TRỞ LẠI)
        self.properties = QFrame()
        self.properties.setFixedWidth(240)
        self.properties.setStyleSheet("background-color: #2D2D2D; border-left: 1px solid #3F3F3F;")
        p_layout = QVBoxLayout(self.properties)
        
        btn_save = QPushButton("EXPORT SVG")
        btn_save.setFixedHeight(45); btn_save.setStyleSheet("background-color: #4BBEFF; color: black; font-weight: bold; border-radius: 5px;")
        btn_save.clicked.connect(self.save_file); p_layout.addWidget(btn_save)
        
        p_layout.addSpacing(20)
        p_layout.addWidget(QLabel("<b style='color:white'>COLOR PALETTE</b>"))
        
        colors = ["#FF5555", "#50FA7B", "#F1FA8C", "#BD93F9", "#FF79C6", "#FFFFFF", "#000000"]
        for c in colors:
            btn = QPushButton(); btn.setFixedHeight(35)
            btn.setStyleSheet(f"background-color: {c}; border: 1px solid #555; border-radius: 4px;")
            btn.clicked.connect(lambda ch, color=c: self.canvas.change_color(color))
            p_layout.addWidget(btn)
        
        p_layout.addStretch()
        main_layout.addWidget(self.properties)

    def save_file(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save SVG", "", "SVG Files (*.svg)")
        if path:
            with open(path, "w") as f:
                f.write('<svg width="800" height="600" xmlns="http://www.w3.org/2000/svg">\n')
                for item in self.canvas.scene.items():
                    if isinstance(item, QGraphicsRectItem):
                        r = item.rect()
                        f.write(f'  <rect x="{r.x()}" y="{r.y()}" width="{r.width()}" height="{r.height()}" fill="{item.brush().color().name()}"/>\n')
                f.write('</svg>')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SVGPaintApp(); window.show()
    sys.exit(app.exec())