import xml.etree.ElementTree as ET
from PyQt6.QtWidgets import (
    QFileDialog,
    QGraphicsRectItem,
    QGraphicsEllipseItem,
    QGraphicsLineItem,
    QGraphicsTextItem,
    QGraphicsPolygonItem,
    QGraphicsItem,
)  # Thêm QGraphicsItem
from PyQt6.QtCore import Qt, QPointF  # Thêm QPointF
from PyQt6.QtSvgWidgets import QGraphicsSvgItem
from PyQt6.QtGui import (
    QPainterPath,
    QPen,
    QColor,
    QBrush,
    QPolygonF,
)  # Thêm cụm quản lý màu và đa giác này
import re


class SVGHandler:
    @staticmethod
    def parse_svg_path_data(d_string):
        """Hàm dịch chuỗi lệnh 'd' của path thành QPainterPath (Hỗ trợ Tọa độ Tương đối & Tuyệt đối)"""
        path = QPainterPath()
        if not d_string:
            return path

        # Regex thông minh bắt được số âm, số thập phân và lệnh (Ví dụ: M, -10.5, 20)
        tokens = re.findall(r"[A-Za-z]|[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", d_string)

        i = 0
        cmd = ""
        current_x, current_y = 0.0, 0.0  # Bút vẽ đang đứng ở đâu

        while i < len(tokens):
            # 1. Đọc lệnh (Nếu là chữ cái)
            if tokens[i].isalpha():
                cmd = tokens[i]
                i += 1

            if i >= len(tokens):
                break

            # Kiểm tra xem lệnh này là tương đối (chữ thường) hay tuyệt đối (chữ hoa)
            is_relative = cmd.islower()

            # 2. Xử lý Di chuyển bút (Move)
            if cmd in ["M", "m"]:
                x, y = float(tokens[i]), float(tokens[i + 1])
                if is_relative:
                    x += current_x
                    y += current_y
                path.moveTo(x, y)
                current_x, current_y = x, y
                i += 2
                # SVG Rule: Sau chữ M, nếu có thêm tọa độ thì mặc định nó hiểu là kẻ đường thẳng (L hoặc l)
                cmd = "l" if is_relative else "L"

            # 3. Xử lý Kẻ đường thẳng (Line)
            elif cmd in ["L", "l"]:
                x, y = float(tokens[i]), float(tokens[i + 1])
                if is_relative:
                    x += current_x
                    y += current_y
                path.lineTo(x, y)
                current_x, current_y = x, y
                i += 2

            # 4. Xử lý Đường ngang (Horizontal Line) - Rất hay gặp trong SVG
            elif cmd in ["H", "h"]:
                x = float(tokens[i])
                if is_relative:
                    x += current_x
                path.lineTo(x, current_y)
                current_x = x
                i += 1

            # 5. Xử lý Đường dọc (Vertical Line)
            elif cmd in ["V", "v"]:
                y = float(tokens[i])
                if is_relative:
                    y += current_y
                path.lineTo(current_x, y)
                current_y = y
                i += 1

            # 6. Xử lý Đường cong (Cubic Bezier)
            elif cmd in ["C", "c"]:
                x1, y1 = float(tokens[i]), float(tokens[i + 1])
                x2, y2 = float(tokens[i + 2]), float(tokens[i + 3])
                x, y = float(tokens[i + 4]), float(tokens[i + 5])
                if is_relative:
                    x1 += current_x
                    y1 += current_y
                    x2 += current_x
                    y2 += current_y
                    x += current_x
                    y += current_y
                path.cubicTo(x1, y1, x2, y2, x, y)
                current_x, current_y = x, y
                i += 6

            # 7. Xử lý Đóng hình (Close)
            elif cmd in ["Z", "z"]:
                path.closeSubpath()
                cmd = ""

            else:
                # Bỏ qua các tọa độ của các lệnh phức tạp chưa support (như S, Q, A) để không bị lỗi treo
                i += 1

        return path

    @staticmethod
    def export_svg(parent_widget, scene):
        file_path, _ = QFileDialog.getSaveFileName(
            parent_widget, "Export SVG", "", "SVG Files (*.svg)"
        )
        if not file_path:
            return False

        try:
            # 1. Khởi tạo thẻ <svg> gốc
            rect = scene.sceneRect()
            width, height = int(rect.width()), int(rect.height())

            svg = ET.Element(
                "svg",
                xmlns="http://www.w3.org/2000/svg",
                version="1.1",
                width=str(width),
                height=str(height),
            )

            # 2. Duyệt qua TẤT CẢ các item trên bảng vẽ (đảo ngược để layer dưới cùng vẽ trước)
            for item in reversed(scene.items()):

                # --- A. NẾU LÀ TEXT ---
                if isinstance(item, QGraphicsTextItem):
                    text_el = ET.SubElement(svg, "text")
                    text_el.text = item.toPlainText()

                    # Tọa độ Text (phải cộng thêm pointSize vì SVG tính từ đường baseline của chữ)
                    pos = item.scenePos()
                    text_el.set("x", str(pos.x()))
                    text_el.set("y", str(pos.y() + item.font().pointSize()))

                    # Style của chữ
                    text_el.set("fill", item.defaultTextColor().name())
                    text_el.set("font-family", item.font().family())
                    text_el.set("font-size", f"{item.font().pointSize()}px")

                    styles = []
                    if item.font().bold():
                        styles.append("font-weight:bold")
                    if item.font().italic():
                        styles.append("font-style:italic")
                    if item.font().underline():
                        styles.append("text-decoration:underline")
                    if item.font().strikeOut():
                        styles.append("text-decoration:line-through")
                    if styles:
                        text_el.set("style", ";".join(styles))

                    text_el.set("opacity", str(item.opacity()))
                    continue

                # --- B. CÁC HÌNH KHỐI (SHAPE) ---
                if not hasattr(item, "pen"):
                    continue  # Bỏ qua các item rác không có nét vẽ

                pen = item.pen()
                stroke = pen.color().name()
                stroke_width = str(pen.width())
                opacity = str(item.opacity())

                # Lấy màu Fill (Nếu là no brush/transparent thì để none)
                fill = "none"
                if hasattr(item, "brush"):
                    brush = item.brush()
                    if (
                        brush.style() != Qt.BrushStyle.NoBrush
                        and brush.color().alpha() > 0
                    ):
                        fill = brush.color().name()

                pos = item.scenePos()

                # B.1 HÌNH CHỮ NHẬT
                if isinstance(item, QGraphicsRectItem):
                    r = item.rect()
                    ET.SubElement(
                        svg,
                        "rect",
                        x=str(r.x() + pos.x()),
                        y=str(r.y() + pos.y()),
                        width=str(r.width()),
                        height=str(r.height()),
                        fill=fill,
                        stroke=stroke,
                        **{"stroke-width": stroke_width},
                        opacity=opacity,
                    )

                # B.2 HÌNH TRÒN / ELIP
                elif isinstance(item, QGraphicsEllipseItem):
                    r = item.rect()
                    cx = r.x() + pos.x() + r.width() / 2
                    cy = r.y() + pos.y() + r.height() / 2
                    rx = r.width() / 2
                    ry = r.height() / 2
                    ET.SubElement(
                        svg,
                        "ellipse",
                        cx=str(cx),
                        cy=str(cy),
                        rx=str(rx),
                        ry=str(ry),
                        fill=fill,
                        stroke=stroke,
                        **{"stroke-width": stroke_width},
                        opacity=opacity,
                    )

                # B.3 ĐƯỜNG THẲNG
                elif isinstance(item, QGraphicsLineItem):
                    line = item.line()
                    ET.SubElement(
                        svg,
                        "line",
                        x1=str(line.x1() + pos.x()),
                        y1=str(line.y1() + pos.y()),
                        x2=str(line.x2() + pos.x()),
                        y2=str(line.y2() + pos.y()),
                        stroke=stroke,
                        **{"stroke-width": stroke_width},
                        opacity=opacity,
                    )

                # B.4 ĐA GIÁC (POLYGON)
                elif isinstance(item, QGraphicsPolygonItem):
                    poly = item.polygon()
                    # Nối tất cả các đỉnh x,y lại thành 1 chuỗi string cho SVG
                    points_str = " ".join(
                        [f"{p.x() + pos.x()},{p.y() + pos.y()}" for p in poly]
                    )
                    if points_str:
                        ET.SubElement(
                            svg,
                            "polygon",
                            points=points_str,
                            fill=fill,
                            stroke=stroke,
                            **{"stroke-width": stroke_width},
                            opacity=opacity,
                        )

            # 3. Định dạng XML đẹp đẽ và lưu ra file
            tree = ET.ElementTree(svg)
            if hasattr(ET, "indent"):
                ET.indent(tree, space="  ", level=0)  # Cho file code thụt lề dễ nhìn

            tree.write(file_path, encoding="utf-8", xml_declaration=True)
            print(f"Exported successfully to {file_path}")
            return True
        except Exception as e:
            print(f"Error exporting SVG: {e}")
            return False

    @staticmethod
    def import_svg(parent_widget, scene):
        file_path, _ = QFileDialog.getOpenFileName(
            parent_widget, "Open SVG", "", "SVG Files (*.svg)"
        )
        if not file_path:
            return None

        try:
            tree = ET.parse(file_path)
            root = tree.getroot()

            # Xóa sạch bản vẽ cũ trước khi mở bản vẽ mới
            scene.clear()

            # Lấy namespace (thường là http://www.w3.org/2000/svg)
            ns = {"svg": "http://www.w3.org/2000/svg"}

            # Duyệt qua các thẻ con trong SVG
            for elem in root:
                tag = elem.tag.split("}")[-1]  # Loại bỏ namespace nếu có

                item = None
                print(tag)
                # 1. Đọc Hình chữ nhật
                if tag == "rect":
                    if elem.get("width") == "100%":
                        continue  # Bỏ qua rect làm background
                    item = QGraphicsRectItem(
                        0, 0, float(elem.get("width")), float(elem.get("height"))
                    )
                    item.setPos(float(elem.get("x", 0)), float(elem.get("y", 0)))

                # 2. Đọc Hình Elip
                elif tag == "ellipse":
                    rx, ry = float(elem.get("rx")), float(elem.get("ry"))
                    cx, cy = float(elem.get("cx")), float(elem.get("cy"))
                    item = QGraphicsEllipseItem(0, 0, rx * 2, ry * 2)
                    item.setPos(cx - rx, cy - ry)

                # 3. Đọc Đường thẳng
                elif tag == "line":
                    x1, y1 = float(elem.get("x1")), float(elem.get("y1"))
                    x2, y2 = float(elem.get("x2")), float(elem.get("y2"))
                    item = QGraphicsLineItem(x1, y1, x2, y2)

                # 4. Đọc Văn bản
                elif tag == "text":
                    from canvas.paint_canvas import (
                        InteractiveTextItem,
                    )  # Import tại chỗ để tránh vòng lặp

                    item = InteractiveTextItem()
                    item.setPlainText(elem.text if elem.text else "")
                    item.setPos(
                        float(elem.get("x", 0)),
                        float(elem.get("y", 0))
                        - float(elem.get("font-size", "16").replace("px", "")),
                    )
                    item.setDefaultTextColor(QColor(elem.get("fill", "#FFFFFF")))

                # 5. Đọc Đa giác (Polygon)
                elif tag == "polygon":
                    from canvas.paint_canvas import InteractivePolygonItem

                    points_str = elem.get("points", "")
                    poly = QPolygonF()
                    for p in points_str.split():
                        x, y = map(float, p.split(","))
                        poly.append(QPointF(x, y))
                    item = InteractivePolygonItem(poly)
                elif tag == "path":
                    from PyQt6.QtWidgets import QGraphicsPathItem

                    d_data = elem.get("d", "")
                    painter_path = SVGHandler.parse_svg_path_data(d_data)
                    item = QGraphicsPathItem(painter_path)
                # --- Áp dụng Style chung ---
                if item:
                    # Nét vẽ (Stroke)
                    if hasattr(item, "setPen"):
                        stroke = elem.get("stroke", "#FFFFFF")
                        width = float(elem.get("stroke-width", 2))
                        item.setPen(QPen(QColor(stroke), width))

                    # Màu nền (Fill)
                    if hasattr(item, "setBrush"):
                        fill = elem.get("fill", "none")
                        if fill != "none":
                            item.setBrush(QBrush(QColor(fill)))

                    item.setOpacity(float(elem.get("opacity", 1.0)))
                    item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
                    item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
                    scene.addItem(item)

            print("Imported successfully!")
            return file_path
        except Exception as e:
            print(f"Error importing SVG: {e}")
            return None

    @staticmethod
    def save_svg_to_path(scene, file_path):
        """Hàm lưu file trực tiếp vào đường dẫn có sẵn"""
        try:
            rect = scene.sceneRect()
            width, height = int(rect.width()), int(rect.height())
            svg = ET.Element(
                "svg",
                xmlns="http://www.w3.org/2000/svg",
                version="1.1",
                width=str(width),
                height=str(height),
            )

            # (Phần logic duyệt item để tạo SVG giữ nguyên như hàm export_svg)
            for item in reversed(scene.items()):

                # --- A. NẾU LÀ TEXT ---
                if isinstance(item, QGraphicsTextItem):
                    text_el = ET.SubElement(svg, "text")
                    text_el.text = item.toPlainText()

                    # Tọa độ Text (phải cộng thêm pointSize vì SVG tính từ đường baseline của chữ)
                    pos = item.scenePos()
                    text_el.set("x", str(pos.x()))
                    text_el.set("y", str(pos.y() + item.font().pointSize()))

                    # Style của chữ
                    text_el.set("fill", item.defaultTextColor().name())
                    text_el.set("font-family", item.font().family())
                    text_el.set("font-size", f"{item.font().pointSize()}px")

                    styles = []
                    if item.font().bold():
                        styles.append("font-weight:bold")
                    if item.font().italic():
                        styles.append("font-style:italic")
                    if item.font().underline():
                        styles.append("text-decoration:underline")
                    if item.font().strikeOut():
                        styles.append("text-decoration:line-through")
                    if styles:
                        text_el.set("style", ";".join(styles))

                    text_el.set("opacity", str(item.opacity()))
                    continue

                # --- B. CÁC HÌNH KHỐI (SHAPE) ---
                if not hasattr(item, "pen"):
                    continue  # Bỏ qua các item rác không có nét vẽ

                pen = item.pen()
                stroke = pen.color().name()
                stroke_width = str(pen.width())
                opacity = str(item.opacity())

                # Lấy màu Fill (Nếu là no brush/transparent thì để none)
                fill = "none"
                if hasattr(item, "brush"):
                    brush = item.brush()
                    if (
                        brush.style() != Qt.BrushStyle.NoBrush
                        and brush.color().alpha() > 0
                    ):
                        fill = brush.color().name()

                pos = item.scenePos()

                # B.1 HÌNH CHỮ NHẬT
                if isinstance(item, QGraphicsRectItem):
                    r = item.rect()
                    ET.SubElement(
                        svg,
                        "rect",
                        x=str(r.x() + pos.x()),
                        y=str(r.y() + pos.y()),
                        width=str(r.width()),
                        height=str(r.height()),
                        fill=fill,
                        stroke=stroke,
                        **{"stroke-width": stroke_width},
                        opacity=opacity,
                    )

                # B.2 HÌNH TRÒN / ELIP
                elif isinstance(item, QGraphicsEllipseItem):
                    r = item.rect()
                    cx = r.x() + pos.x() + r.width() / 2
                    cy = r.y() + pos.y() + r.height() / 2
                    rx = r.width() / 2
                    ry = r.height() / 2
                    ET.SubElement(
                        svg,
                        "ellipse",
                        cx=str(cx),
                        cy=str(cy),
                        rx=str(rx),
                        ry=str(ry),
                        fill=fill,
                        stroke=stroke,
                        **{"stroke-width": stroke_width},
                        opacity=opacity,
                    )

                # B.3 ĐƯỜNG THẲNG
                elif isinstance(item, QGraphicsLineItem):
                    line = item.line()
                    ET.SubElement(
                        svg,
                        "line",
                        x1=str(line.x1() + pos.x()),
                        y1=str(line.y1() + pos.y()),
                        x2=str(line.x2() + pos.x()),
                        y2=str(line.y2() + pos.y()),
                        stroke=stroke,
                        **{"stroke-width": stroke_width},
                        opacity=opacity,
                    )

                # B.4 ĐA GIÁC (POLYGON)
                elif isinstance(item, QGraphicsPolygonItem):
                    poly = item.polygon()
                    # Nối tất cả các đỉnh x,y lại thành 1 chuỗi string cho SVG
                    points_str = " ".join(
                        [f"{p.x() + pos.x()},{p.y() + pos.y()}" for p in poly]
                    )
                    if points_str:
                        ET.SubElement(
                            svg,
                            "polygon",
                            points=points_str,
                            fill=fill,
                            stroke=stroke,
                            **{"stroke-width": stroke_width},
                            opacity=opacity,
                        )

            tree = ET.ElementTree(svg)
            if hasattr(ET, "indent"):
                ET.indent(tree, space="  ", level=0)
            tree.write(file_path, encoding="utf-8", xml_declaration=True)
            return True
        except Exception as e:
            print(f"Error saving SVG: {e}")
            return False
