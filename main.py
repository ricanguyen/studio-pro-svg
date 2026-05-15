import sys
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QMainWindow,
    QPushButton,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QFrame,
    QLabel,
    QMenu,
    QMessageBox,
)
from PyQt6.QtGui import QIcon, QKeySequence, QShortcut, QUndoStack, QAction
from PyQt6.QtCore import Qt, QTimer

# Import các module đã được chia tách
from canvas.paint_canvas import PaintCanvas
from ui.widgets import Toolbar, PropertiesPanel, NotificationToast
from utils.file_handler import SVGHandler


class SVGPaintApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Studio Pro - SVG Paint")
        self.resize(1200, 800)
        self.setWindowIcon(QIcon("img/logo.png"))

        self.undo_stack = QUndoStack(self)
        self.current_file_path = None
        self.is_dark = True  # Theo dõi Theme hiện tại

        # Khởi tạo các Component
        self.canvas = PaintCanvas(self.undo_stack)
        self.toolbar = Toolbar(self.canvas)
        self.properties = PropertiesPanel(self.canvas)
        self.canvas.properties_panel = self.properties
        self.toast = NotificationToast(self)

        self._init_ui()
        self._setup_shortcuts()

        # Cập nhật màu sắc ngay khi mở app
        self.apply_theme()

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        center_container = QWidget()
        center_layout = QVBoxLayout(center_container)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(0)

        self.header = self._setup_header()
        center_layout.addWidget(self.header)
        center_layout.addWidget(self.canvas)

        main_layout.addWidget(self.toolbar)
        main_layout.addWidget(center_container, 1)
        main_layout.addWidget(self.properties)

    def resizeEvent(self, event):
        self.toast.move(self.width() - 140, self.height() - 60)
        super().resizeEvent(event)

    # ==========================================
    # LOGIC MENU, HEADER & THEME
    # ==========================================
    def _setup_header(self):
        header = QFrame()
        header.setFixedHeight(50)
        header.setObjectName("canvasHeader")

        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(10, 0, 10, 0)

        self.title_label = QLabel("Studio Pro")
        h_layout.addWidget(self.title_label)

        for menu_name in ["File", "Edit"]:
            btn = QPushButton(menu_name)
            btn.setObjectName("navButton")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)

            # --- 1. MENU FILE
            if menu_name == "File":
                self.file_menu = QMenu(self)

                new_action = QAction("New", self)
                new_action.setShortcut("Ctrl+N")
                new_action.triggered.connect(self.new_file)

                open_action = QAction("Open SVG...", self)
                open_action.setShortcut("Ctrl+O")
                open_action.triggered.connect(self.open_file)

                save_action = QAction("Save", self)
                save_action.setShortcut("Ctrl+S")
                save_action.triggered.connect(self.save_file)

                export_action = QAction("Export SVG...", self)
                export_action.setShortcut("Ctrl+E")
                export_action.triggered.connect(
                    lambda: SVGHandler.export_svg(self, self.canvas.scene)
                )

                self.file_menu.addAction(new_action)
                self.file_menu.addSeparator()
                self.file_menu.addAction(open_action)
                self.file_menu.addAction(save_action)
                self.file_menu.addAction(export_action)

                btn.setMenu(self.file_menu)
                self.addAction(new_action)
                self.addAction(open_action)
                self.addAction(save_action)
                self.addAction(export_action)
            # --- 2. MENU EDIT (ĐOẠN CẦN THÊM MỚI) ---
            elif menu_name == "Edit":
                self.edit_menu = QMenu(self)

                # Tính năng Undo
                undo_action = QAction("Undo", self)
                undo_action.setShortcut("Ctrl+Z")
                undo_action.triggered.connect(self.undo_stack.undo)
                self.edit_menu.addAction(undo_action)

                # Tính năng Redo
                redo_action = QAction("Redo", self)
                redo_action.setShortcut("Ctrl+Y")
                redo_action.triggered.connect(self.undo_stack.redo)
                self.edit_menu.addAction(redo_action)

                # Gắn menu vào nút
                btn.setMenu(self.edit_menu)
            # ----------------------------------------
            h_layout.addWidget(btn)

        h_layout.addStretch()

        # NÚT TOGGLE THEME
        self.btn_theme = QPushButton("☀️ Light")
        self.btn_theme.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_theme.setFixedSize(80, 30)
        self.btn_theme.clicked.connect(self.toggle_theme)
        h_layout.addWidget(self.btn_theme)

        return header

    def _setup_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+Z"), self).activated.connect(self.undo_stack.undo)
        QShortcut(QKeySequence("Ctrl+Y"), self).activated.connect(self.undo_stack.redo)
        QShortcut(QKeySequence("Delete"), self).activated.connect(
            self.canvas.delete_selected
        )

    def toggle_theme(self):
        self.is_dark = not self.is_dark
        self.apply_theme()

    def apply_theme(self):
        """Nhạc trưởng điều phối thay đổi màu sắc toàn bộ ứng dụng"""
        self.canvas.set_theme(self.is_dark)
        self.toolbar.set_theme(self.is_dark)
        self.properties.set_theme(self.is_dark)

        # 2. Xử lý màu cho Header và Menu (Đoạn code bạn đã làm)
        if self.is_dark:
            self.header.setStyleSheet("""
                QFrame#canvasHeader { background-color: #121212; border-bottom: 1px solid #2D2D2D; }
                QPushButton#navButton { color: #E0E0E0; background: "transparent"; border: none; padding: 5px 12px; }
                QPushButton#navButton:hover { background-color: #333333; color: #FFFFFF; border-radius: 4px; }
            """)
            self.title_label.setStyleSheet(
                "color: white; font-weight: bold; font-size: 14px;"
            )
            self.btn_theme.setText("☀️ Light")
            self.btn_theme.setStyleSheet(
                "background-color: #333; color: white; border-radius: 4px; border: 1px solid #555;"
            )
        else:
            self.header.setStyleSheet("""
                QFrame#canvasHeader { background-color: #F8F9FA; border-bottom: 1px solid #DDDDDD; }
                QPushButton#navButton { color: #333333; background: transparent; border: none; padding: 5px 12px; }
                QPushButton#navButton:hover { background-color: #E9ECEF; color: #000000; border-radius: 4px; }
            """)
            self.title_label.setStyleSheet(
                "color: #333333; font-weight: bold; font-size: 14px;"
            )
            self.btn_theme.setText("🌙 Dark")
            self.btn_theme.setStyleSheet(
                "background-color: #F0F0F0; color: #333; border-radius: 4px; border: 1px solid #CCC;"
            )

    # ==========================================
    # QUẢN LÝ LUỒNG FILE (NEW, OPEN, SAVE)
    # ==========================================
    def open_file(self):
        path = SVGHandler.import_svg(self, self.canvas.scene)
        if path:
            self.current_file_path = path
            self.undo_stack.clear()
            self.undo_stack.setClean()

            # --- RESET TRẠNG THÁI SAU KHI MỞ FILE ---
            self.canvas.scene.clearSelection()
            self.canvas.reset_default_tools()
            # Ép thanh công cụ bên trái quay về nút Select (chuột)
            for btn in self.toolbar.group.buttons():
                if btn.toolTip().startswith("Select"):
                    btn.setChecked(True)
                    self.canvas.set_mode("select")
                    break

    def new_file(self):
        has_items = len(self.canvas.scene.items()) > 0
        is_saved = self.undo_stack.isClean()

        if has_items and not is_saved:
            reply = self._show_custom_msgbox(
                "Lưu thay đổi?",
                "Bản vẽ có sự thay đổi. Bạn có muốn lưu trước khi tạo trang mới không?",
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No
                | QMessageBox.StandardButton.Cancel,
            )
            if reply == QMessageBox.StandardButton.Yes:
                if self.current_file_path:
                    if SVGHandler.save_svg_to_path(
                        self.canvas.scene, self.current_file_path
                    ):
                        self._reset_canvas()
                else:
                    path, _ = QFileDialog.getSaveFileName(
                        self, "Save SVG", "", "SVG Files (*.svg)"
                    )
                    if path:
                        self.current_file_path = path
                        if SVGHandler.save_svg_to_path(self.canvas.scene, path):
                            self._reset_canvas()
            elif reply == QMessageBox.StandardButton.No:
                self._reset_canvas()

        elif has_items and is_saved:
            reply = self._show_custom_msgbox(
                "Đóng file?",
                "Tác phẩm đã được lưu. Bạn có chắc muốn đóng file hiện tại để tạo trang trắng không?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                self._reset_canvas()
        else:
            self._reset_canvas()

    def save_file(self):
        if self.current_file_path:
            self.toast.show_message("Đang lưu...", "⏳", 3000)
            QTimer.singleShot(500, self._execute_save)
        else:
            path, _ = QFileDialog.getSaveFileName(
                self, "Save SVG", "", "SVG Files (*.svg)"
            )
            if path:
                self.current_file_path = path
                self._execute_save()

    def _execute_save(self):
        success = SVGHandler.save_svg_to_path(self.canvas.scene, self.current_file_path)
        if success:
            self.undo_stack.setClean()
            self.toast.show_message("Đã lưu", "✅")
        else:
            self.toast.show_message("Lỗi!", "❌")

    def _reset_canvas(self):
        """Hàm phụ trợ dọn dẹp sạch sẽ Canvas và Tools"""
        self.canvas.scene.clear()
        self.undo_stack.clear()
        self.current_file_path = None

        # --- RESET TRẠNG THÁI KHI TẠO FILE MỚI ---
        self.canvas.reset_default_tools()
        # Ép thanh công cụ bên trái quay về nút Select (chuột)
        for btn in self.toolbar.group.buttons():
            if btn.toolTip().startswith("Select"):
                btn.setChecked(True)
                self.canvas.set_mode("select")
                break

        if hasattr(self, "properties"):
            self.properties.update_panel_state([])

    def _show_custom_msgbox(self, title, text, buttons):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        msg_box.setStandardButtons(buttons)

        if self.is_dark:
            msg_box.setStyleSheet("""
                QMessageBox { background-color: #2A2A2A; }
                QLabel { color: #E0E0E0; font-size: 13px; }
                QPushButton { background-color: #333333; color: white; border: 1px solid #555; padding: 6px 15px; border-radius: 4px; min-width: 60px;}
                QPushButton:hover { background-color: #4BBEFF; color: black; }
            """)
        else:
            msg_box.setStyleSheet("""
                QMessageBox { background-color: #F8F9FA; }
                QLabel { color: #333333; font-size: 13px; }
                QPushButton { background-color: #FFFFFF; color: #333; border: 1px solid #CCC; padding: 6px 15px; border-radius: 4px; min-width: 60px;}
                QPushButton:hover { background-color: #4BBEFF; color: white; }
            """)
        return msg_box.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    try:
        with open("styles.qss", "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print("Cảnh báo: Không tìm thấy file styles.qss")

    window = SVGPaintApp()
    window.show()
    sys.exit(app.exec())
