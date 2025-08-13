import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtCore import Qt, QSize

class SubWindow(QWidget):
    def __init__(self, color, parent=None):
        super().__init__(parent)
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)

        self.label = QLabel(f"Subwindow ({color})", self)
        self.label.setAlignment(Qt.AlignCenter)

    def resizeEvent(self, event):
        # Center the label inside this subwindow
        self.label.resize(self.width(), self.height())
        super().resizeEvent(event)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Window with 3 Resizable Subwindows")
        self.resize(800, 400)

        # Create 3 subwindows with different colors
        self.sub1 = SubWindow("lightblue", self)
        self.sub2 = SubWindow("lightgreen", self)
        self.sub3 = SubWindow("lightcoral", self)

    def resizeEvent(self, event):
        width = self.width()
        height = self.height()

        # Divide window into three vertical panels (equal width)
        margin = 10
        spacing = 10
        sub_width = (width - 4 * spacing) // 3
        sub_height = height - 2 * spacing

        # Set geometry of each subwindow
        self.sub1.setGeometry(margin, spacing, sub_width, sub_height)
        self.sub2.setGeometry(margin + sub_width + spacing, spacing, sub_width, sub_height)
        self.sub3.setGeometry(margin + 2 * (sub_width + spacing), spacing, sub_width, sub_height)

        print(f"Main window size: {width}x{height}")
        super().resizeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
