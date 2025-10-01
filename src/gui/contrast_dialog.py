from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QSlider, QDialogButtonBox, QCheckBox
from PyQt5.QtCore import Qt


class ContrastDialog(QDialog):
    def __init__(self, init_clip=0.5, live_update_callback=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Adjust Contrast")
        self.setMinimumWidth(300)

        self.live_update_callback = live_update_callback

        self.clip_slider = QSlider(Qt.Horizontal)
        self.clip_slider.setMinimum(0)
        self.clip_slider.setMaximum(50)  # 0.0% ~ 5.0%
        self.clip_slider.setValue(int(init_clip * 10))
        self.clip_slider.valueChanged.connect(self.on_value_changed)

        self.label = QLabel()
        self.update_label(self.clip_slider.value())

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Clipping Upper Percent (%)"))
        layout.addWidget(self.clip_slider)
        layout.addWidget(self.label)
        self.setLayout(layout)

    def update_label(self, value):
        self.label.setText(f"Clip top {value / 10:.1f}% brightest pixels")

    def on_value_changed(self, *_):
        clip_percent = self.clip_slider.value() / 10.0
        self.update_label(self.clip_slider.value())
        if self.live_update_callback:
            self.live_update_callback(clip_percent)