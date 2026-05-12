import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QWidget, QHBoxLayout, 
                             QVBoxLayout, QFrame, QLabel) # Thêm QVBoxLayout, QFrame, QLabel
from PyQt6.QtGui import QIcon, QUndoStack, QKeySequence, QShortcut
from PyQt6.QtCore import Qt

# Import các thành phần từ thư mục con
from canvas.paint_canvas import PaintCanvas
from ui.widgets import Toolbar, PropertiesPanel

class SVGPaintApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.undo_stack = QUndoStack(self)
        self.setWindowTitle("Studio Pro - SVG Paint")
        self.resize(1100, 700)

        # GÁN ICON CHO CỬA SỔ
        # Thay 'logo.png' bằng tên file chính xác của bạn trong thư mục img
        self.setWindowIcon(QIcon("img/logo.png"))

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Khởi tạo Canvas và bọc nó vào một Container có Header
        self.canvas = PaintCanvas(self.undo_stack)
        
        # TẠO VÙNG GIỮA (Header + Canvas)
        center_container = QWidget()
        center_layout = QVBoxLayout(center_container)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(0)

        # Tạo thanh Header giả
        header = QFrame()
        header.setFixedHeight(50)
        header.setObjectName("canvasHeader") # Để định dạng trong styles.qss nếu cần
        header.setStyleSheet("background-color: #121212; border-bottom: 1px solid #2D2D2D;")
        h_layout = QHBoxLayout(header)
        
       # Chữ Studio Pro
        title_label = QLabel("Studio Pro")
        # Thêm text-decoration: none để bỏ gạch chân hoàn toàn
        title_label.setStyleSheet("""
            color: white; 
            font-weight: bold; 
            margin-left: 15px; 
            font-size: 14px;
            text-decoration: none; 
            border: none;
        """)
        h_layout.addWidget(title_label)
        
        # Các mục Menu (Chuyển từ QLabel sang QPushButton)
        for m in ["File", "Edit", "View", "Object", "Window", "Help"]:
            btn_menu = QPushButton(m)
            btn_menu.setObjectName("navButton")  # Đặt tên để viết CSS
            btn_menu.setCursor(Qt.CursorShape.PointingHandCursor) # Hiện bàn tay khi rê vào
            
            # Nếu bạn muốn xử lý logic khi click vào menu:
            # btn_menu.clicked.connect(lambda ch, name=m: print(f"Open {name} menu"))
            
            h_layout.addWidget(btn_menu)
        
        # Đưa Header và Canvas vào layout dọc của vùng giữa
        center_layout.addWidget(header)
        center_layout.addWidget(self.canvas)

        # 2. Khởi tạo các Widget UI khác
        self.toolbar = Toolbar(self.canvas)
        self.properties = PropertiesPanel(self.canvas)

        # 3. Sắp xếp vào Layout chính (Thay self.canvas bằng center_container)
        main_layout.addWidget(self.toolbar)          # Trái
        main_layout.addWidget(center_container, 1)   # Giữa (Giờ đã bao gồm Header + Canvas)
        main_layout.addWidget(self.properties)       # Phải

        # 4. Phím tắt hệ thống
        QShortcut(QKeySequence("Ctrl+Z"), self).activated.connect(self.undo_stack.undo)
        QShortcut(QKeySequence("Ctrl+Y"), self).activated.connect(self.undo_stack.redo)
        QShortcut(QKeySequence("Delete"), self).activated.connect(self.canvas.delete_selected)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    try:
        with open("styles.qss", "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        pass

    window = SVGPaintApp()
    window.show()
    sys.exit(app.exec())