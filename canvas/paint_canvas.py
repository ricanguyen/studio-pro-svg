import math
from PyQt6.QtWidgets import (QGraphicsView, QGraphicsScene, QGraphicsRectItem, 
                             QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsItem,
                             QGraphicsPolygonItem)
from PyQt6.QtCore import Qt, QRectF, QLineF, QPointF
from PyQt6.QtGui import QPen, QColor, QBrush, QPolygonF
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
            min_dist = float('inf')
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

    def set_mode(self, mode):
        self.mode = mode
        # Chế độ select thì mới cho phép di chuyển/chọn item
        is_selectable = (mode == "select")
        for item in self.scene.items():
            item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, is_selectable)
            item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, is_selectable)

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
        self.current_fill_color = color_hex
        new_color = QColor(color_hex)
        for item in self.scene.selectedItems():
            if hasattr(item, 'setBrush') and not isinstance(item, QGraphicsLineItem):
                old_brush = item.brush()
                new_brush = QBrush(new_color)
                self.undo_stack.push(ColorCommand(item, old_brush, new_brush))
            elif isinstance(item, QGraphicsLineItem):
                self.change_stroke_color(color_hex)
                
    def change_stroke_color(self, color):
        self.current_stroke_color = color
        for item in self.scene.selectedItems():
            pen = item.pen()
            pen.setColor(QColor(color))
            item.setPen(pen)

    def set_stroke_width(self, width):
        self.current_stroke_width = width
        for item in self.scene.selectedItems():
            pen = item.pen()
            pen.setWidth(width)
            item.setPen(pen)

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
                self.current_item = InteractivePolygonItem(QPolygonF()) # Đa giác rỗng khởi đầu

            if self.current_item:
                # Áp dụng các thông số hiện tại cho item mới
                pen = QPen(QColor(self.current_stroke_color), self.current_stroke_width)
                self.current_item.setPen(pen)
                
                if not isinstance(self.current_item, QGraphicsLineItem):
                    self.current_item.setBrush(QBrush(QColor(self.current_fill_color)))
                
                self.current_item.setOpacity(self.current_opacity)
                self.current_item.setFlags(
                    QGraphicsItem.GraphicsItemFlag.ItemIsSelectable | 
                    QGraphicsItem.GraphicsItemFlag.ItemIsMovable
                )

    def mouseMoveEvent(self, event):
        if self.mode == "select":
            super().mouseMoveEvent(event)
            return

        if self.current_item and self.start_point:
            end_point = self.mapToScene(event.pos())
            
            if isinstance(self.current_item, QGraphicsLineItem):
                self.current_item.setLine(QLineF(self.start_point, end_point))
            elif isinstance(self.current_item, InteractivePolygonItem):
                # Vẽ tam giác mặc định dựa trên khung kéo chuột
                rect = QRectF(self.start_point, end_point).normalized()
                poly = QPolygonF()
                poly.append(QPointF(rect.center().x(), rect.top()))       # Đỉnh giữa trên
                poly.append(QPointF(rect.right(), rect.bottom()))         # Đỉnh phải dưới
                poly.append(QPointF(rect.left(), rect.bottom()))          # Đỉnh trái dưới
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
            if isinstance(self.current_item, InteractivePolygonItem) and self.current_item.polygon().isEmpty():
                self.current_item = None
            else:
                self.undo_stack.push(AddCommand(self.scene, self.current_item))
                self.current_item = None
        
        super().mouseReleaseEvent(event)

    def handle_selection_changed(self):
        selected_items = self.scene.selectedItems()
        if hasattr(self, 'properties_panel'):
            self.properties_panel.update_panel_state(selected_items)