from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout, QHBoxLayout, QSlider, QPushButton, QFileDialog, QSizePolicy, QMessageBox
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap, QFont
import numpy as np
from PIL import Image


class MosaicPreviewDialog(QDialog):
    def __init__(self, mosaic_img: np.ndarray, metadata=None, parent=None):
        """
        Mosaic preview dialog with contrast adjustment.

        Args:
            mosaic_img: Stitched mosaic image (H, W)
            metadata: Dictionary containing mosaic_row, mosaic_column info
            parent: Parent widget
        """
        super().__init__(parent)
        self.mosaic_img = mosaic_img  # shape: (H, W)
        self.metadata = metadata or {}
        self.clip_lower = 0.0  # Lower clip percentage
        self.clip_upper = 0.5  # Upper clip percentage

        # Get mosaic dimensions
        self.height, self.width = mosaic_img.shape
        self.rows = self.metadata.get('mosaic_row', '?')
        self.cols = self.metadata.get('mosaic_column', '?')

        # Set window properties
        self.setMinimumSize(800, 600)
        self.resize(1000, 800)

        # Set font
        font = QFont("Calibri", 10)
        self.setFont(font)

        # Update window title with mosaic info
        self.update_window_title()

        self.img_8bit = None
        self.qimg = None

        # Image label
        self.img_label = QLabel()
        self.img_label.setAlignment(Qt.AlignCenter)
        self.img_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Info label
        self.info_label = QLabel()
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("font-family: Calibri; font-size: 10pt; color: #555; padding: 5px;")
        self.update_info_label()

        # Lower clip slider
        self.lower_slider = QSlider(Qt.Horizontal)
        self.lower_slider.setMinimum(0)
        self.lower_slider.setMaximum(100)  # 0-10%
        self.lower_slider.setValue(int(self.clip_lower * 10))
        self.lower_slider.valueChanged.connect(self.on_slider_changed)

        # Upper clip slider
        self.upper_slider = QSlider(Qt.Horizontal)
        self.upper_slider.setMinimum(0)
        self.upper_slider.setMaximum(100)  # 0-10%
        self.upper_slider.setValue(int(self.clip_upper * 10))
        self.upper_slider.valueChanged.connect(self.on_slider_changed)

        # Timer for debouncing slider updates (reduce lag)
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self.apply_contrast_change)

        # Save button
        self.save_btn = QPushButton("Save Image")
        self.save_btn.setStyleSheet("font-family: Calibri; font-size: 10pt;")
        self.save_btn.clicked.connect(self.save_image)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.img_label, stretch=1)
        layout.addWidget(self.info_label)

        # Contrast controls
        lower_box = QHBoxLayout()
        lower_label = QLabel("Lower Clip:")
        lower_label.setStyleSheet("font-family: Calibri; font-size: 10pt;")
        self.lower_value_label = QLabel("0.0%")
        self.lower_value_label.setStyleSheet("font-family: Calibri; font-size: 10pt; min-width: 50px;")
        lower_box.addWidget(lower_label)
        lower_box.addWidget(self.lower_slider)
        lower_box.addWidget(self.lower_value_label)

        upper_box = QHBoxLayout()
        upper_label = QLabel("Upper Clip:")
        upper_label.setStyleSheet("font-family: Calibri; font-size: 10pt;")
        self.upper_value_label = QLabel("0.5%")
        self.upper_value_label.setStyleSheet("font-family: Calibri; font-size: 10pt; min-width: 50px;")
        upper_box.addWidget(upper_label)
        upper_box.addWidget(self.upper_slider)
        upper_box.addWidget(self.upper_value_label)

        layout.addLayout(lower_box)
        layout.addLayout(upper_box)

        button_box = QHBoxLayout()
        button_box.addStretch()
        button_box.addWidget(self.save_btn)
        layout.addLayout(button_box)

        self.setLayout(layout)

        # Initial image processing
        self.update_image_data()
        self.update_display()

    def update_window_title(self):
        """Update window title with mosaic dimensions."""
        title = f"Mosaic Preview - {self.width}×{self.height}"
        if self.rows != '?' and self.cols != '?':
            title += f" ({self.rows}×{self.cols} tiles)"
        self.setWindowTitle(title)

    def update_info_label(self):
        """Update info label with mosaic information."""
        info_text = f"Resolution: {self.width}×{self.height}"
        if self.rows != '?' and self.cols != '?':
            info_text += f" | Grid: {self.rows}×{self.cols} tiles"
        self.info_label.setText(info_text)

    def on_slider_changed(self):
        """Handle slider value changes with debouncing."""
        self.pending_lower = self.lower_slider.value()
        self.pending_upper = self.upper_slider.value()

        # Update labels immediately for responsive feedback
        self.lower_value_label.setText(f"{self.pending_lower / 10.0:.1f}%")
        self.upper_value_label.setText(f"{self.pending_upper / 10.0:.1f}%")

        # Debounce the actual image processing (reduce lag)
        self.update_timer.start(200)  # 200ms delay

    def apply_contrast_change(self):
        """Apply contrast changes after debounce delay."""
        self.clip_lower = self.pending_lower / 10.0
        self.clip_upper = self.pending_upper / 10.0
        self.update_image_data()
        self.update_display()

    def update_image_data(self):
        """Update 8-bit image data with current clip values."""
        vmin = np.percentile(self.mosaic_img, self.clip_lower)
        vmax = np.percentile(self.mosaic_img, 100 - self.clip_upper)

        # Avoid division by zero
        if vmax == vmin:
            vmax = vmin + 1e-7

        # Normalize to 8-bit
        normalized = (self.mosaic_img - vmin) / (vmax - vmin)
        self.img_8bit = np.clip(normalized * 255, 0, 255).astype(np.uint8)

        h, w = self.img_8bit.shape
        self.qimg = QImage(self.img_8bit.data, w, h, w, QImage.Format_Grayscale8)

    def update_display(self):
        """Update displayed image, scaling to fit current window size."""
        if self.qimg is None:
            return

        label_w = self.img_label.width()
        label_h = self.img_label.height()

        if label_w > 0 and label_h > 0:
            pixmap = QPixmap.fromImage(self.qimg)
            scaled_pixmap = pixmap.scaled(
                label_w, label_h,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.img_label.setPixmap(scaled_pixmap)

    def resizeEvent(self, event):
        """Handle window resize events."""
        super().resizeEvent(event)
        # Only update display (scale), not reprocess image data
        self.update_display()

    def save_image(self):
        """Save the processed mosaic image."""
        default_name = f"mosaic_{self.width}x{self.height}.tif"
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save mosaic", default_name, "TIFF files (*.tif)"
        )
        if filename:
            Image.fromarray(self.img_8bit).save(filename)
            QMessageBox.information(self, "Save Complete", f"Mosaic saved to:\n{filename}")
