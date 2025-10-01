import numpy as np
from PIL import Image, ImageDraw
from PyQt5.QtWidgets import (QLabel, QDialog, QPushButton, QVBoxLayout, QSizePolicy,
                             QHBoxLayout, QSlider, QFileDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
from src.logic.utils import norm_to_8bit


class AlignViewer(QDialog):
    def __init__(self, tomography, last_dir='.'):
        super().__init__()
        self.setWindowTitle("Align Viewer")
        self.setMinimumSize(500, 500)
        self.setModal(True)

        self.tomo = tomography
        self.proj_images = [norm_to_8bit(img.copy()) for img in self.tomo.as_array()]
        self.red_points = [None] * len(self.proj_images)
        self.last_dir = last_dir

        self.center_index = len(self.proj_images) // 2
        self.index = self.center_index
        self.shifts = [[0, 0] for _ in range(len(self.proj_images))]
        half_height = self.proj_images[0].shape[0] // 2
        self.line_y1 = half_height + 100
        self.dragging_line1 = False

        self.img_label = QLabel()
        self.img_label.setAlignment(Qt.AlignCenter)
        self.img_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.prev_btn = QPushButton('Prev')
        self.next_btn = QPushButton('Next')
        self.save_btn = QPushButton('Save shifts')
        self.load_btn = QPushButton('Load shifts')
        self.done_btn = QPushButton('Finish') 

        self.prev_btn.clicked.connect(self.prev_pair)
        self.next_btn.clicked.connect(self.next_pair)
        self.save_btn.clicked.connect(self.save_shifts)
        self.load_btn.clicked.connect(self.load_shifts) 
        self.done_btn.clicked.connect(self.accept) 
        
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(len(self.proj_images) - 1)
        self.slider.setValue(self.index)
        self.slider.valueChanged.connect(self.on_slider_changed)
    
        layout = QVBoxLayout()
        layout.addWidget(self.img_label)
        hbox = QHBoxLayout()
        hbox.addWidget(self.prev_btn)
        hbox.addWidget(self.next_btn)
        hbox.addWidget(self.save_btn)
        hbox.addWidget(self.load_btn) 
        hbox.addWidget(self.done_btn)
        layout.addLayout(hbox)
        layout.addWidget(self.slider)
        self.setLayout(layout)

        self.update_view()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_view()

    def keyPressEvent(self, event):
        key = event.key()
        dx, dy = 0, 0
        if key == Qt.Key_W:
            self.shifts[self.index][0] -= 1
            dy -= 1
        elif key == Qt.Key_S:
            self.shifts[self.index][0] += 1
            dy += 1
        elif key == Qt.Key_A:
            self.shifts[self.index][1] -= 1
            dx -= 1
        elif key == Qt.Key_D:
            self.shifts[self.index][1] += 1
            dx += 1

        img_temp = self.proj_images[self.index]
        self.proj_images[self.index] = np.roll(img_temp, shift=(dy, dx), axis=(0, 1))
        if self.red_points[self.index] is not None:
            x, y = self.red_points[self.index]
            self.red_points[self.index] = (x + dx, y + dy)
        self.update_view()

    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton or self.img_label.pixmap() is None:
            return
        
        # 滑鼠座標
        mouse_x = event.x() - self.img_label.x()
        mouse_y = event.y() - self.img_label.y()
        pixmap = self.img_label.pixmap()
        label_w, label_h = self.img_label.width(), self.img_label.height()
        pm_w, pm_h = pixmap.width(), pixmap.height()
        # 圖片在 QLabel 中的偏移（居中）
        offset_x = max((label_w - pm_w) // 2, 0)
        offset_y = max((label_h - pm_h) // 2, 0)
        # 扣除 padding 得到實際圖片上的座標
        img_x = int((mouse_x - offset_x) / self.scale)
        img_y = int((mouse_y - offset_y) / self.scale)

        # 防止座標超出範圍
        if img_x < 0 or img_x >= self.raw_width or img_y < 0 or img_y >= self.raw_height:
            return

        if abs(img_y - self.line_y1) < 5:
            self.dragging_line1 = True
        else:
            center_x = self.raw_width // 2
            center_y = self.raw_height // 2
            dx = center_x - img_x
            dy = center_y - img_y

            # 記錄並平移影像
            self.red_points[self.index] = (center_x, center_y)
            self.shifts[self.index][0] += dy
            self.shifts[self.index][1] += dx
            self.proj_images[self.index] = np.roll(self.proj_images[self.index], shift=(dy, dx), axis=(0, 1))
            self.update_view()

    def mouseMoveEvent(self, event):
        if self.dragging_line1:
            mouse_y = event.pos().y() - self.img_label.pos().y()
            img_y = int(mouse_y / self.scale)
            img_y = max(0, min(img_y, self.raw_height - 1))
            self.line_y1 = img_y
            self.update_view()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging_line1 = False

    def on_slider_changed(self, value):
        self.index = value
        self.update_view()

    def update_view(self):
        img_show = self.proj_images[self.index]
        img_rgb = np.stack([img_show]*3, axis=-1)
        pil_img = Image.fromarray(img_rgb)
        draw = ImageDraw.Draw(pil_img)
        h, w = pil_img.size

        # support line and point
        draw.line([(0, self.line_y1), (pil_img.width, self.line_y1)], fill=(0, 255, 0), width=1)
        if self.red_points[self.index] is not None:
            x, y = self.red_points[self.index]
            r = 8  # 十字長度
            draw.line([(x - r, y), (x + r, y)], fill=(0, 255, 0), width=2)
            draw.line([(x, y - r), (x, y + r)], fill=(0, 255, 0), width=2)

        img_rgb = np.array(pil_img)
        self.raw_height, self.raw_width = img_rgb.shape[:2]
        label_w, label_h = self.img_label.width(), self.img_label.height()
        scale_w = label_w / self.raw_width
        scale_h = label_h / self.raw_height
        self.scale = min(scale_w, scale_h)

        h, w = img_rgb.shape[:2]
        qimg = QImage(img_rgb.data, w, h, 3 * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)
        self.img_label.setPixmap(pixmap.scaled(label_w, label_h, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        self.setWindowTitle(f"Align Viewer {self.index + 1}/{len(self.proj_images)}")

    def prev_pair(self):
        if self.index > 0:
            self.index -= 1
            self.slider.setValue(self.index)

    def next_pair(self):
        if self.index < len(self.proj_images) - 1:
            self.index += 1
            self.slider.setValue(self.index)
    
    def save_shifts(self):
        save_path = QFileDialog.getSaveFileName(self, "Save shifts", self.last_dir, "Text Files (*.txt)")[0]
        if save_path:
            with open(save_path, 'w') as f:
                for i, (dx, dy) in enumerate(self.shifts):
                    f.write(f"{str(i).zfill(3)},{dx},{dy}\n")
            print(f'Saved {save_path}')

    def load_shifts(self):
        shifts_file, _ = QFileDialog.getOpenFileName(None, "Load Shifts", "*.txt")
        if shifts_file:
            with open(shifts_file, 'r') as f:
                for line in f:
                    parts = line.strip().split(',')
                    if len(parts) == 3:
                        idx, dy, dx = map(int, parts)
                        if 0 <= idx < len(self.shifts):
                            self.shifts[idx] = [dy, dx]  # 注意 numpy shift 是 (dy, dx)
                            self.proj_images[idx] = np.roll(self.proj_images[idx], shift=(dy, dx), axis=(0, 1))
        self.update_view()

    def accept(self):
        for i, img in enumerate(self.proj_images):
            self.tomo.set(i, img)  # 更新 Tomography 中的對應圖片
        super().accept()