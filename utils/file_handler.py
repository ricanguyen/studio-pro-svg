from PyQt6.QtWidgets import QFileDialog, QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsLineItem
from PyQt6.QtCore import Qt

class SVGHandler:
    @staticmethod
    def export_svg(parent, scene):
        """Hàm xuất dữ liệu từ GraphicsScene ra file .svg"""
        file_path, _ = QFileDialog.getSaveFileName(
            parent, "Export SVG", "", "SVG Files (*.svg)"
        )
        
        if not file_path:
            return

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                # Khởi tạo thẻ svg chuẩn
                f.write('<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n')
                f.write('<svg width="800" height="600" xmlns="http://www.w3.org/2000/svg">\n')
                
                # Vẽ nền (optional)
                f.write('  <rect width="100%" height="100%" fill="#1E1E1E"/>\n')
                
                # Duyệt qua các item theo thứ tự từ dưới lên trên (Ascending)
                for item in scene.items(Qt.SortOrder.AscendingOrder):
                    pen_color = item.pen().color().name()
                    stroke_w = item.pen().width()
                    
                    if isinstance(item, QGraphicsRectItem):
                        r = item.rect()
                        fill = item.brush().color().name()
                        f.write(f'  <rect x="{r.x()}" y="{r.y()}" width="{r.width()}" height="{r.height()}" '
                                f'fill="{fill}" stroke="{pen_color}" stroke-width="{stroke_w}"/>\n')
                    
                    elif isinstance(item, QGraphicsEllipseItem):
                        r = item.rect()
                        fill = item.brush().color().name()
                        cx, cy = r.x() + r.width()/2, r.y() + r.height()/2
                        rx, ry = r.width()/2, r.height()/2
                        f.write(f'  <ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" '
                                f'fill="{fill}" stroke="{pen_color}" stroke-width="{stroke_w}"/>\n')
                    
                    elif isinstance(item, QGraphicsLineItem):
                        l = item.line()
                        f.write(f'  <line x1="{l.x1()}" y1="{l.y1()}" x2="{l.x2()}" y2="{l.y2()}" '
                                f'stroke="{pen_color}" stroke-width="{stroke_w}"/>\n')
                
                f.write('</svg>')
            print(f"Successfully exported to {file_path}")
        except Exception as e:
            print(f"Error exporting SVG: {e}")