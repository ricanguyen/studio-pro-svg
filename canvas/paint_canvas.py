from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsItem
from PyQt6.QtCore import Qt, QRectF, QLineF
from PyQt6.QtGui import QPen, QColor, QBrush
from models.commands import AddCommand, DeleteCommand, ColorCommand

class PaintCanvas(QGraphicsView):
    def __init__(self, undo_stack):
        super().__init__()
        self.undo_stack = undo_stack
        self.scene = QGraphicsScene(0, 0, 800, 600)
        self.setScene(self.scene)
        self.setBackgroundBrush(QBrush(QColor("#1E1E1E")))
        self.mode = "select"
        self.current_item = None
        self.start_point = None

    def set_mode(self, mode):
        self.mode = mode
        for item in self.scene.items():
            item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, mode == "select")
            item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, mode == "select")

    def clear_all(self):
        all_items = [item for item in self.scene.items() if item.scene() == self.scene]
        if all_items:
            self.undo_stack.push(DeleteCommand(self.scene, all_items, "Clear All"))

    def delete_selected(self):
        items = self.scene.selectedItems()
        if items:
            self.undo_stack.push(DeleteCommand(self.scene, items))

    def change_color(self, color_hex):
        for item in self.scene.selectedItems():
            if hasattr(item, 'setBrush') and not isinstance(item, QGraphicsLineItem):
                self.undo_stack.push(ColorCommand(item, item.brush(), QBrush(QColor(color_hex))))
            elif isinstance(item, QGraphicsLineItem):
                pen = item.pen()
                pen.setColor(QColor(color_hex))
                item.setPen(pen)

    def mousePressEvent(self, event):
        if self.mode == "select": super().mousePressEvent(event)
        elif event.button() == Qt.MouseButton.LeftButton:
            self.start_point = self.mapToScene(event.pos())
            pen = QPen(QColor("#4BBEFF"), 2)
            if self.mode == "rect": self.current_item = QGraphicsRectItem()
            elif self.mode == "ellipse": self.current_item = QGraphicsEllipseItem()
            elif self.mode == "line": self.current_item = QGraphicsLineItem()
            if self.current_item:
                self.current_item.setPen(pen)
                self.current_item.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable | QGraphicsItem.GraphicsItemFlag.ItemIsMovable)

    def mouseMoveEvent(self, event):
        if self.mode == "select": super().mouseMoveEvent(event)
        elif self.current_item and self.start_point:
            end_point = self.mapToScene(event.pos())
            if isinstance(self.current_item, QGraphicsLineItem):
                self.current_item.setLine(QLineF(self.start_point, end_point))
            else:
                self.current_item.setRect(QRectF(self.start_point, end_point).normalized())
            if self.current_item.scene() is None: self.scene.addItem(self.current_item)

    def mouseReleaseEvent(self, event):
        if self.current_item and self.mode != "select":
            self.scene.removeItem(self.current_item)
            self.undo_stack.push(AddCommand(self.scene, self.current_item))
        super().mouseReleaseEvent(event)
        self.current_item = None