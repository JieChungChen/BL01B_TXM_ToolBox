from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QSlider, QSizePolicy,
                              QRadioButton, QDialogButtonBox, QGroupBox, QHBoxLayout,
                              QSpinBox, QPushButton, QFileDialog, QMessageBox)
from PyQt5.QtGui import QImage, QPixmap, QFont
from PyQt5.QtCore import Qt
from PIL import Image
import numpy as np
import os


class FBPResolutionDialog(QDialog):
    """Dialog for selecting FBP reconstruction resolution."""

    def __init__(self, original_size, parent=None):
        """
        Initialize resolution selection dialog.

        Args:
            original_size: Tuple of (height, width) of original images
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("FBP Reconstruction Settings")
        self.setMinimumWidth(450)

        # Set font
        font = QFont("Calibri", 12)
        self.setFont(font)

        self.selected_size = 128  # Default
        self.angle_interval = 1.0  # Default angle interval in degrees

        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Info label
        info_label = QLabel(f"<b>Original Image Size:</b> {original_size[0]}×{original_size[1]}")
        info_label.setStyleSheet("font-family: Calibri; font-size: 13pt; padding: 12px;")
        layout.addWidget(info_label)

        # Angle interval group
        angle_group = QGroupBox("Angle Interval")
        angle_group.setStyleSheet("font-family: Calibri; font-size: 12pt; font-weight: bold;")
        angle_layout = QHBoxLayout()
        angle_layout.setSpacing(10)

        angle_label = QLabel("Projection angle interval:")
        angle_label.setStyleSheet("font-family: Calibri; font-size: 12pt; font-weight: normal;")

        self.angle_spinbox = QSpinBox()
        self.angle_spinbox.setMinimum(1)
        self.angle_spinbox.setMaximum(90)
        self.angle_spinbox.setValue(1)
        self.angle_spinbox.setSuffix(" degree(s)")
        self.angle_spinbox.setStyleSheet("font-family: Calibri; font-size: 12pt;")
        self.angle_spinbox.valueChanged.connect(self.set_angle_interval)

        angle_layout.addWidget(angle_label)
        angle_layout.addWidget(self.angle_spinbox)
        angle_layout.addStretch()
        angle_group.setLayout(angle_layout)
        layout.addWidget(angle_group)

        # Resolution selection group
        group_box = QGroupBox("Select Reconstruction Resolution")
        group_box.setStyleSheet("font-family: Calibri; font-size: 12pt; font-weight: bold;")
        group_layout = QVBoxLayout()
        group_layout.setSpacing(8)

        # Radio buttons
        self.radio_64 = QRadioButton("64×64 (Fastest, ~2-5 seconds)")
        self.radio_128 = QRadioButton("128×128 (Fast, ~5-15 seconds) — Recommended")
        self.radio_256 = QRadioButton("256×256 (Moderate, ~30-60 seconds)")
        self.radio_512 = QRadioButton("512×512 (Slow, ~2-5 minutes)")
        self.radio_original = QRadioButton(f"Original ({min(original_size[0], original_size[1])}×{min(original_size[0], original_size[1])}) (Very slow)")

        # Set default
        self.radio_128.setChecked(True)

        # Style radio buttons
        radio_style = "font-family: Calibri; font-size: 12pt; font-weight: normal; padding: 5px;"
        self.radio_64.setStyleSheet(radio_style)
        self.radio_128.setStyleSheet(radio_style)
        self.radio_256.setStyleSheet(radio_style)
        self.radio_512.setStyleSheet(radio_style)
        self.radio_original.setStyleSheet(radio_style)

        # Connect signals
        self.radio_64.toggled.connect(lambda checked: checked and self.set_size(64))
        self.radio_128.toggled.connect(lambda checked: checked and self.set_size(128))
        self.radio_256.toggled.connect(lambda checked: checked and self.set_size(256))
        self.radio_512.toggled.connect(lambda checked: checked and self.set_size(512))
        self.radio_original.toggled.connect(lambda checked: checked and self.set_size(None))

        group_layout.addWidget(self.radio_64)
        group_layout.addWidget(self.radio_128)
        group_layout.addWidget(self.radio_256)
        group_layout.addWidget(self.radio_512)
        group_layout.addWidget(self.radio_original)
        group_box.setLayout(group_layout)
        layout.addWidget(group_box)

        # Warning label
        warning_label = QLabel(
            "<i>⚠ Higher resolutions require more computation time and memory.</i>"
        )
        warning_label.setStyleSheet("font-family: Calibri; font-size: 11pt; color: #d35400; padding: 8px;")
        warning_label.setWordWrap(True)
        layout.addWidget(warning_label)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.setStyleSheet("font-family: Calibri; font-size: 12pt;")
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def set_size(self, size):
        """Set the selected reconstruction size."""
        self.selected_size = size

    def set_angle_interval(self, value):
        """Set the angle interval."""
        self.angle_interval = float(value)

    def get_size(self):
        """Get the selected reconstruction size."""
        return self.selected_size

    def get_angle_interval(self):
        """Get the angle interval."""
        return self.angle_interval


class FBPViewer(QDialog):
    """Viewer for displaying FBP reconstruction results."""

    def __init__(self, recon_images, parent=None):
        super().__init__(parent)
        self.recon_images = recon_images
        self.current_index = 0

        # Get reconstruction dimensions
        self.n_slices, self.height, self.width = recon_images.shape

        # Set window properties
        self.setMinimumSize(600, 600)
        self.resize(800, 800)

        # Set font
        font = QFont("Calibri", 10)
        self.setFont(font)

        # Image label
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.image_label.setScaledContents(False)

        # Info label
        self.info_label = QLabel()
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("font-family: Calibri; font-size: 10pt; color: #555; padding: 5px;")

        # Slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(self.n_slices - 1)
        self.slider.valueChanged.connect(self.update_image)

        # Save button
        self.save_button = QPushButton("Save Reconstruction as TIF Series")
        self.save_button.setStyleSheet("font-family: Calibri; font-size: 12pt; padding: 8px;")
        self.save_button.clicked.connect(self.save_reconstruction)

        # Layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.image_label, stretch=1)
        layout.addWidget(self.info_label)
        layout.addWidget(self.slider)
        layout.addWidget(self.save_button)

        self.update_image(0)

    def resizeEvent(self, event):
        """Handle window resize events."""
        super().resizeEvent(event)
        self.update_image(self.current_index)

    def update_image(self, index):
        """Update displayed image and window title."""
        self.current_index = index
        img = self.recon_images[index]
        h, w = img.shape

        # Create QImage without any interpolation on the original data
        qimg = QImage(img.data, w, h, w, QImage.Format_Grayscale8)
        pixmap = QPixmap.fromImage(qimg)

        # Scale to fit label while maintaining aspect ratio
        # Use SmoothTransformation for better visual quality when displaying
        label_w = self.image_label.width()
        label_h = self.image_label.height()

        if label_w > 0 and label_h > 0:
            scaled_pixmap = pixmap.scaled(
                label_w, label_h,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
        else:
            self.image_label.setPixmap(pixmap)

        # Update window title
        self.setWindowTitle(
            f"FBP Reconstruction - {self.width}×{self.height} - Slice {index + 1}/{self.n_slices}"
        )

        # Update info label
        self.info_label.setText(
            f"Resolution: {self.width}×{self.height} | Slice: {index + 1}/{self.n_slices}"
        )

    def save_reconstruction(self):
        """Save all reconstruction slices as TIF series."""
        # Select output directory
        output_dir = QFileDialog.getExistingDirectory(
            self,
            "Select Directory to Save Reconstruction",
            "",
            QFileDialog.ShowDirsOnly
        )

        if not output_dir:
            return  # User cancelled

        try:
            # Save each slice with 4-digit filename starting from 0001
            for i in range(self.n_slices):
                filename = f"{i+1:04d}.tif"
                filepath = os.path.join(output_dir, filename)

                # Get image data
                img_data = self.recon_images[i]

                # Save as TIF using PIL
                img_pil = Image.fromarray(img_data)
                img_pil.save(filepath)

            # Show success message
            QMessageBox.information(
                self,
                "Save Complete",
                f"Successfully saved {self.n_slices} slices to:\n{output_dir}"
            )

        except Exception as e:
            # Show error message
            QMessageBox.critical(
                self,
                "Save Error",
                f"Failed to save reconstruction:\n{str(e)}"
            )
