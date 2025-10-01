from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout, QHBoxLayout, QSlider, QPushButton, QFileDialog
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
import numpy as np
from PIL import Image


class MosaicPreviewDialog(QDialog):
    def __init__(self, mosaic_img: np.ndarray, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Mosaic Preview")
        self.mosaic_img = mosaic_img  # shape: (H, W)
        self.clip_percent = 0.5  # default clip percent

        self.img_8bit = None
        self.qimg = None

        self.img_label = QLabel()
        self.img_label.setAlignment(Qt.AlignCenter)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(50)
        self.slider.setValue(int(self.clip_percent * 10))  # 1.0 → 10
        self.slider.valueChanged.connect(self.on_slider_changed)
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self.apply_contrast_change)

        self.save_btn = QPushButton("Save image")
        self.save_btn.clicked.connect(self.save_image)

        hbox = QHBoxLayout()
        hbox.addWidget(QLabel("Contrast"))
        hbox.addWidget(self.slider)
        hbox.addWidget(self.save_btn)

        layout = QVBoxLayout()
        layout.addWidget(self.img_label)
        layout.addLayout(hbox)
        self.setLayout(layout)

        self.update_image_data()
        self.update_display()

    def on_slider_changed(self, value):
        self.pending_value = value
        self.update_timer.start(100)  # 100ms 內如果沒再動，就執行更新

    def apply_contrast_change(self):
        self.clip_percent = self.pending_value / 10.0
        self.update_image_data()
        self.update_display()

    def update_image_data(self):
        vmax = np.percentile(self.mosaic_img, 100 - self.clip_percent) 
        self.img_8bit = np.clip(self.mosaic_img, 0, vmax)
        self.img_8bit = (self.img_8bit * (255/vmax)).astype(np.uint8)
        h, w = self.img_8bit.shape
        self.qimg = QImage(self.img_8bit.data, w, h, w, QImage.Format_Grayscale8)

    def update_display(self):
        if self.qimg is None:
            return
        label_w = self.img_label.width()
        label_h = self.img_label.height()
        pixmap = QPixmap.fromImage(self.qimg)
        self.img_label.setPixmap(pixmap.scaled(label_w, label_h, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_display()  # resize 時只 scale，不重新轉資料

    def save_image(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save mosaic", f"mosaic.tif", "TIFF files (*.tif)")
        if filename:
            Image.fromarray(self.img_8bit).save(filename)