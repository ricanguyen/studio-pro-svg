import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QWidget, 
                             QHBoxLayout, QVBoxLayout, QFrame, QLabel, QMenu)
from PyQt6.QtGui import QIcon, QKeySequence, QShortcut, QUndoStack, QAction
from PyQt6.QtCore import Qt

from canvas.paint_canvas import PaintCanvas
from ui.widgets import Toolbar, PropertiesPanel
from utils.file_handler import SVGHandler

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
        title_label.setStyleSheet("color: white; font-weight: bold; font-size: 14px; border: none; margin-right: 20px;")
        h_layout.addWidget(title_label)
        
        # Danh sách các menu
        for menu_name in ["File", "Edit", "View", "Object", "Window", "Help"]:
            btn = QPushButton(menu_name)
            btn.setObjectName("navButton")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            
            # CHỈ XỬ LÝ DROPDOWN CHO NÚT "FILE"
            if menu_name == "File":
                file_menu = QMenu(self)
                file_menu.setStyleSheet("""
                    QMenu { background-color: #2A2A2A; color: #E0E0E0; border: 1px solid #444; padding: 5px 0px; }
                    QMenu::item { padding: 5px 30px 5px 20px; }
                    QMenu::item:selected { background-color: #4BBEFF; color: black; }
                    QMenu::separator { height: 1px; background-color: #444; margin: 4px 10px; }
                """)
                
                # 1. Action: New (Phải nằm trên cùng)
                new_action = QAction("New", self)
                new_action.setShortcut("Ctrl+N")
                new_action.triggered.connect(self.new_file)
                file_menu.addAction(new_action)
                
                # Đường kẻ phân cách
                file_menu.addSeparator()
                
                # 2. Action: Open
                open_action = QAction("Open SVG...", self)
                open_action.setShortcut("Ctrl+O")
                open_action.triggered.connect(lambda: SVGHandler.import_svg(self, self.canvas.scene))
                file_menu.addAction(open_action)
                
                # 3. Action: Export
                export_action = QAction("Export SVG...", self)
                export_action.setShortcut("Ctrl+E")
                export_action.triggered.connect(lambda: SVGHandler.export_svg(self, self.canvas.scene))
                file_menu.addAction(export_action)
                
                # Gắn Menu vào nút và đăng ký phím tắt toàn cục
                btn.setMenu(file_menu)
                self.addAction(new_action)
                self.addAction(open_action)
                self.addAction(export_action)
            
            h_layout.addWidget(btn)
            
        h_layout.addStretch()
        return header

    def _setup_shortcuts(self):
        """Cấu hình các phím tắt điều khiển"""
        QShortcut(QKeySequence("Ctrl+Z"), self).activated.connect(self.undo_stack.undo)
        QShortcut(QKeySequence("Ctrl+Y"), self).activated.connect(self.undo_stack.redo)
        QShortcut(QKeySequence("Delete"), self).activated.connect(self.canvas.delete_selected)
        
    # --- THÊM HÀM NÀY ĐỂ XỬ LÝ TẠO FILE MỚI ---
    def new_file(self):
        """Dọn sạch canvas và reset lịch sử Undo để bắt đầu bản vẽ mới"""
        self.canvas.scene.clear()
        self.undo_stack.clear()
        
        # Reset lại bảng Properties bên phải (làm mờ nó đi vì không có gì được chọn)
        if hasattr(self, 'properties'):
            self.properties.update_panel_state([])

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
    