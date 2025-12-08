from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QSlider
from PyQt5.QtCore import Qt


class ContrastDialog(QDialog):
    def __init__(self, init_clip_lower=0.0, init_clip_upper=0.5, live_update_callback=None, parent=None):
        """
        Contrast adjustment dialog with dual clip control.

        Args:
            init_clip_lower: Initial lower clip percentage (0-10%)
            init_clip_upper: Initial upper clip percentage (0-10%)
            live_update_callback: Callback function(clip_lower, clip_upper)
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Adjust Contrast")
        self.setMinimumWidth(450)
        self.setMinimumHeight(250)

        # Set font for better readability
        from PyQt5.QtGui import QFont
        font = QFont("Calibri", 12)
        self.setFont(font)

        self.live_update_callback = live_update_callback

        # Lower clip slider (for darkest pixels)
        self.lower_slider = QSlider(Qt.Horizontal)
        self.lower_slider.setMinimum(0)
        self.lower_slider.setMaximum(100)  # 0.0% ~ 10.0%
        self.lower_slider.setValue(int(init_clip_lower * 10))
        self.lower_slider.valueChanged.connect(self.on_value_changed)

        # Upper clip slider (for brightest pixels)
        self.upper_slider = QSlider(Qt.Horizontal)
        self.upper_slider.setMinimum(0)
        self.upper_slider.setMaximum(100)  # 0.0% ~ 10.0%
        self.upper_slider.setValue(int(init_clip_upper * 10))
        self.upper_slider.valueChanged.connect(self.on_value_changed)

        # Labels
        self.lower_label = QLabel()
        self.upper_label = QLabel()
        self.update_labels()

        # Layout
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # Lower clip section
        lower_title = QLabel("<b>Lower Bound (Clip Darkest Pixels)</b>")
        lower_title.setStyleSheet("font-family: Calibri; font-size: 12pt;")
        layout.addWidget(lower_title)
        layout.addWidget(self.lower_slider)
        self.lower_label.setStyleSheet("font-family: Calibri; font-size: 12pt; color: #333;")
        layout.addWidget(self.lower_label)

        layout.addSpacing(20)

        # Upper clip section
        upper_title = QLabel("<b>Upper Bound (Clip Brightest Pixels)</b>")
        upper_title.setStyleSheet("font-family: Calibri; font-size: 12pt;")
        layout.addWidget(upper_title)
        layout.addWidget(self.upper_slider)
        self.upper_label.setStyleSheet("font-family: Calibri; font-size: 12pt; color: #333;")
        layout.addWidget(self.upper_label)

        layout.addSpacing(15)

        # Summary label
        self.summary_label = QLabel()
        self.summary_label.setStyleSheet("font-family: Calibri; font-size: 12pt; color: #555; font-style: italic; padding: 5px;")
        layout.addWidget(self.summary_label)
        self.update_summary()

        self.setLayout(layout)

    def update_labels(self):
        """Update the clip percentage labels."""
        lower_val = self.lower_slider.value() / 10.0
        upper_val = self.upper_slider.value() / 10.0
        self.lower_label.setText(f"Clip bottom {lower_val:.1f}% darkest pixels")
        self.upper_label.setText(f"Clip top {upper_val:.1f}% brightest pixels")

    def update_summary(self):
        """Update summary label."""
        lower_val = self.lower_slider.value() / 10.0
        upper_val = self.upper_slider.value() / 10.0
        total = lower_val + upper_val
        self.summary_label.setText(f"Total clipping: {total:.1f}% ({lower_val:.1f}% lower + {upper_val:.1f}% upper)")

    def on_value_changed(self):
        """Handle slider value changes."""
        self.update_labels()
        self.update_summary()

        if self.live_update_callback:
            clip_lower = self.lower_slider.value() / 10.0
            clip_upper = self.upper_slider.value() / 10.0
            self.live_update_callback(clip_lower, clip_upper)