from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QSlider
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt
from src.logic.utils import norm_to_8bit


class FBPViewer(QDialog):
    def __init__(self, recon_images, parent=None):
        super().__init__(parent)
        self.setWindowTitle("FBP Reconstruction Result")
        self.recon_images = recon_images
        self.current_index = 0
        
        layout = QVBoxLayout(self)
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.image_label)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(len(recon_images) - 1)
        self.slider.valueChanged.connect(self.update_image)
        layout.addWidget(self.slider)

        self.update_image(0)

    def update_image(self, index):
        self.current_index = index
        img = self.recon_images[index]
        h, w = img.shape
        qimg = QImage(img.data, w, h, w, QImage.Format_Grayscale8)
        pixmap = QPixmap.fromImage(qimg)
        self.image_label.setPixmap(pixmap.scaled(
            self.image_label.width(),
            self.image_label.height(),
            Qt.KeepAspectRatio
        ))