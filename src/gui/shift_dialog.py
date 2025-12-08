from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                              QSpinBox, QDialogButtonBox)
from PyQt5.QtGui import QFont


class ShiftDialog(QDialog):
    """Dialog for setting Y-axis shift amount."""

    def __init__(self, image_height, parent=None):
        """
        Initialize Y-shift dialog.

        Args:
            image_height: Height of the image in pixels
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Y-axis Shift")
        self.setMinimumWidth(400)

        # Set font
        font = QFont("Calibri", 12)
        self.setFont(font)

        self.shift_amount = 0  # Default

        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Info label
        info_label = QLabel(
            "<b>Shift images vertically</b><br>"
            f"Image height: {image_height} pixels"
        )
        info_label.setStyleSheet("font-family: Calibri; font-size: 12pt; padding: 10px;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # Shift amount input
        shift_layout = QHBoxLayout()
        shift_layout.setSpacing(10)

        shift_label = QLabel("Shift amount (pixels):")
        shift_label.setStyleSheet("font-family: Calibri; font-size: 12pt;")

        self.shift_spinbox = QSpinBox()
        self.shift_spinbox.setMinimum(-image_height)
        self.shift_spinbox.setMaximum(image_height)
        self.shift_spinbox.setValue(0)
        self.shift_spinbox.setSuffix(" px")
        self.shift_spinbox.setStyleSheet("font-family: Calibri; font-size: 12pt;")
        self.shift_spinbox.valueChanged.connect(self.set_shift_amount)

        shift_layout.addWidget(shift_label)
        shift_layout.addWidget(self.shift_spinbox)
        shift_layout.addStretch()
        layout.addLayout(shift_layout)

        # Description
        desc_label = QLabel(
            "<i>Positive values shift down, negative values shift up.<br>"
            "The shift wraps around (np.roll behavior).</i>"
        )
        desc_label.setStyleSheet("font-family: Calibri; font-size: 11pt; color: #555; padding: 5px;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.setStyleSheet("font-family: Calibri; font-size: 12pt;")
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def set_shift_amount(self, value):
        """Set the shift amount."""
        self.shift_amount = value

    def get_shift_amount(self):
        """Get the shift amount."""
        return self.shift_amount