import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QWidget, 
                             QHBoxLayout, QVBoxLayout, QFrame, QLabel)
from PyQt6.QtGui import QIcon, QKeySequence, QShortcut, QUndoStack
from PyQt6.QtCore import Qt

from canvas.paint_canvas import PaintCanvas
from ui.widgets import Toolbar, PropertiesPanel

class SVGPaintApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Studio Pro - SVG Paint")
        self.resize(1200, 800)
        self.setWindowIcon(QIcon("img/logo.png"))

        # Khởi tạo phần lõi xử lý dữ liệu
        self.undo_stack = QUndoStack(self)

        # Khởi tạo các thành phần giao diện chính
        self.canvas = PaintCanvas(self.undo_stack)
        self.toolbar = Toolbar(self.canvas)
        self.properties = PropertiesPanel(self.canvas)
        
        # Liên kết canvas với panel thuộc tính
        self.canvas.properties_panel = self.properties

        self._init_ui()
        self._setup_shortcuts()

    def _init_ui(self):
        """Thiết lập bố cục tổng thể của ứng dụng"""
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Vùng trung tâm: Gồm Header và Canvas
        center_container = QWidget()
        center_layout = QVBoxLayout(center_container)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(0)

        header = self._setup_header()
        
        center_layout.addWidget(header)
        center_layout.addWidget(self.canvas)

        # Thêm các thành phần vào hàng ngang chính
        main_layout.addWidget(self.toolbar)      # Trái
        main_layout.addWidget(center_container, 1) # Giữa (co giãn)
        main_layout.addWidget(self.properties)   # Phải

    def _setup_header(self):
        """Tạo thanh menu header phía trên canvas"""
        header = QFrame()
        header.setFixedHeight(50)
        header.setObjectName("canvasHeader")
        header.setStyleSheet("background-color: #121212; border-bottom: 1px solid #2D2D2D;")
        
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(10, 0, 10, 0)
        
        title_label = QLabel("Studio Pro")
        title_label.setStyleSheet("""
            color: white; font-weight: bold; font-size: 14px;
            border: none; margin-right: 20px;
        """)
        h_layout.addWidget(title_label)
        
        # Tạo nhanh các nút menu
        for menu_name in ["File", "Edit", "View", "Object", "Window", "Help"]:
            btn = QPushButton(menu_name)
            btn.setObjectName("navButton")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            h_layout.addWidget(btn)
            
        h_layout.addStretch() # Đẩy các nút về phía trái
        return header

    def _setup_shortcuts(self):
        """Cấu hình các phím tắt điều khiển"""
        QShortcut(QKeySequence("Ctrl+Z"), self).activated.connect(self.undo_stack.undo)
        QShortcut(QKeySequence("Ctrl+Y"), self).activated.connect(self.undo_stack.redo)
        QShortcut(QKeySequence("Delete"), self).activated.connect(self.canvas.delete_selected)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Load stylesheet từ file ngoài
    try:
        with open("styles.qss", "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print("Cảnh báo: Không tìm thấy file styles.qss")

    window = SVGPaintApp()
    window.show()
    sys.exit(app.exec())