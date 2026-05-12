import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout
from PyQt6.QtGui import QUndoStack, QKeySequence, QShortcut

# Import các thành phần từ thư mục con
from canvas.paint_canvas import PaintCanvas
from ui.widgets import Toolbar, PropertiesPanel

class SVGPaintApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.undo_stack = QUndoStack(self)
        self.setWindowTitle("Studio Pro - SVG Paint")
        self.resize(1100, 700)

        # Cấu trúc nền
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Khởi tạo Canvas (Thành phần trung tâm)
        self.canvas = PaintCanvas(self.undo_stack)

        # 2. Khởi tạo các Widget UI và truyền Canvas vào để chúng điều khiển
        self.toolbar = Toolbar(self.canvas)
        self.properties = PropertiesPanel(self.canvas)

        # 3. Sắp xếp vào Layout chính
        main_layout.addWidget(self.toolbar)      # Trái
        main_layout.addWidget(self.canvas, 1)    # Giữa
        main_layout.addWidget(self.properties)   # Phải

        # 4. Phím tắt hệ thống
        QShortcut(QKeySequence("Ctrl+Z"), self).activated.connect(self.undo_stack.undo)
        QShortcut(QKeySequence("Ctrl+Y"), self).activated.connect(self.undo_stack.redo)
        QShortcut(QKeySequence("Delete"), self).activated.connect(self.canvas.delete_selected)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Áp dụng styles.qss nếu bạn đã có file này
    try:
        with open("styles.qss", "r") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        pass

    window = SVGPaintApp()
    window.show()
    sys.exit(app.exec())