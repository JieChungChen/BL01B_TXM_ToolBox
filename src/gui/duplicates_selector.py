from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt
import numpy as np
from src.logic.utils import norm_to_8bit


class DuplicateAngleResolver(QDialog):
    def __init__(self, images, theta_value):
        super().__init__()
        self.setWindowTitle(f"Select best image for θ = {theta_value:.2f}")
        self.selected_idx = None

        layout = QVBoxLayout()
        hbox = QHBoxLayout()

        for i, img in enumerate(images):
            label = QLabel()
            img8 = norm_to_8bit(img)
            h, w = img8.shape
            qimg = QImage(img8.data, w, h, w, QImage.Format_Grayscale8)
            pixmap = QPixmap.fromImage(qimg).scaled(400, 400, Qt.KeepAspectRatio)

            label.setPixmap(pixmap)
            label.mousePressEvent = lambda e, idx=i: self.select(idx)
            hbox.addWidget(label)

        layout.addLayout(hbox)
        self.setLayout(layout)

    def select(self, idx):
        self.selected_idx = idx
        self.accept()

    def get_selection(self):
        return self.selected_idx


def resolve_duplicates(images, thetas, duplicates):
    selected_images = []
    selected_thetas = []

    for group in duplicates:
        imgs = [images[i] for i in group]
        theta_val = thetas[group[0]]

        dialog = DuplicateAngleResolver(imgs, theta_val)
        if dialog.exec_() == QDialog.Accepted:
            idx = dialog.get_selection()
            chosen_idx = group[idx]
            selected_images.append(images[chosen_idx])
            selected_thetas.append(thetas[chosen_idx])

    all_idx = set(range(len(thetas)))
    dup_idx = set(i for group in duplicates for i in group)
    nondup_idx = list(all_idx - dup_idx)

    for i in nondup_idx:
        if thetas[i].is_integer():
            selected_images.append(images[i])
            selected_thetas.append(thetas[i])

    selected_images = np.array(selected_images)
    selected_thetas = np.array(selected_thetas)
    sort_idx = np.argsort(selected_thetas)
    return selected_images[sort_idx], selected_thetas[sort_idx]