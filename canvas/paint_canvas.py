from PyQt6.QtWidgets import (QGraphicsView, QGraphicsScene, QGraphicsRectItem, 
                             QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsItem)
from PyQt6.QtCore import Qt, QRectF, QLineF
from PyQt6.QtGui import QPen, QColor, QBrush
from models.commands import AddCommand, DeleteCommand, ColorCommand

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
        """Thay đổi màu nền (Fill)"""
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
        """Thay đổi màu viền"""
        self.current_stroke_color = color
        for item in self.scene.selectedItems():
            pen = item.pen()
            pen.setColor(QColor(color))
            item.setPen(pen)

    def set_stroke_width(self, width):
        """Thay đổi độ dày viền"""
        self.current_stroke_width = width
        for item in self.scene.selectedItems():
            pen = item.pen()
            pen.setWidth(width)
            item.setPen(pen)

    def set_opacity(self, value):
        """Thay đổi độ trong suốt (0.0 - 1.0)"""
        self.current_opacity = value / 100.0
        for item in self.scene.selectedItems():
            item.setOpacity(self.current_opacity)

    # --- Xử lý sự kiện chuột ---

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
            self.undo_stack.push(AddCommand(self.scene, self.current_item))
            self.current_item = None
        
        super().mouseReleaseEvent(event)

    def handle_selection_changed(self):
        selected_items = self.scene.selectedItems()
        # Cập nhật panel thuộc tính nếu có
        if hasattr(self, 'properties_panel'):
            self.properties_panel.update_panel_state(selected_items)