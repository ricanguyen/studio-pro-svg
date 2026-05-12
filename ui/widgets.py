from PyQt6.QtWidgets import QFrame, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt
from utils.file_handler import SVGHandler

class Toolbar(QFrame):
    def __init__(self, canvas):
        super().__init__()
        self.canvas = canvas
        self.setFixedWidth(80)
        self.setStyleSheet("background-color: #2D2D2D; border-right: 1px solid #3F3F3F;")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Nút Clear
        btn_clear = QPushButton("CLEAR")
        btn_clear.setStyleSheet("background-color: #f39c12; color: white; font-weight: bold; min-height: 40px;")
        btn_clear.clicked.connect(self.canvas.clear_all)
        layout.addWidget(btn_clear)

        # Các nút vẽ
        tools = [("Select", "select"), ("Rect", "rect"), ("Circ", "ellipse"), ("Line", "line")]
        for text, mode in tools:
            btn = QPushButton(text)
            btn.setFixedSize(65, 45)
            btn.setStyleSheet("background-color: #3D3D3D; color: white; border-radius: 4px;")
            btn.clicked.connect(lambda checked, m=mode: self.canvas.set_mode(m))
            layout.addWidget(btn)
        
        layout.addStretch()

class PropertiesPanel(QFrame):
    def __init__(self, canvas):
        super().__init__()
        self.canvas = canvas
        self.setFixedWidth(220)
        self.setStyleSheet("background-color: #2D2D2D; border-left: 1px solid #3F3F3F;")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<b style='color:white'>COLOR PALETTE</b>"))
        
        colors = ["#FF5555", "#50FA7B", "#F1FA8C", "#BD93F9", "#FF79C6", "#FFFFFF"]
        for c in colors:
            btn = QPushButton()
            btn.setFixedHeight(30)
            btn.setStyleSheet(f"background-color: {c}; border-radius: 3px;")
            btn.clicked.connect(lambda checked, color=c: self.canvas.change_color(color))
            layout.addWidget(btn)
        btn_save = QPushButton("EXPORT SVG")
        btn_save.setFixedHeight(45)
        btn_save.setStyleSheet("background-color: #4BBEFF; color: black; font-weight: bold; margin-top: 10px;")
        # Kết nối nút bấm với hàm xử lý file ở utils
        btn_save.clicked.connect(lambda: SVGHandler.export_svg(self, self.canvas.scene))
        self.layout().addWidget(btn_save)
        layout.addStretch()
         