from PyQt6.QtGui import QUndoCommand

class AddCommand(QUndoCommand):
    def __init__(self, scene, item):
        super().__init__("Add Item")
        self.scene = scene
        self.item = item

    def redo(self):
        if self.item.scene() is None:
            self.scene.addItem(self.item)

    def undo(self):
        self.scene.removeItem(self.item)

class DeleteCommand(QUndoCommand):
    def __init__(self, scene, items, description="Delete"):
        super().__init__(description); self.scene = scene; self.items = items
    def undo(self): 
        for item in self.items: self.scene.addItem(item)
    def redo(self): 
        for item in self.items: self.scene.removeItem(item)

class ColorCommand(QUndoCommand):
    def __init__(self, item, old_brush, new_brush):
        super().__init__(); self.item = item; self.old_brush = old_brush; self.new_brush = new_brush
    def undo(self): self.item.setBrush(self.old_brush)
    def redo(self): self.item.setBrush(self.new_brush)