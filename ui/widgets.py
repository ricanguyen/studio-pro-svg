import sys
from PyQt6.QtWidgets import (
    QButtonGroup, QFrame, QSlider, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QWidget, QLineEdit, QColorDialog, QGraphicsOpacityEffect
)
from PyQt6.QtGui import QIcon, QColor, QPixmap
from PyQt6.QtCore import Qt, QSize
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

        layout.addSpacing(20)
        tools_title = QLabel("<b style='color:#AAAAAA; font-size: 10px;'>TOOLS</b>")
        tools_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(tools_title)

        # Danh sách công cụ vẽ
        tools = [
            ("cursor.svg", "select", "Select (V)"),
            ("square.svg", "rect", "Rectangle (R)"),
            ("circle.svg", "ellipse", "Ellipse (E)"),
            ("minus.svg", "line", "Line (L)")
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
        self.setFixedWidth(220)
        self.setObjectName("rightPanel")
        self.init_ui()
        self.update_panel_state([])

    def _add_separator(self, layout):
        """Hàm tiện ích để kẻ đường phân cách"""
        line = QFrame()
        line.setFixedHeight(1)
        line.setObjectName("separator")
        layout.addWidget(line)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Tiêu đề và nút xuất file
        title = QLabel("Properties")
        title.setObjectName("panelTitle")
        layout.addWidget(title)
        self._add_separator(layout)

        btn_save = QPushButton("EXPORT SVG")
        btn_save.setObjectName("btnAction")
        btn_save.clicked.connect(lambda: SVGHandler.export_svg(self, self.canvas.scene))
        layout.addWidget(btn_save)
        layout.addSpacing(15)

        # Khu vực chỉnh màu (Fill & Stroke)
        color_section = QWidget()
        color_layout = QHBoxLayout(color_section)
        color_layout.setContentsMargins(0, 0, 0, 0)

        # Fill Color
        self.fill_picker = ColorPickerWidget("#4BBEFF", self.canvas.change_color)
        color_layout.addLayout(self._create_labeled_widget("FILL", self.fill_picker))

        # Stroke Color
        self.stroke_picker = ColorPickerWidget("#ADC6FF", self.canvas.change_stroke_color)
        color_layout.addLayout(self._create_labeled_widget("STROKE", self.stroke_picker))
        
        layout.addWidget(color_section)
        self._add_separator(layout)

        # Độ dày viền (Stroke Width)
        self.stroke_width_widget = StrokeWidthWidget(2, self.canvas.set_stroke_width)
        width_layout = self._create_labeled_widget("STROKE WIDTH", self.stroke_width_widget)
        layout.addSpacing(10)
        layout.addLayout(width_layout)
        
        self._add_separator(layout)

        # Độ trong suốt (Opacity)
        opacity_container = QWidget()
        op_v_layout = QVBoxLayout(opacity_container)
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
        layout.addWidget(opacity_container)

    def _create_labeled_widget(self, label_text, widget):
        """Tạo nhanh một cụm gồm Label nhỏ phía trên và Widget phía dưới"""
        v_layout = QVBoxLayout()
        v_layout.setContentsMargins(0, 0, 0, 0)
        lbl = QLabel(f"<b style='color:#888; font-size: 9px;'>{label_text}</b>")
        v_layout.addWidget(lbl)
        v_layout.addWidget(widget)
        return v_layout

    def update_panel_state(self, selected_items):
        has_selection = len(selected_items) > 0
        self.setEnabled(has_selection)
        
        if has_selection:
            self.setGraphicsEffect(None)
            # Lấy thông số từ object đầu tiên để đồng bộ UI
            item = selected_items[0]
            if hasattr(item, 'pen'):
                self.stroke_width_widget.input.setText(str(int(item.pen().width())))
        else:
            eff = QGraphicsOpacityEffect()
            eff.setOpacity(0.4)
            self.setGraphicsEffect(eff)

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
        new_val = max(1, min(50, self.value + delta))
        self.input.setText(str(new_val))

    def handle_input(self, text):
        try:
            val = int(text)
            self.value = val
            if self.on_change:
                self.on_change(val)
        except ValueError:
            pass