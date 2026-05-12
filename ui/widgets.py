from PyQt6.QtWidgets import QFrame, QSlider, QVBoxLayout, QPushButton, QLabel
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
from PyQt6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QLineEdit, QColorDialog, QWidget,
                             QSpinBox, QComboBox) # Thêm QSpinBox và QComboBox


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

        layout.addSpacing(15) # Khoảng cách trước bảng màu
       # --- PHẦN MÀU SẮC (FILL & STROKE SONG SONG) ---
        color_section = QWidget()
        color_layout = QHBoxLayout(color_section)
        color_layout.setContentsMargins(0, 0, 0, 0)
        color_layout.setSpacing(10)

        # Cột bên trái: FILL
        fill_container = QWidget()
        fill_v_layout = QVBoxLayout(fill_container)
        fill_v_layout.setContentsMargins(0, 0, 0, 0)
        fill_v_layout.addWidget(QLabel("<b style='color:#888; font-size: 9px;'>FILL</b>"))
        self.fill_picker = ColorPickerWidget(
            initial_color="#4BBEFF", 
            on_color_change=self.canvas.change_color
        )
        fill_v_layout.addWidget(self.fill_picker)

        # Cột bên phải: STROKE
        stroke_container = QWidget()
        stroke_v_layout = QVBoxLayout(stroke_container)
        stroke_v_layout.setContentsMargins(0, 0, 0, 0)
        stroke_v_layout.addWidget(QLabel("<b style='color:#888; font-size: 9px;'>STROKE</b>"))
        self.stroke_picker = ColorPickerWidget(
            initial_color="#ADC6FF", 
            on_color_change=self.canvas.change_stroke_color
        )
        stroke_v_layout.addWidget(self.stroke_picker)

        # Thêm cả 2 vào layout ngang
        color_layout.addWidget(fill_container)
        color_layout.addWidget(stroke_container)

        layout.addWidget(color_section)
        # ----------------------------------------------
       # --- THÊM ĐƯỜNG KẺ NGANG Ở ĐÂY ---
        separator = QFrame()
        separator.setFixedHeight(1)  # Ép cứng chiều cao đúng 1 pixel
        separator.setObjectName("separator")
        layout.addWidget(separator)
        # --- PHẦN STROKE PROPERTIES (WIDTH & STYLE) ---
        stroke_prop_section = QWidget()
        stroke_prop_layout = QHBoxLayout(stroke_prop_section)
        stroke_prop_layout.setContentsMargins(0, 0, 0, 0)
        stroke_prop_layout.setSpacing(10)

        # --- PHẦN STROKE WIDTH (MINIMALIST) ---
        width_container = QWidget()
        width_v_layout = QVBoxLayout(width_container)
        width_v_layout.setContentsMargins(0, 0, 0, 0)
        width_v_layout.addWidget(QLabel("<b style='color:#888; font-size: 9px;'>STROKE WIDTH</b>"))
        
        # Dùng widget mới tự chế
        self.stroke_width_widget = StrokeWidthWidget(
            initial_value=2, 
            on_change=self.canvas.set_stroke_width
        )
        width_v_layout.addWidget(self.stroke_width_widget)
        
        layout.addSpacing(15)
        layout.addWidget(width_container)
            # --- THÊM ĐƯỜNG KẺ NGANG Ở ĐÂY ---
        separator = QFrame()
        separator.setFixedHeight(1)  # Ép cứng chiều cao đúng 1 pixel
        separator.setObjectName("separator")
        layout.addWidget(separator)
        # --- PHẦN STROKE PROPERTIES (WIDTH & STYLE) ---
        stroke_prop_section = QWidget()
        stroke_prop_layout = QHBoxLayout(stroke_prop_section)
        stroke_prop_layout.setContentsMargins(0, 0, 0, 0)
        stroke_prop_layout.setSpacing(10)
        # --- PHẦN OPACITY (SLIDER) ---
        opacity_container = QWidget()
        opacity_v_layout = QVBoxLayout(opacity_container)
        opacity_v_layout.setContentsMargins(0, 0, 0, 0)
        opacity_v_layout.setSpacing(5)

        # Header hàng Opacity (Text + % Value)
        opacity_header_layout = QHBoxLayout()
        opacity_label = QLabel("<b style='color:#888; font-size: 9px;'>OPACITY</b>")
        self.opacity_value_label = QLabel("100%")
        self.opacity_value_label.setStyleSheet("color: #FFFFFF; font-size: 10px;")
        
        opacity_header_layout.addWidget(opacity_label)
        opacity_header_layout.addStretch()
        opacity_header_layout.addWidget(self.opacity_value_label)
        
        # Thanh trượt Opacity
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.setObjectName("opacitySlider")
        
        # Kết nối logic
        self.opacity_slider.valueChanged.connect(self.update_opacity_logic)

        opacity_v_layout.addLayout(opacity_header_layout)
        opacity_v_layout.addWidget(self.opacity_slider)
        
        layout.addSpacing(15)
        layout.addWidget(opacity_container)

    # Hàm bổ trợ ngay trong PropertiesPanel để cập nhật Label và gọi Canvas
    def update_opacity_logic(self, value):
        self.opacity_value_label.setText(f"{value}%")
        self.canvas.set_opacity(value)

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
        self.hex_input.setMaxLength(10)

        self.hex_input.textChanged.connect(self.on_hex_typed)

        layout.addWidget(self.btn_color)
        layout.addWidget(self.hex_input)
        
        # ---> THÊM DÒNG NÀY ĐỂ ÉP CHÚNG NÓ GỌN VỀ BÊN TRÁI <---
        layout.addStretch()

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

class StrokeWidthWidget(QWidget):
    def __init__(self, initial_value=2, on_change=None):
        super().__init__()
        self.on_change = on_change
        self.value = initial_value

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2) # Khoảng cách rất nhỏ giữa ô nhập và nút

        # 1. Ô nhập số
        self.input = QLineEdit(str(self.value))
        self.input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.input.setObjectName("strokeWidthInput")
        self.input.textChanged.connect(self.handle_text_change)

        # 2. Cột chứa 2 nút tăng giảm nằm dọc
        button_container = QWidget()
        button_layout = QVBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(0)

        self.btn_up = QPushButton("▲")
        self.btn_down = QPushButton("▼")
        
        # Style cho nút nhỏ lại
        for btn in [self.btn_up, self.btn_down]:
            btn.setFixedSize(18, 13)
            btn.setObjectName("widthStepBtn")

        self.btn_up.clicked.connect(lambda: self.update_value(1))
        self.btn_down.clicked.connect(lambda: self.update_value(-1))

        button_layout.addWidget(self.btn_up)
        button_layout.addWidget(self.btn_down)

        layout.addWidget(self.input, 1)
        layout.addWidget(button_container)

    def update_value(self, delta):
        new_val = max(1, min(20, self.value + delta))
        if new_val != self.value:
            self.value = new_val
            self.input.setText(str(self.value))

    def handle_text_change(self, text):
        try:
            val = int(text)
            self.value = val
            if self.on_change:
                self.on_change(val)
        except ValueError:
            pass