# time: 2024/8/26
# author: Jingfeng Tang
# e-mail: tangjingfeng@stmail.ujs.edu.cn
# a tool for generating image masks
# step1: input an image
# step2: doodle any region of image
# step3: save mask


import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QAction, QColorDialog, QVBoxLayout, QWidget, \
    QSpinBox, QLabel, QPushButton, QDialog
from PyQt5.QtGui import QImage, QPainter, QPen, QColor, QPainterPath
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QIcon

from PyQt5.QtGui import QImage
from PIL import Image
import numpy as np


def qimage_to_np(qimg):
    # Get the QImage data as a byte string
    height, width = qimg.height(), qimg.width()
    ptr = qimg.bits()
    ptr.setsize(qimg.byteCount())
    # Reshape the byte string into a NumPy array
    img_array = np.array(ptr).reshape(height, width, 4)  # Assumes 32-bit color with alpha channel
    return img_array


class DrawWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.image = None
        self.drawing = False
        self.last_point = QPoint()
        self.pen_color = QColor(255, 0, 0, 20)  # 更加透明的红色
        self.pen_width = 5
        self.setMouseTracking(True)
        self.paths = []

    def load_image(self, filename):
        self.paths.clear()
        self.image = QImage(filename)

        self.mask = QImage(self.image.size(), QImage.Format_ARGB32_Premultiplied)
        # self.mask = QImage(self.image.size())
        self.mask.fill(Qt.transparent)

        self.update()

    def save_mask(self, filename):
        if self.image is None:
            return
        # 保存图像
        numpy_array = qimage_to_np(self.mask)
        numpy_array = numpy_array.sum(axis=2)
        numpy_array[numpy_array != 0.] = 1.
        numpyimg = (numpy_array * 255).astype(np.uint8)
        # 创建PIL图像
        image = Image.fromarray(numpyimg)

        # 保存图像
        image.save(filename, 'PNG')


    def set_pen_color(self, color):
        self.pen_color = color

    def set_pen_width(self, width):
        self.pen_width = width

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.image is not None:
            self.drawing = True
            self.last_point = event.pos()

    def mouseMoveEvent(self, event):
        if self.drawing and self.image is not None:
            painter = QPainter(self.mask)
            painter1 = QPainter(self.image)
            pen = QPen(self.pen_color, self.pen_width, Qt.SolidLine)
            painter.setPen(pen)
            painter1.setPen(pen)
            painter.drawLine(self.last_point, event.pos())
            painter1.drawLine(self.last_point, event.pos())
            self.last_point = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = False

    def paintEvent(self, event):
        if self.image is not None:
            painter = QPainter(self)
            painter.drawImage(0, 0, self.image)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.draw_widget = DrawWidget()
        self.setCentralWidget(self.draw_widget)

        menubar = self.menuBar()

        # Open Action
        open_action = QAction('Open Image', self)
        open_action.triggered.connect(self.open_image)
        menubar.addAction(open_action)

        # Save Mask Action
        save_action = QAction('Save Mask', self)
        save_action.triggered.connect(self.save_mask)
        menubar.addAction(save_action)

        # Set Pen Color Action
        color_action = QAction('Set Pen Color', self)
        color_action.triggered.connect(self.set_pen_color)
        menubar.addAction(color_action)

        # Set Pen Width Action
        pen_width_action = QAction('Set Pen Width', self)
        pen_width_action.triggered.connect(self.show_pen_width_dialog)
        menubar.addAction(pen_width_action)


        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('Image Doodler')

    def show_pen_width_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle('Set Pen Width')
        layout = QVBoxLayout(dialog)

        layout.addWidget(QLabel('Pen Width:'))

        self.pen_width_spinbox = QSpinBox()
        self.pen_width_spinbox.setRange(1, 100)
        self.pen_width_spinbox.setValue(self.draw_widget.pen_width)
        self.pen_width_spinbox.valueChanged.connect(self.set_pen_width)
        layout.addWidget(self.pen_width_spinbox)

        button = QPushButton('OK')
        button.clicked.connect(dialog.accept)
        layout.addWidget(button)

        dialog.setLayout(layout)
        dialog.exec_()


    def open_image(self):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getOpenFileName(self, 'Open Image', '', 'Images (*.png *.jpg *.bmp)', options=options)
        if filename:
            self.draw_widget.load_image(filename)

    def save_mask(self):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getSaveFileName(self, 'Save Mask', '', 'PNG Files (*.png)', options=options)
        if filename:
            self.draw_widget.save_mask(filename)

    def set_pen_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.draw_widget.set_pen_color(color)

    def set_pen_width(self):
        width = self.pen_width_spinbox.value()
        self.draw_widget.set_pen_width(width)


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QAction, QColorDialog, QVBoxLayout, QWidget, \
        QSpinBox, QLabel, QPushButton, QDialog
    from PyQt5.QtGui import QImage, QPainter, QPen, QColor
    from PyQt5.QtCore import Qt, QPoint
    from PyQt5.QtGui import QIcon

    app = QApplication(sys.argv)
    main_win = MainWindow()

    # 设置窗口图标
    app_icon = QIcon(r'E:\2_my_project\image_doodler\tjf.png')  # 更改为你的图标文件路径
    main_win.setWindowIcon(app_icon)

    main_win.show()
    sys.exit(app.exec_())

