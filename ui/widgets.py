import sys
from PyQt6.QtWidgets import (
    QButtonGroup, QFrame, QSlider, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QWidget, QLineEdit, QColorDialog, QGraphicsOpacityEffect,
    QStackedWidget, QFontComboBox, QSpinBox, QGraphicsTextItem
)
from PyQt6.QtGui import QIcon, QColor, QFont
from PyQt6.QtCore import Qt, QSize, QTimer
from utils.file_handler import SVGHandler

class Toolbar(QFrame):
    def __init__(self, canvas):
        super().__init__()
        self.canvas = canvas
        self.setFixedWidth(80)
        self.setObjectName("leftToolbar")

        self.group = QButtonGroup(self)
        self.group.setExclusive(True)
        
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Logo app
        logo_label = QLabel("SP")
        logo_label.setObjectName("logoLabel")
        logo_label.setFixedSize(50, 50)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_label)

        # Nút dọn dẹp canvas
        btn_clear = QPushButton()
        btn_clear.setObjectName("btnClear")
        btn_clear.setIcon(QIcon("img/clear.svg"))
        btn_clear.setIconSize(QSize(24, 24))
        btn_clear.setToolTip("Clear Canvas (Dọn sạch vùng vẽ)")
        btn_clear.setFixedSize(65, 45)
        btn_clear.clicked.connect(self.canvas.clear_all)
        layout.addWidget(btn_clear)

        self.btn_grid = QPushButton()
        self.btn_grid.setObjectName("btnGrid")
        self.btn_grid.setIcon(QIcon("img/grid.svg")) # ⚠️ Nhớ chèn 1 file grid.svg vào thư mục img nhé
        self.btn_grid.setIconSize(QSize(24, 24))
        self.btn_grid.setToolTip("Toggle Grid (Bật/Tắt Lưới)")
        self.btn_grid.setFixedSize(65, 45)
        self.btn_grid.setCheckable(True) # Cho phép nút giữ trạng thái lún xuống
        self.btn_grid.setChecked(False)  # Mặc định chưa bấm
        self.btn_grid.clicked.connect(self.canvas.toggle_grid)
        layout.addWidget(self.btn_grid)

        layout.addSpacing(20)
        tools_title = QLabel("<b style='color:#AAAAAA; font-size: 10px;'>TOOLS</b>")
        tools_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(tools_title)

        # Danh sách công cụ vẽ
        tools = [
            ("cursor.svg", "select", "Select (V)"),
            ("square.svg", "rect", "Rectangle (R)"),
            ("circle.svg", "ellipse", "Ellipse (E)"),
            ("minus.svg", "line", "Line (L)"),
            ("polygon.svg", "polygon", "Polygon (P)"),
             ("text.svg", "text", "Text (P)")
        ]
        
        for icon_file, mode, tooltip in tools:
            btn = QPushButton()
            btn.setObjectName("toolBtn")
            btn.setIcon(QIcon(f"img/{icon_file}"))
            btn.setIconSize(QSize(24, 24))
            btn.setToolTip(tooltip)

            btn.setCheckable(True)
            self.group.addButton(btn)
            if mode == "select":
                btn.setChecked(True)

            btn.clicked.connect(lambda checked, m=mode: self.canvas.set_mode(m))
            layout.addWidget(btn)
        
        layout.addStretch()

class PropertiesPanel(QFrame):
    def __init__(self, canvas):
        super().__init__()
        self.canvas = canvas
        self.setFixedWidth(240) # Mở rộng thêm một chút để chứa đủ nút
        self.setObjectName("rightPanel")
        self.init_ui()
        self.update_panel_state([])

    def _add_separator(self, layout):
        line = QFrame()
        line.setFixedHeight(1)
        line.setObjectName("separator")
        layout.addWidget(line)

    def _create_labeled_widget(self, label_text, widget):
        """Tạo nhanh một cụm gồm Label nhỏ phía trên và Widget phía dưới"""
        v_layout = QVBoxLayout()
        v_layout.setContentsMargins(0, 0, 0, 0)
        v_layout.setSpacing(4) # <-- THÊM DÒNG NÀY: Ép chữ sát vào widget
        lbl = QLabel(f"<b style='color:#888; font-size: 9px;'>{label_text}</b>")
        v_layout.addWidget(lbl)
        v_layout.addWidget(widget)
        return v_layout

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        title = QLabel("Properties")
        title.setObjectName("panelTitle")
        layout.addWidget(title)
        self._add_separator(layout)

        # ==================================================
        # QSTACKEDWIDGET: VŨ KHÍ LẬT TRANG GIAO DIỆN
        # ==================================================
        self.stacked_widget = QStackedWidget()

        # --------------------------------------------------
        # TRANG 1: THUỘC TÍNH HÌNH KHỐI (SHAPE)
        # --------------------------------------------------
        self.shape_page = QWidget()
        shape_layout = QVBoxLayout(self.shape_page)
        shape_layout.setContentsMargins(0, 0, 0, 0)

        shape_layout.setSpacing(15) 
        shape_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        color_section = QWidget()
        color_layout = QHBoxLayout(color_section)
        color_layout.setContentsMargins(0, 0, 0, 0)

        self.fill_picker = ColorPickerWidget("#4BBEFF", self.canvas.change_color)
        color_layout.addLayout(self._create_labeled_widget("FILL", self.fill_picker))

        self.stroke_picker = ColorPickerWidget("#ADC6FF", self.canvas.change_stroke_color)
        color_layout.addLayout(self._create_labeled_widget("STROKE", self.stroke_picker))
        
        shape_layout.addWidget(color_section)
        self._add_separator(shape_layout)

        self.stroke_width_widget = StrokeWidthWidget(2, self.canvas.set_stroke_width)
        shape_layout.addSpacing(10)
        shape_layout.addLayout(self._create_labeled_widget("STROKE WIDTH", self.stroke_width_widget))

        # --------------------------------------------------
        # TRANG 2: THUỘC TÍNH VĂN BẢN (TEXT)
        # --------------------------------------------------
        self.text_page = QWidget()
        text_layout = QVBoxLayout(self.text_page)
        text_layout.setContentsMargins(0, 0, 0, 0)

        text_layout.setSpacing(15)
        text_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # 1. Text Color
        self.text_color_picker = ColorPickerWidget("#FFFFFF", self.canvas.change_text_color)
        text_layout.addLayout(self._create_labeled_widget("TEXT COLOR", self.text_color_picker))
        text_layout.addSpacing(10)

        # 2. Font Family
        self.font_combo = QFontComboBox()
        self.font_combo.setStyleSheet("background-color: #1E1E1E; color: white; border: 1px solid #444; border-radius: 3px; min-height: 25px;")
        self.font_combo.currentFontChanged.connect(self.canvas.change_font_family)
        text_layout.addLayout(self._create_labeled_widget("FONT FAMILY", self.font_combo))
        text_layout.addSpacing(10)

       # 3. Size & Styles (B, I, U, S) chung 1 hàng
        style_container = QWidget() # Tạo một cái hộp (Widget) để chứa
        style_row = QHBoxLayout(style_container) # Gắn Layout vào cái hộp đó
        style_row.setContentsMargins(0, 0, 0, 0)
        
        self.font_size_spin = StrokeWidthWidget(16, self.canvas.change_font_size)
        style_row.addWidget(self.font_size_spin)
        style_row.addWidget(self.font_size_spin)
        
        btn_style = """
            QPushButton { background: #2A2A2A; border: 1px solid #444; border-radius: 3px; } 
            QPushButton:hover { background: #333333; }
            QPushButton:checked { background: #4BBEFF; border: 1px solid #4BBEFF; }
        """
        
        # 1. Nút BOLD
        self.btn_bold = QPushButton() # Bỏ chữ "B" ở đây
        self.btn_bold.setIcon(QIcon("img/bold.svg")) # Đảm bảo tên file SVG của bạn khớp nhé
        self.btn_bold.setToolTip("Bold (In đậm)")
        self.btn_bold.setCheckable(True)
        self.btn_bold.setFixedSize(28, 25) # Nới rộng xíu cho vuông vắn với icon
        self.btn_bold.setStyleSheet(btn_style)
        self.btn_bold.clicked.connect(lambda: self.canvas.toggle_font_style('bold', self.btn_bold.isChecked()))
        
        # 2. Nút ITALIC
        self.btn_italic = QPushButton()
        self.btn_italic.setIcon(QIcon("img/italic.svg"))
        self.btn_italic.setToolTip("Italic (In nghiêng)")
        self.btn_italic.setCheckable(True)
        self.btn_italic.setFixedSize(28, 25)
        self.btn_italic.setStyleSheet(btn_style)
        self.btn_italic.clicked.connect(lambda: self.canvas.toggle_font_style('italic', self.btn_italic.isChecked()))
        
        # 3. Nút UNDERLINE
        self.btn_underline = QPushButton()
        self.btn_underline.setIcon(QIcon("img/underline.svg"))
        self.btn_underline.setToolTip("Underline (Gạch chân)")
        self.btn_underline.setCheckable(True)
        self.btn_underline.setFixedSize(28, 25)
        self.btn_underline.setStyleSheet(btn_style)
        self.btn_underline.clicked.connect(lambda: self.canvas.toggle_font_style('underline', self.btn_underline.isChecked()))
        
        # 4. Nút STRIKETHROUGH
        self.btn_strike = QPushButton()
        self.btn_strike.setIcon(QIcon("img/strikethrough.svg")) 
        self.btn_strike.setToolTip("Strikethrough (Gạch ngang)")
        self.btn_strike.setCheckable(True)
        self.btn_strike.setFixedSize(28, 25)
        self.btn_strike.setStyleSheet(btn_style)
        self.btn_strike.clicked.connect(lambda: self.canvas.toggle_font_style('strike', self.btn_strike.isChecked()))
        
        # Add vào layout
        style_row.addWidget(self.btn_bold)
        style_row.addWidget(self.btn_italic)
        style_row.addWidget(self.btn_underline)
        style_row.addWidget(self.btn_strike)
        
        style_row.addWidget(self.btn_bold)
        style_row.addWidget(self.btn_italic)
        style_row.addWidget(self.btn_underline)
        style_row.addWidget(self.btn_strike)
        
        text_layout.addLayout(self._create_labeled_widget("SIZE & STYLE", style_container))

        # Đưa 2 trang vào Stack
        self.stacked_widget.addWidget(self.shape_page)
        self.stacked_widget.addWidget(self.text_page)
        layout.addWidget(self.stacked_widget)
        
        self._add_separator(layout)

        # --------------------------------------------------
        # OPACITY (LUÔN HIỆN Ở DƯỚI CÙNG CHO CẢ SHAPE & TEXT)
        # --------------------------------------------------
        self.opacity_container = QWidget()
        op_v_layout = QVBoxLayout(self.opacity_container)
        op_v_layout.setContentsMargins(0, 5, 0, 5)

        op_header = QHBoxLayout()
        op_header.addWidget(QLabel("<b style='color:#888; font-size: 9px;'>OPACITY</b>"))
        op_header.addStretch()
        self.opacity_label = QLabel("100%")
        self.opacity_label.setStyleSheet("color: white; font-size: 10px;")
        op_header.addWidget(self.opacity_label)

        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.valueChanged.connect(self.update_opacity_logic)

        op_v_layout.addLayout(op_header)
        op_v_layout.addWidget(self.opacity_slider)
        layout.addWidget(self.opacity_container)

        layout.addStretch()

    # --------------------------------------------------
    # LOGIC CHUYỂN TRANG THÔNG MINH KHI CLICK ITEM
    # --------------------------------------------------
    def update_panel_state(self, selected_items):
        has_selection = len(selected_items) > 0
        self.stacked_widget.setEnabled(has_selection)
        self.opacity_container.setEnabled(has_selection)
        
        if has_selection:
            # Xóa hiệu ứng mờ cho các khu vực chỉnh sửa
            self.stacked_widget.setGraphicsEffect(None)
            self.opacity_container.setGraphicsEffect(None)
            
            item = selected_items[0]
            
            if isinstance(item, QGraphicsTextItem):
                self.stacked_widget.setCurrentWidget(self.text_page)
                font = item.font()
                self.font_combo.setCurrentFont(font)
                self.font_size_spin.input.setText(str(font.pointSize()))
                self.btn_bold.setChecked(font.bold())
                self.btn_italic.setChecked(font.italic())
                self.btn_underline.setChecked(font.underline())
                self.btn_strike.setChecked(font.strikeOut())
                
                color_hex = item.defaultTextColor().name().upper()
                self.text_color_picker.hex_input.blockSignals(True)
                self.text_color_picker.hex_input.setText(color_hex)
                self.text_color_picker.update_button_style(color_hex)
                self.text_color_picker.current_color = color_hex
                self.text_color_picker.hex_input.blockSignals(False)
                
            else:
                self.stacked_widget.setCurrentWidget(self.shape_page)
                if hasattr(item, 'pen'):
                    self.stroke_width_widget.input.setText(str(int(item.pen().width())))
        else:
            # Nếu không chọn gì, chỉ làm mờ khu vực Stack và Opacity, chừa nút Export ra
            eff1 = QGraphicsOpacityEffect()
            eff1.setOpacity(0.4)
            self.stacked_widget.setGraphicsEffect(eff1)
            
            eff2 = QGraphicsOpacityEffect()
            eff2.setOpacity(0.4)
            self.opacity_container.setGraphicsEffect(eff2)

    def update_opacity_logic(self, value):
        self.opacity_label.setText(f"{value}%")
        self.canvas.set_opacity(value)

class ColorPickerWidget(QWidget):
    def __init__(self, initial_color="#FFFFFF", on_color_change=None):
        super().__init__()
        self.on_color_change = on_color_change
        self.current_color = initial_color
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        self.btn_color = QPushButton()
        self.btn_color.setFixedSize(28, 28)
        self.btn_color.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update_button_style(self.current_color)
        self.btn_color.clicked.connect(self.open_dialog)

        self.hex_input = QLineEdit(self.current_color)
        self.hex_input.setObjectName("hexInput")
        self.hex_input.setFixedWidth(65)
        self.hex_input.textChanged.connect(self.on_hex_changed)

        layout.addWidget(self.btn_color)
        layout.addWidget(self.hex_input)
        layout.addStretch()

    def update_button_style(self, color):
        self.btn_color.setStyleSheet(f"background-color: {color}; border: 1px solid #444; border-radius: 3px;")

    def open_dialog(self):
        color = QColorDialog.getColor(QColor(self.current_color), self, "Pick Color")
        if color.isValid():
            self.hex_input.setText(color.name().upper())

    def on_hex_changed(self, text):
        if len(text) == 7 and text.startswith('#'):
            self.current_color = text
            self.update_button_style(text)
            if self.on_color_change:
                self.on_color_change(text)

class StrokeWidthWidget(QWidget):
    def __init__(self, initial_value=2, on_change=None):
        super().__init__()
        self.on_change = on_change
        self.value = initial_value

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        self.input = QLineEdit(str(self.value))
        self.input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.input.setObjectName("strokeWidthInput")
        self.input.textChanged.connect(self.handle_input)

        # Cụm nút Up/Down
        btns = QWidget()
        btn_layout = QVBoxLayout(btns)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(0)

        self.up = QPushButton("▲")
        self.down = QPushButton("▼")
        for b in [self.up, self.down]:
            b.setFixedSize(18, 12)
            b.setObjectName("widthStepBtn")

        self.up.clicked.connect(lambda: self.step(1))
        self.down.clicked.connect(lambda: self.step(-1))

        btn_layout.addWidget(self.up)
        btn_layout.addWidget(self.down)

        layout.addWidget(self.input)
        layout.addWidget(btns)
        layout.addStretch()

    def step(self, delta):
        new_val = max(1, min(200, self.value + delta))
        self.input.setText(str(new_val))

    def handle_input(self, text):
        try:
            val = int(text)
            self.value = val
            if self.on_change:
                self.on_change(val)
        except ValueError:
            pass

class NotificationToast(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setFixedSize(120, 40)
        self.setObjectName("toast")
        self.setStyleSheet("""
            #toast {
                background-color: #2A2A2A;
                border: 1px solid #4BBEFF;
                border-radius: 20px;
            }
            QLabel { color: white; font-size: 11px; border: none; }
        """)
        
        self.layout = QHBoxLayout(self)
        self.icon_label = QLabel("⏳") # Icon loading tạm thời
        self.text_label = QLabel("Đang lưu...")
        self.layout.addWidget(self.icon_label)
        self.layout.addWidget(self.text_label)
        
        self.hide() # Mặc định ẩn

    def show_message(self, text, icon="✅", duration=2000):
        self.text_label.setText(text)
        self.icon_label.setText(icon)
        self.show()
        self.raise_() # Đảm bảo nằm trên cùng
        # Tự động ẩn sau duration ms
        QTimer.singleShot(duration, self.hide)           