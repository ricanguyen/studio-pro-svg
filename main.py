import sys
from PyQt6.QtWidgets import (QApplication, QFileDialog, QMainWindow, QPushButton, QWidget, 
                             QHBoxLayout, QVBoxLayout, QFrame, QLabel, QMenu, QMessageBox)
from PyQt6.QtGui import QIcon, QKeySequence, QShortcut, QUndoStack, QAction
from PyQt6.QtCore import Qt, QTimer

# Import các module đã được chia tách
from canvas.paint_canvas import PaintCanvas
from ui.widgets import Toolbar, PropertiesPanel, NotificationToast # Đã import Toast từ ui
from utils.file_handler import SVGHandler

class SVGPaintApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Studio Pro - SVG Paint")
        self.resize(1200, 800)
        self.setWindowIcon(QIcon("img/logo.png"))

        self.undo_stack = QUndoStack(self)
        self.current_file_path = None # Lưu đường dẫn file đang mở

        # Khởi tạo các Component
        self.canvas = PaintCanvas(self.undo_stack)
        self.toolbar = Toolbar(self.canvas)
        self.properties = PropertiesPanel(self.canvas)
        self.canvas.properties_panel = self.properties
        self.toast = NotificationToast(self)

        self._init_ui()
        self._setup_shortcuts()

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

        header = self._setup_header()
        center_layout.addWidget(header)
        center_layout.addWidget(self.canvas)

        main_layout.addWidget(self.toolbar)
        main_layout.addWidget(center_container, 1)
        main_layout.addWidget(self.properties)
    
    def resizeEvent(self, event):
        self.toast.move(self.width() - 140, self.height() - 60)
        super().resizeEvent(event)

    # ==========================================
    # LOGIC MENU & HEADER
    # ==========================================
    def _setup_header(self):
        header = QFrame()
        header.setFixedHeight(50)
        header.setObjectName("canvasHeader")
        header.setStyleSheet("background-color: #121212; border-bottom: 1px solid #2D2D2D;")
        
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(10, 0, 10, 0)
        
        title_label = QLabel("Studio Pro")
        title_label.setStyleSheet("color: white; font-weight: bold; font-size: 14px; border: none; margin-right: 20px;")
        h_layout.addWidget(title_label)
        
        for menu_name in ["File", "Edit", "View", "Object", "Window", "Help"]:
            btn = QPushButton(menu_name)
            btn.setObjectName("navButton")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            
            if menu_name == "File":
                file_menu = QMenu(self)
                file_menu.setStyleSheet("""
                    QMenu { background-color: #2A2A2A; color: #E0E0E0; border: 1px solid #444; padding: 5px 0px; }
                    QMenu::item { padding: 5px 30px 5px 20px; }
                    QMenu::item:selected { background-color: #4BBEFF; color: black; }
                    QMenu::separator { height: 1px; background-color: #444; margin: 4px 10px; }
                """)
                
                new_action = QAction("New", self)
                new_action.setShortcut("Ctrl+N")
                new_action.triggered.connect(self.new_file)
                
                open_action = QAction("Open SVG...", self)
                open_action.setShortcut("Ctrl+O")
                open_action.triggered.connect(self.open_file) # Chuyển qua gọi hàm open_file riêng
                
                save_action = QAction("Save", self)
                save_action.setShortcut("Ctrl+S")
                save_action.triggered.connect(self.save_file)

                export_action = QAction("Export SVG...", self)
                export_action.setShortcut("Ctrl+E")
                export_action.triggered.connect(lambda: SVGHandler.export_svg(self, self.canvas.scene))
                
                file_menu.addAction(new_action)
                file_menu.addSeparator()
                file_menu.addAction(open_action)
                file_menu.addAction(save_action)
                file_menu.addAction(export_action)
                
                btn.setMenu(file_menu)
                self.addAction(new_action)
                self.addAction(open_action)
                self.addAction(save_action)
                self.addAction(export_action)
            
            h_layout.addWidget(btn)
            
        h_layout.addStretch()
        return header

    def _setup_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+Z"), self).activated.connect(self.undo_stack.undo)
        QShortcut(QKeySequence("Ctrl+Y"), self).activated.connect(self.undo_stack.redo)
        QShortcut(QKeySequence("Delete"), self).activated.connect(self.canvas.delete_selected)

    # ==========================================
    # QUẢN LÝ LUỒNG FILE (NEW, OPEN, SAVE)
    # ==========================================
    def open_file(self):
        """Mở file và lưu lại đường dẫn để Ctrl+S hoạt động chuẩn"""
        path = SVGHandler.import_svg(self, self.canvas.scene)
        if path:
            self.current_file_path = path
            self.undo_stack.clear() # Mở file mới thì xóa lịch sử cũ
            self.undo_stack.setClean()

    def new_file(self):
        has_items = len(self.canvas.scene.items()) > 0
        is_saved = self.undo_stack.isClean()

        if has_items and not is_saved:
            reply = self._show_custom_msgbox(
                "Lưu thay đổi?",
                "Bản vẽ có sự thay đổi. Bạn có muốn lưu trước khi tạo trang mới không?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )
            if reply == QMessageBox.StandardButton.Yes:
                if self.current_file_path:
                    if SVGHandler.save_svg_to_path(self.canvas.scene, self.current_file_path):
                        self._reset_canvas()
                else:
                    path, _ = QFileDialog.getSaveFileName(self, "Save SVG", "", "SVG Files (*.svg)")
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
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
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
            path, _ = QFileDialog.getSaveFileName(self, "Save SVG", "", "SVG Files (*.svg)")
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
        self.canvas.scene.clear()
        self.undo_stack.clear()
        self.current_file_path = None
        if hasattr(self, 'properties'):
            self.properties.update_panel_state([])

    def _show_custom_msgbox(self, title, text, buttons):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        msg_box.setStandardButtons(buttons)
        msg_box.setStyleSheet("""
            QMessageBox { background-color: #2A2A2A; }
            QLabel { color: #E0E0E0; font-size: 13px; }
            QPushButton { background-color: #333333; color: white; border: 1px solid #555; padding: 6px 15px; border-radius: 4px; min-width: 60px; }
            QPushButton:hover { background-color: #4BBEFF; color: black; }
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