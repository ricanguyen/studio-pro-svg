import math
from PyQt6.QtWidgets import (
    QGraphicsView,
    QGraphicsScene,
    QGraphicsRectItem,
    QGraphicsEllipseItem,
    QGraphicsLineItem,
    QGraphicsItem,
    QGraphicsPolygonItem,
    QGraphicsTextItem,
    QInputDialog,
    QLineEdit,
)
from PyQt6.QtCore import Qt, QRectF, QLineF, QPointF
from PyQt6.QtGui import QPen, QColor, QBrush, QPolygonF, QFont
from models.commands import AddCommand, DeleteCommand, ColorCommand


# =======================================================
# 1. HÀM TOÁN HỌC HỖ TRỢ ĐA GIÁC
# =======================================================
def point_to_segment_dist(p, p1, p2):
    x0, y0 = p.x(), p.y()
    x1, y1 = p1.x(), p1.y()
    x2, y2 = p2.x(), p2.y()

    dx = x2 - x1
    dy = y2 - y1
    if dx == 0 and dy == 0:
        return math.hypot(x0 - x1, y0 - y1)

    t = ((x0 - x1) * dx + (y0 - y1) * dy) / (dx * dx + dy * dy)
    t = max(0, min(1, t))
    px = x1 + t * dx
    py = y1 + t * dy
    return math.hypot(x0 - px, y0 - py)


# =======================================================
# 2. CLASS ĐA GIÁC THÔNG MINH (KÉO CẠNH SINH ĐỈNH)
# =======================================================
class InteractivePolygonItem(QGraphicsPolygonItem):
    def __init__(self, polygon, parent=None):
        super().__init__(polygon, parent)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.dragging_index = -1

    def mousePressEvent(self, event):
        if self.isSelected():
            pos = event.pos()
            poly = self.polygon()

            # Ưu tiên 1: Kéo một ĐỈNH đã có (Bán kính 8px)
            for i in range(poly.count()):
                if math.hypot(poly.at(i).x() - pos.x(), poly.at(i).y() - pos.y()) < 8:
                    self.dragging_index = i
                    event.accept()
                    return

            # Ưu tiên 2: Bấm trúng CẠNH (Khoảng cách < 5px) -> Sinh đỉnh mới
            min_dist = float("inf")
            insert_index = -1

            for i in range(poly.count()):
                p1 = poly.at(i)
                p2 = poly.at((i + 1) % poly.count())

                dist = point_to_segment_dist(pos, p1, p2)
                if dist < min_dist and dist < 5.0:
                    min_dist = dist
                    insert_index = i + 1

            if insert_index != -1:
                poly.insert(insert_index, pos)
                self.setPolygon(poly)
                self.dragging_index = insert_index
                event.accept()
                return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.dragging_index != -1:
            poly = self.polygon()
            poly.replace(self.dragging_index, event.pos())
            self.setPolygon(poly)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.dragging_index != -1:
            self.dragging_index = -1
            event.accept()
        else:
            super().mouseReleaseEvent(event)


# =======================================================
# CLASS TEXT THÔNG MINH (NHẬP CHỮ & DOUBLE-CLICK ĐỂ SỬA)
# =======================================================
class InteractiveTextItem(QGraphicsTextItem):
    def __init__(self, parent=None):
        super().__init__("", parent)
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemIsMovable
        )
        # Bật chế độ edit ngay khi vừa tạo
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)

    def focusOutEvent(self, event):
        """Khi click ra ngoài vùng text: Tắt chế độ gõ chữ, khóa lại thành object bình thường"""
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)

        # Nếu người dùng không nhập gì mà click ra ngoài -> Tự động xóa để rác không đầy scene
        if self.toPlainText().strip() == "":
            if self.scene():
                self.scene().removeItem(self)

        super().focusOutEvent(event)

    def mouseDoubleClickEvent(self, event):
        """Double click để bật lại con trỏ nhấp nháy và sửa chữ"""
        if self.isSelected():
            self.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
            self.setFocus()
        super().mouseDoubleClickEvent(event)


# =======================================================
# 3. CLASS CANVAS CHÍNH
# =======================================================
class PaintCanvas(QGraphicsView):
    def __init__(self, undo_stack):
        super().__init__()
        self.undo_stack = undo_stack
        self.scene = QGraphicsScene(0, 0, 800, 600)
        self.setScene(self.scene)

        # Cấu hình mặc định
        self.setBackgroundBrush(QBrush(QColor("#1E1E1E")))
        self.mode = "select"
        self.current_item = None
        self.start_point = None

        # Lưu trữ trạng thái công cụ hiện tại
        self.current_fill_color = "transparent"
        self.current_stroke_color = "#FFFFFF"
        self.current_stroke_width = 2
        self.current_opacity = 1.0

        self.scene.selectionChanged.connect(self.handle_selection_changed)
        self.show_grid = False
        self.is_dark_theme = True

    def reset_default_tools(self):
        """Đưa cọ vẽ về màu mặc định (Stroke Xám, Fill Trong suốt)"""
        self.current_fill_color = "transparent"
        self.current_stroke_color = (
            "#888888"  # Màu xám chuẩn, thấy rõ trên cả Dark/Light
        )
        self.current_stroke_width = 2
        self.current_opacity = 1.0

    def set_mode(self, mode):
        self.mode = mode
        # Chế độ select thì mới cho phép di chuyển/chọn item
        is_selectable = mode == "select"
        for item in self.scene.items():
            item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, is_selectable)
            item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, is_selectable)

        # --- Reset màu khi bắt đầu vẽ hình mới ---
        if mode != "select":
            self.scene.clearSelection()  # Bỏ chọn các hình cũ để tránh vô tình đổi màu chúng
            self.reset_default_tools()  # Reset màu cọ về Xám/Trong suốt

    def clear_all(self):
        all_items = [item for item in self.scene.items() if item.scene() == self.scene]
        if all_items:
            self.undo_stack.push(DeleteCommand(self.scene, all_items, "Clear All"))

    def delete_selected(self):
        items = self.scene.selectedItems()
        if items:
            self.undo_stack.push(DeleteCommand(self.scene, items))

    # --- Các hàm thay đổi thuộc tính đối tượng ---
    def change_color(self, color_hex):
        """Thay đổi màu nền (Fill)"""
        self.current_fill_color = color_hex
        new_color = QColor(color_hex)
        for item in self.scene.selectedItems():
            if hasattr(item, "setBrush") and not isinstance(item, QGraphicsLineItem):
                old_brush = item.brush()
                new_brush = QBrush(new_color)
                self.undo_stack.push(ColorCommand(item, old_brush, new_brush))
            elif isinstance(item, QGraphicsLineItem):
                self.change_stroke_color(color_hex)
            elif isinstance(item, QGraphicsTextItem):
                item.setDefaultTextColor(new_color)

    def add_text_item(self, pos):
        text, ok = QInputDialog.getText(
            self, "Add Text", "Enter your text:", QLineEdit.EchoMode.Normal
        )

        if ok and text:
            text_item = QGraphicsTextItem(text)

            # Cấu hình vị trí và thuộc tính
            text_item.setPos(pos)

            # QUAN TRỌNG: Nếu self.current_fill_color là 'transparent', chữ sẽ bị tàng hình.
            # Ta nên ưu tiên dùng màu trắng hoặc màu đã chọn nếu nó hợp lệ.
            color = QColor(self.current_fill_color)
            if self.current_fill_color == "transparent":
                color = QColor(
                    "#FFFFFF"
                )  # Mặc định chữ màu trắng nếu fill đang để trống

            text_item.setDefaultTextColor(color)
            text_item.setOpacity(self.current_opacity)

            # Bật tính năng tương tác
            text_item.setFlags(
                QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
                | QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            )

            # Đẩy vào Scene trước khi đẩy vào UndoStack (tùy vào cách bạn viết AddCommand)
            self.scene.addItem(text_item)

            # Đưa vào hệ thống Undo/Redo
            if hasattr(self, "undo_stack"):
                self.undo_stack.push(AddCommand(self.scene, text_item))
        """Mở hộp thoại nhập chữ và chèn vào canvas"""
        text, ok = QInputDialog.getText(
            self, "Add Text", "Enter your text:", QLineEdit.EchoMode.Normal
        )

        if ok and text:
            text_item = QGraphicsTextItem(text)
            text_item.setPos(pos)

            # Áp dụng màu sắc và độ trong suốt hiện tại
            text_item.setDefaultTextColor(QColor(self.current_fill_color))
            text_item.setOpacity(self.current_opacity)

            # Cho phép chọn và di chuyển
            text_item.setFlags(
                QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
                | QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            )

            # Đưa vào Undo Stack
            self.undo_stack.push(AddCommand(self.scene, text_item))

    def change_stroke_color(self, color):
        """Thay đổi màu viền (Stroke)"""
        self.current_stroke_color = color
        for item in self.scene.selectedItems():
            if hasattr(item, "pen"):
                pen = item.pen()
                pen.setColor(QColor(color))
                item.setPen(pen)
            elif isinstance(item, QGraphicsTextItem):
                item.setDefaultTextColor(QColor(color))

    def set_stroke_width(self, width):
        """Thay đổi độ dày viền (Width)"""
        self.current_stroke_width = width
        for item in self.scene.selectedItems():
            if hasattr(item, "pen"):
                pen = item.pen()
                pen.setWidth(width)
                item.setPen(pen)

    # --- CÁC HÀM ĐỊNH DẠNG TEXT ---

    def change_text_color(self, color_hex):
        for item in self.scene.selectedItems():
            if isinstance(item, QGraphicsTextItem):
                item.setDefaultTextColor(QColor(color_hex))

    def change_font_family(self, font):
        for item in self.scene.selectedItems():
            if isinstance(item, QGraphicsTextItem):
                f = item.font()
                f.setFamily(font.family())
                item.setFont(f)

    def change_font_size(self, size):
        for item in self.scene.selectedItems():
            if isinstance(item, QGraphicsTextItem):
                f = item.font()
                f.setPointSize(size)
                item.setFont(f)

    def toggle_font_style(self, style_type, is_checked):
        for item in self.scene.selectedItems():
            if isinstance(item, QGraphicsTextItem):
                f = item.font()
                if style_type == "bold":
                    f.setBold(is_checked)
                elif style_type == "italic":
                    f.setItalic(is_checked)
                elif style_type == "underline":
                    f.setUnderline(is_checked)
                elif style_type == "strike":
                    f.setStrikeOut(is_checked)
                item.setFont(f)

    def set_opacity(self, value):
        self.current_opacity = value / 100.0
        for item in self.scene.selectedItems():
            item.setOpacity(self.current_opacity)

    # --- Xử lý sự kiện chuột (VẼ HÌNH) ---
    def mousePressEvent(self, event):
        if self.mode == "select":
            super().mousePressEvent(event)
            return

        if event.button() == Qt.MouseButton.LeftButton:
            self.start_point = self.mapToScene(event.pos())

            # Khởi tạo item theo mode
            if self.mode == "rect":
                self.current_item = QGraphicsRectItem()
            elif self.mode == "ellipse":
                self.current_item = QGraphicsEllipseItem()
            elif self.mode == "line":
                self.current_item = QGraphicsLineItem()
            elif self.mode == "polygon":
                self.current_item = InteractivePolygonItem(QPolygonF())
            elif self.mode == "text":
                text_item = InteractiveTextItem()

                # Cài đặt màu chữ (Dùng màu Stroke hiện tại cho đồng bộ)
                text_item.setDefaultTextColor(QColor(self.current_stroke_color))

                # Cài đặt Font chữ mặc định
                font = QFont("Arial", 16)
                text_item.setFont(font)

                # Đặt vị trí Text đúng ngay mũi tên chuột
                text_item.setPos(self.start_point)
                self.scene.addItem(text_item)

                # Lưu vào Undo Stack
                self.undo_stack.push(AddCommand(self.scene, text_item))

                # Kích hoạt con trỏ nhấp nháy ngay lập tức
                text_item.setFocus()

                # Không gán vào self.current_item để chặn logic kéo thả (mouseMoveEvent)
                self.current_item = None
                return

            if self.current_item:
                # Áp dụng các thông số hiện tại cho item mới
                pen = QPen(QColor(self.current_stroke_color), self.current_stroke_width)
                self.current_item.setPen(pen)

                if not isinstance(self.current_item, QGraphicsLineItem):
                    self.current_item.setBrush(QBrush(QColor(self.current_fill_color)))

                self.current_item.setOpacity(self.current_opacity)
                self.current_item.setFlags(
                    QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
                    | QGraphicsItem.GraphicsItemFlag.ItemIsMovable
                )

    def mouseMoveEvent(self, event):
        if self.mode == "select":
            super().mouseMoveEvent(event)
            return

        if self.current_item and self.start_point:
            end_point = self.mapToScene(event.pos())
            if self.start_point == end_point:
                return

            if isinstance(self.current_item, QGraphicsLineItem):
                self.current_item.setLine(QLineF(self.start_point, end_point))
            elif isinstance(self.current_item, InteractivePolygonItem):
                # Vẽ tam giác mặc định dựa trên khung kéo chuột
                rect = QRectF(self.start_point, end_point).normalized()
                poly = QPolygonF()
                poly.append(QPointF(rect.center().x(), rect.top()))  # Đỉnh giữa trên
                poly.append(QPointF(rect.right(), rect.bottom()))  # Đỉnh phải dưới
                poly.append(QPointF(rect.left(), rect.bottom()))  # Đỉnh trái dưới
                self.current_item.setPolygon(poly)
            else:
                rect = QRectF(self.start_point, end_point).normalized()
                self.current_item.setRect(rect)

            # Hiển thị tạm thời trên scene khi đang kéo
            if self.current_item.scene() is None:
                self.scene.addItem(self.current_item)

    def mouseReleaseEvent(self, event):
        if self.current_item and self.mode != "select":
            # Xóa tạm thời để AddCommand quản lý việc đưa vào scene (hỗ trợ Undo)
            self.scene.removeItem(self.current_item)

            # Nếu là polygon mà nhấp nhả tại chỗ (không kéo) thì bỏ qua
            if (
                isinstance(self.current_item, InteractivePolygonItem)
                and self.current_item.polygon().isEmpty()
            ):
                self.current_item = None
            else:
                self.undo_stack.push(AddCommand(self.scene, self.current_item))
                self.current_item = None

        super().mouseReleaseEvent(event)

    def handle_selection_changed(self):
        selected_items = self.scene.selectedItems()

        # 1. Cập nhật "Ký ức" nội bộ của Canvas theo hình vừa click
        if len(selected_items) > 0:
            item = selected_items[0]

            if hasattr(item, "pen"):
                self.current_stroke_width = item.pen().width()
                c = item.pen().color()
                self.current_stroke_color = (
                    "transparent" if c.alpha() == 0 else c.name().upper()
                )

            if hasattr(item, "brush"):
                c = item.brush().color()
                self.current_fill_color = (
                    "transparent"
                    if c.alpha() == 0 or item.brush().style() == Qt.BrushStyle.NoBrush
                    else c.name().upper()
                )

            self.current_opacity = item.opacity()

        # 2. Gửi lệnh báo cho bảng Properties Panel cập nhật UI
        if hasattr(self, "properties_panel"):
            self.properties_panel.update_panel_state(selected_items)

    # --- DÁN LẠI HÀM ADD TEXT DUY NHẤT VÀ CHUẨN XÁC NÀY ---
    def add_text_item(self, pos):
        """Mở hộp thoại nhập chữ và chèn vào canvas"""
        text, ok = QInputDialog.getText(
            self, "Add Text", "Enter your text:", QLineEdit.EchoMode.Normal
        )

        if ok and text:
            text_item = InteractiveTextItem()  # Gọi class Text xịn mà bạn đã làm ở trên
            text_item.setPlainText(text)
            text_item.setPos(pos)

            # Ưu tiên màu trắng/đen nếu nền đang là transparent để chữ không bị tàng hình
            color_str = self.current_fill_color
            if color_str == "transparent":
                color_str = "#FFFFFF" if self.is_dark_theme else "#000000"

            text_item.setDefaultTextColor(QColor(color_str))
            text_item.setOpacity(self.current_opacity)

            # Cài đặt Font chữ mặc định
            font = QFont("Arial", 16)
            text_item.setFont(font)

            # Đưa vào Scene và Undo Stack
            self.scene.addItem(text_item)
            if hasattr(self, "undo_stack"):
                self.undo_stack.push(AddCommand(self.scene, text_item))

    def toggle_grid(self):
        """Bật/tắt trạng thái hiển thị lưới"""
        self.show_grid = not self.show_grid
        # Ép canvas vẽ lại toàn bộ nền
        self.viewport().update()

    def set_theme(self, is_dark):
        """Đổi theme cho canvas và ép vẽ lại"""
        self.is_dark_theme = is_dark
        self.viewport().update()

    def drawBackground(self, painter, rect):
        """Hàm ghi đè (override) để tự vẽ nền và lưới theo Theme"""
        # Xác định màu nền theo Theme
        bg_color = (
            QColor("#1E1E1E")
            if getattr(self, "is_dark_theme", True)
            else QColor("#F8F9FA")
        )

        # Đổ màu nền
        painter.fillRect(rect, bg_color)

        # Vẽ lưới nếu người dùng đang bật nút Grid
        if getattr(self, "show_grid", False):
            # Xác định màu nét lưới theo Theme
            grid_color = (
                QColor("#2A2A2A")
                if getattr(self, "is_dark_theme", True)
                else QColor("#E9ECEF")
            )
            pen = QPen(grid_color, 1)
            painter.setPen(pen)

            # Tính toán và vẽ lưới tọa độ
            left = int(math.floor(rect.left()))
            right = int(math.ceil(rect.right()))
            top = int(math.floor(rect.top()))
            bottom = int(math.ceil(rect.bottom()))

            first_left = left - (left % 20)
            first_top = top - (top % 20)

            for x in range(first_left, right, 20):
                painter.drawLine(x, top, x, bottom)

            for y in range(first_top, bottom, 20):
                painter.drawLine(left, y, right, y)
