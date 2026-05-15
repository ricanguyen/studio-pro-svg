from PyQt6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QSlider,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QWidget,
    QLineEdit,
    QColorDialog,
    QGraphicsOpacityEffect,
    QStackedWidget,
    QFontComboBox,
    QGraphicsTextItem,
)
from PyQt6.QtGui import QIcon, QColor, QIntValidator
from PyQt6.QtCore import Qt, QSize, QTimer


# ==========================================
# 1. TOOLBAR (THANH CÔNG CỤ BÊN TRÁI)
# ==========================================
class Toolbar(QFrame):
    def __init__(self, canvas):
        super().__init__()
        self.canvas = canvas
        self.setFixedWidth(80)
        self.setObjectName("leftToolbar")

        self.group = QButtonGroup(self)
        self.group.setExclusive(True)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
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

        # Nút Lưới (Grid)
        self.btn_grid = QPushButton()
        self.btn_grid.setObjectName("btnGrid")
        self.btn_grid.setIcon(QIcon("img/grid.svg"))
        self.btn_grid.setIconSize(QSize(24, 24))
        self.btn_grid.setToolTip("Toggle Grid (Bật/Tắt Lưới)")
        self.btn_grid.setFixedSize(65, 45)
        self.btn_grid.setCheckable(True)
        self.btn_grid.setChecked(False)
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
            ("text.svg", "text", "Text (T)"),
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

    def set_theme(self, is_dark):
        self.setObjectName("mainToolbar")
        bg_color = "#121212" if is_dark else "#F8F9FA"
        border_color = "#2D2D2D" if is_dark else "#CCCCCC"
        label_color = "#AAAAAA" if is_dark else "#555555"
        btn_hover = "#2A2A2A" if is_dark else "#E9ECEF"

        self.setStyleSheet(f"""
            QWidget#mainToolbar {{ 
                background-color: {bg_color}; 
                border-right: 1px solid {border_color}; 
            }}
            QLabel {{ color: {label_color}; }}
            QPushButton {{ background-color: transparent; border: none; padding: 5px; }}
            QPushButton:hover {{ background-color: {btn_hover}; }}
            QPushButton:checked {{ background-color: #4BBEFF; }}
        """)


# ==========================================
# 2. PROPERTIES PANEL (BẢNG THUỘC TÍNH)
# ==========================================
class PropertiesPanel(QFrame):
    def __init__(self, canvas):
        super().__init__()
        self.canvas = canvas
        self.setFixedWidth(240)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setObjectName("rightPanel")
        self.init_ui()
        self.update_panel_state([])

    def _add_separator(self, layout):
        line = QFrame()
        line.setFixedHeight(1)
        line.setObjectName("separator")
        layout.addWidget(line)

    def _create_labeled_widget(self, label_text, widget):
        v_layout = QVBoxLayout()
        v_layout.setContentsMargins(0, 0, 0, 0)
        v_layout.setSpacing(4)
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

        self.stacked_widget = QStackedWidget()

        # --- TRANG 1: SHAPE PROPERTIES ---
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

        self.stroke_picker = ColorPickerWidget(
            "#ADC6FF", self.canvas.change_stroke_color
        )
        color_layout.addLayout(
            self._create_labeled_widget("STROKE", self.stroke_picker)
        )

        shape_layout.addWidget(color_section)
        self._add_separator(shape_layout)

        self.stroke_width_widget = StrokeWidthWidget(2, self.canvas.set_stroke_width)
        shape_layout.addSpacing(10)
        shape_layout.addLayout(
            self._create_labeled_widget("STROKE WIDTH", self.stroke_width_widget)
        )

        # --- TRANG 2: TEXT PROPERTIES ---
        self.text_page = QWidget()
        text_layout = QVBoxLayout(self.text_page)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(15)
        text_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.text_color_picker = ColorPickerWidget(
            "#FFFFFF", self.canvas.change_text_color
        )
        text_layout.addLayout(
            self._create_labeled_widget("TEXT COLOR", self.text_color_picker)
        )
        text_layout.addSpacing(10)

        self.font_combo = QFontComboBox()
        self.font_combo.currentFontChanged.connect(self.canvas.change_font_family)
        text_layout.addLayout(
            self._create_labeled_widget("FONT FAMILY", self.font_combo)
        )
        text_layout.addSpacing(10)

        # Hàng chứa Size và Style chữ
        style_container = QWidget()
        style_row = QHBoxLayout(style_container)
        style_row.setContentsMargins(0, 0, 0, 0)

        self.font_size_spin = StrokeWidthWidget(16, self.canvas.change_font_size)
        style_row.addWidget(self.font_size_spin)

        # Nút B, I, U, S (Đã xóa các dòng bị lặp 2 lần)
        self.btn_bold = self._create_style_btn(
            "bold.svg",
            "Bold",
            lambda: self.canvas.toggle_font_style("bold", self.btn_bold.isChecked()),
        )
        self.btn_italic = self._create_style_btn(
            "italic.svg",
            "Italic",
            lambda: self.canvas.toggle_font_style(
                "italic", self.btn_italic.isChecked()
            ),
        )
        self.btn_underline = self._create_style_btn(
            "underline.svg",
            "Underline",
            lambda: self.canvas.toggle_font_style(
                "underline", self.btn_underline.isChecked()
            ),
        )
        self.btn_strike = self._create_style_btn(
            "strikethrough.svg",
            "Strikethrough",
            lambda: self.canvas.toggle_font_style(
                "strike", self.btn_strike.isChecked()
            ),
        )

        style_row.addWidget(self.btn_bold)
        style_row.addWidget(self.btn_italic)
        style_row.addWidget(self.btn_underline)
        style_row.addWidget(self.btn_strike)

        text_layout.addLayout(
            self._create_labeled_widget("SIZE & STYLE", style_container)
        )

        self.stacked_widget.addWidget(self.shape_page)
        self.stacked_widget.addWidget(self.text_page)
        layout.addWidget(self.stacked_widget)

        self._add_separator(layout)

        # --- OPACITY ---
        self.opacity_container = QWidget()
        op_v_layout = QVBoxLayout(self.opacity_container)
        op_v_layout.setContentsMargins(0, 5, 0, 5)

        op_header = QHBoxLayout()
        op_header.addWidget(
            QLabel("<b style='color:#888; font-size: 9px;'>OPACITY</b>")
        )
        op_header.addStretch()
        self.opacity_label = QLabel("100%")
        self.opacity_label.setStyleSheet(
            "font-size: 10px;"
        )  # Bỏ màu cứng để đổi theo theme
        op_header.addWidget(self.opacity_label)

        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.valueChanged.connect(self.update_opacity_logic)

        op_v_layout.addLayout(op_header)
        op_v_layout.addWidget(self.opacity_slider)
        layout.addWidget(self.opacity_container)
        layout.addStretch()

    def _create_style_btn(self, icon_name, tooltip, callback):
        """Hàm phụ trợ rút gọn code tạo nút Style"""
        btn = QPushButton()
        btn.setIcon(QIcon(f"img/{icon_name}"))
        btn.setToolTip(tooltip)
        btn.setCheckable(True)
        btn.setFixedSize(28, 25)
        btn.clicked.connect(callback)
        return btn

    def update_panel_state(self, selected_items):
        has_selection = len(selected_items) > 0
        self.stacked_widget.setEnabled(has_selection)
        self.opacity_container.setEnabled(has_selection)

        if has_selection:
            self.stacked_widget.setGraphicsEffect(None)
            self.opacity_container.setGraphicsEffect(None)
            item = selected_items[0]

            # --- ĐỒNG BỘ OPACITY (Cho cả Text lẫn Shape) ---
            self.opacity_slider.blockSignals(
                True
            )  # Khóa signal để thanh trượt không tự kích hoạt hàm thay đổi
            current_opacity = int(item.opacity() * 100)
            self.opacity_slider.setValue(current_opacity)
            self.opacity_label.setText(f"{current_opacity}%")
            self.opacity_slider.blockSignals(False)

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

                # --- ĐỒNG BỘ STROKE (Màu viền & Độ dày) ---
                if hasattr(item, "pen"):
                    pen = item.pen()
                    self.stroke_width_widget.input.setText(str(int(pen.width())))

                    stroke_color = pen.color()
                    # Nếu alpha = 0 tức là trong suốt
                    stroke_hex = (
                        "transparent"
                        if stroke_color.alpha() == 0 or pen.style() == Qt.PenStyle.NoPen
                        else stroke_color.name().upper()
                    )

                    self.stroke_picker.hex_input.blockSignals(True)
                    self.stroke_picker.hex_input.setText(stroke_hex)
                    self.stroke_picker.update_button_style(stroke_hex)
                    self.stroke_picker.current_color = stroke_hex
                    self.stroke_picker.hex_input.blockSignals(False)

                # --- ĐỒNG BỘ FILL (Màu nền) ---
                if hasattr(item, "brush"):
                    brush = item.brush()
                    fill_color = brush.color()

                    # Kiểm tra xem hình này có màu nền hay là dạng trong suốt (transparent)
                    fill_hex = (
                        "transparent"
                        if fill_color.alpha() == 0
                        or brush.style() == Qt.BrushStyle.NoBrush
                        else fill_color.name().upper()
                    )

                    self.fill_picker.hex_input.blockSignals(True)
                    self.fill_picker.hex_input.setText(fill_hex)
                    self.fill_picker.update_button_style(fill_hex)
                    self.fill_picker.current_color = fill_hex
                    self.fill_picker.hex_input.blockSignals(False)
        else:
            eff1 = QGraphicsOpacityEffect()
            eff1.setOpacity(0.4)
            self.stacked_widget.setGraphicsEffect(eff1)

            eff2 = QGraphicsOpacityEffect()
            eff2.setOpacity(0.4)
            self.opacity_container.setGraphicsEffect(eff2)

    def update_opacity_logic(self, value):
        self.opacity_label.setText(f"{value}%")
        self.canvas.set_opacity(value)

    def set_theme(self, is_dark):
        """Hàm cấp màu chuẩn xác cho cả bảng Properties"""
        self.setObjectName("mainProperties")

        bg_color = "#121212" if is_dark else "#F8F9FA"
        panel_border = "#2D2D2D" if is_dark else "#CCCCCC"
        input_bg = "#2A2A2A" if is_dark else "#FFFFFF"
        input_color = "white" if is_dark else "#000000"
        input_border = "#444" if is_dark else "#CCC"
        label_color = "#E0E0E0" if is_dark else "#333333"
        btn_bg = "#2A2A2A" if is_dark else "#FFFFFF"
        btn_hover_bg = "#333333" if is_dark else "#E9ECEF"
        btn_hover_border = "#4BBEFF"

        self.setStyleSheet(f"""
            QWidget#mainProperties {{ 
                background-color: {bg_color}; 
                border-left: 1px solid {panel_border}; 
            }}
            QLabel {{ color: {label_color}; }}
            QLineEdit, QComboBox, QSpinBox {{
                background-color: {input_bg}; color: {input_color}; 
                border: 1px solid {input_border}; border-radius: 3px; padding: 4px;
            }}
            QPushButton {{ 
                background-color: {btn_bg}; color: {input_color}; 
                border: 1px solid {input_border}; border-radius: 3px; padding: 5px;
            }}
            QPushButton:hover {{ background-color: {btn_hover_bg}; border: 1px solid {btn_hover_border}; }}
            QPushButton:checked {{ background-color: #4BBEFF; border: 1px solid #4BBEFF; color: black; }}
            
            /* --- CSS CHO NÚT SPIN UP/DOWN NHÀ LÀM --- */
            QPushButton#spinButton {{
                background-color: {input_bg};
                color: {input_color};
                border: 1px solid {input_border};
                padding: 1px;
                border-radius: 2px;
            }}
            QPushButton#spinButton:hover {{
                background-color: {btn_hover_bg};
                border: 1px solid {btn_hover_border};
            }}
        """)


# ==========================================
# 3. CÁC COMPONENT CUSTOM DÙNG CHUNG
# ==========================================
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
        self.btn_color.setStyleSheet(
            f"background-color: {color}; border: 1px solid #444; border-radius: 3px;"
        )

    def open_dialog(self):
        color = QColorDialog.getColor(QColor(self.current_color), self, "Pick Color")
        if color.isValid():
            self.hex_input.setText(color.name().upper())

    def on_hex_changed(self, text):
        if len(text) == 7 and text.startswith("#"):
            self.current_color = text
            self.update_button_style(text)
            if self.on_color_change:
                self.on_color_change(text)

    def set_color(self, hex_color):
        # self.current_color = hex_color
        self.hex_input.setText(hex_color.upper())


class StrokeWidthWidget(QWidget):
    def __init__(self, value, callback):
        super().__init__()
        self.value = value
        self.callback = callback

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(1)

        self.input = QLineEdit(str(value))
        self.input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.input.setValidator(QIntValidator(1, 200))
        self.input.setFixedWidth(40)
        self.input.editingFinished.connect(self.set_value_from_input)
        self.main_layout.addWidget(self.input)

        btn_container = QWidget()
        btn_layout = QVBoxLayout(btn_container)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setSpacing(0)

        self.icon_size = QSize(12, 12)

        self.btn_up = QPushButton()
        self.btn_up.setObjectName("spinButton")
        # Đã đổi thành up_arrow.svg (dùng gạch dưới) để chuẩn với các file trước
        self.btn_up.setIcon(QIcon("img/up-arrow.svg"))
        self.btn_up.setIconSize(self.icon_size)
        self.btn_up.setFixedSize(18, 14)
        self.btn_up.clicked.connect(lambda: self.step(1))
        btn_layout.addWidget(self.btn_up)

        self.btn_down = QPushButton()
        self.btn_down.setObjectName("spinButton")
        self.btn_down.setIcon(QIcon("img/down-arrow.svg"))
        self.btn_down.setIconSize(self.icon_size)
        self.btn_down.setFixedSize(18, 14)
        self.btn_down.clicked.connect(lambda: self.step(-1))
        btn_layout.addWidget(self.btn_down)

        self.main_layout.addWidget(btn_container)

    def step(self, delta):
        new_val = max(1, min(200, self.value + delta))
        self.value = new_val
        self.input.setText(str(new_val))
        self.callback(new_val)

    def set_value_from_input(self):
        try:
            val = int(self.input.text())
            new_val = max(1, min(200, val))
            self.value = new_val
            self.input.setText(str(new_val))
            self.callback(new_val)
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
        self.icon_label = QLabel("⏳")
        self.text_label = QLabel("Đang lưu...")
        self.layout.addWidget(self.icon_label)
        self.layout.addWidget(self.text_label)

        self.hide()

    def show_message(self, text, icon="✅", duration=2000):
        self.text_label.setText(text)
        self.icon_label.setText(icon)
        self.show()
        self.raise_()
        QTimer.singleShot(duration, self.hide)
