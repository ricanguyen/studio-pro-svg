from PyQt6.QtWidgets import QFrame, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt
from utils.file_handler import SVGHandler
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtGui import QPixmap, QIcon  
from PyQt6.QtCore import Qt, QSize      
from PyQt6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QLineEdit, QColorDialog, QWidget) # Thêm các module này
from PyQt6.QtGui import QPixmap, QIcon, QColor
from PyQt6.QtCore import Qt, QSize
from utils.file_handler import SVGHandler

class Toolbar(QFrame):
    def __init__(self, canvas):
        super().__init__()
        self.canvas = canvas
        self.setFixedWidth(80)
        self.setObjectName("leftToolbar") # ID để QSS nhận diện
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # CHUYỂN LOGO SP VỀ ĐÂY
        logo_label = QLabel("SP")
        logo_label.setObjectName("logoLabel") # Dùng ID trong styles.qss
        logo_label.setFixedSize(50, 50)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_label)

        # Nút Clear (CHUYỂN SANG DÙNG ICON)
        btn_clear = QPushButton() # Xóa chữ "CLEAR"
        btn_clear.setObjectName("btnClear") # ID để QSS nhận diện
        
        # Thêm Icon (Tôi khuyên bạn nên đặt tên file là img/clear.svg cho chuẩn)
        btn_clear.setIcon(QIcon("img/clear.svg")) 
        btn_clear.setIconSize(QSize(24, 24)) # Kích thước 24x24 là chuẩn đẹp và sắc nét
        
        # Thêm Tooltip (Cực kỳ quan trọng để người dùng biết nút làm gì)
        btn_clear.setToolTip("Clear Canvas (Dọn sạch vùng vẽ)")

        # Đồng bộ kích thước với các nút công cụ khác (Ví dụ 65x45)
        btn_clear.setFixedSize(65, 45)

        btn_clear.clicked.connect(self.canvas.clear_all)
        layout.addWidget(btn_clear)

        # Thêm khoảng cách và tiêu đề trước khi đến các công cụ vẽ
        layout.addSpacing(20)
        tools_title = QLabel("<b style='color:#AAAAAA; font-size: 10px;'>TOOLS</b>")
        tools_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(tools_title)

        # Các nút vẽ
        tools = [("cursor.svg", "select", "Select Tool (V)"),("square.svg", "rect", "Rectangle Tool (R)"), ("circle.svg", "ellipse", "Ellipse Tool (E)"), ("minus.svg", "line", "Line Tool (L)")]
        for icon_file, mode, tooltip in tools:
            btn = QPushButton()  # Để trống, không truyền text vào nữa
            btn.setObjectName("toolBtn")
            
            # Gán icon cho nút
            btn.setIcon(QIcon(f"img/{icon_file}"))
            btn.setIconSize(QSize(24, 24)) # Chỉnh kích thước icon cho vừa vặn
            
            # Thêm Tooltip để khi rê chuột vào sẽ hiện tên công cụ
            btn.setToolTip(tooltip)
            
            btn.clicked.connect(lambda checked, m=mode: self.canvas.set_mode(m))
            layout.addWidget(btn)
        
        layout.addStretch()

class PropertiesPanel(QFrame):
    def __init__(self, canvas):
        super().__init__()
        self.canvas = canvas
        self.setFixedWidth(220)
        self.setObjectName("rightPanel")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # 1. Tiêu đề Properties
        prop_title = QLabel("Properties")
        prop_title.setObjectName("panelTitle")
        layout.addWidget(prop_title)

       # --- THÊM ĐƯỜNG KẺ NGANG Ở ĐÂY ---
        separator = QFrame()
        separator.setFixedHeight(1)  # Ép cứng chiều cao đúng 1 pixel
        separator.setObjectName("separator")
        layout.addWidget(separator)
        # --------------------------------
        # NÚT EXPORT NẰM DƯỚI TIÊU ĐỀ
        btn_save = QPushButton("EXPORT SVG")
        btn_save.setObjectName("btnAction")
        btn_save.clicked.connect(lambda: SVGHandler.export_svg(self, self.canvas.scene))
        layout.addWidget(btn_save)

        layout.addSpacing(20) # Khoảng cách trước bảng màu
       # --- PHẦN MỚI: CHỌN MÀU (FILL COLOR) ---
        color_title = QLabel("<b style='color:#AAAAAA; font-size: 10px;'>FILL COLOR</b>")
        layout.addWidget(color_title)

        # Gọi cái ColorPickerWidget vừa tạo ở trên
        self.fill_picker = ColorPickerWidget(
            initial_color="#4BBEFF", 
            on_color_change=self.canvas.change_color
        )
        layout.addWidget(self.fill_picker)
        # ----------------------------------------
        
        layout.addStretch()

class ColorPickerWidget(QWidget):
    def __init__(self, initial_color="#FFFFFF", on_color_change=None):
        super().__init__()
        self.on_color_change = on_color_change
        self.current_color = initial_color

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # 1. Nút hiển thị màu hiện tại (Click để mở bảng chọn màu)
        self.btn_color = QPushButton()
        self.btn_color.setFixedSize(30, 30)
        self.btn_color.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update_button_color(self.current_color)
        self.btn_color.clicked.connect(self.open_color_dialog)

        # 2. Ô nhập mã Hex
        self.hex_input = QLineEdit(self.current_color)
        self.hex_input.setObjectName("hexInput")
        self.hex_input.setMaxLength(7) # Giới hạn 7 ký tự: #FFFFFF
        self.hex_input.textChanged.connect(self.on_hex_typed)

        layout.addWidget(self.btn_color)
        layout.addWidget(self.hex_input)

    def update_button_color(self, hex_color):
        # Cập nhật màu nền cho nút
        self.btn_color.setStyleSheet(f"""
            background-color: {hex_color}; 
            border: 1px solid #555555; 
            border-radius: 4px;
        """)

    def open_color_dialog(self):
        # Mở bảng chọn màu của hệ thống
        color = QColorDialog.getColor(QColor(self.current_color), self, "Select Color")
        if color.isValid():
            hex_val = color.name().upper()
            self.hex_input.setText(hex_val) # Sẽ tự động trigger hàm on_hex_typed

    def on_hex_typed(self, text):
        # Chỉ xử lý khi người dùng gõ đủ mã Hex hợp lệ
        if len(text) == 7 and text.startswith('#'):
            self.current_color = text
            self.update_button_color(self.current_color)
            if self.on_color_change:
                self.on_color_change(self.current_color)