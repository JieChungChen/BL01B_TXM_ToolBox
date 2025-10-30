import os
import sys
from PyQt5.QtWidgets import (QProgressDialog, QApplication, QMainWindow,
                              QFileDialog, QMessageBox, QDialog)
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt
from src.gui.integrate_multi_txrm import resolve_duplicates
from src.gui.contrast_dialog import ContrastDialog
from src.gui.manual_alignment import AlignViewer
from src.gui.fbp_viewer import FBPViewer, FBPResolutionDialog
from src.gui.mosaic_viewer import MosaicPreviewDialog
from src.gui.y_shift_dialog import YShiftDialog
from src.gui.main_window import Ui_TXM_ToolBox
from src.logic import data_io
from src.logic.app_context import AppContext
from src.logic.tomography import TXM_Images
from src.logic.fbp import FBPWorker
from src.logic.utils import norm_to_8bit, find_duplicate_angles
from src.logic.decorators import handle_errors
from src.logic.exceptions import FileLoadError


class TXM_ToolBox(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_TXM_ToolBox()
        self.ui.setupUi(self)
        self.setMinimumSize(600, 600)

        self.context = AppContext()

        self.current_id = 0
        self.clip_lower = 0.0 
        self.clip_upper = 0.5  
        
        self.ui.imageSlider.valueChanged.connect(self.update_image)
        self.ui.action_tomo_txrm.triggered.connect(self.load_tomo_txrm)
        self.ui.action_multi_txrm.triggered.connect(self.load_multiple_txrm)
        self.ui.action_tomo_tifs.triggered.connect(lambda: self.load_tifs('tomo'))
        self.ui.action_mosaic_txrm.triggered.connect(self.load_mosaic)
        self.ui.action_mosaic_tifs.triggered.connect(lambda: self.load_tifs('mosaic'))
        self.ui.action_save_img.triggered.connect(self.save_image)
        
        self.ui.action_vertical_flip.triggered.connect(self.vertical_flip)
        self.ui.action_reference.triggered.connect(self.load_ref)
        self.ui.action_y_shift.triggered.connect(self.apply_y_shift)
        self.ui.action_adjust_contrast.triggered.connect(self.open_contrast_dialog)
        self.ui.action_alignment.triggered.connect(self.open_align_viewer)
        self.ui.action_reconstruction.triggered.connect(self.get_fbp_result)
        self.ui.action_full_view.triggered.connect(self.mosaic_stitching)

    def resizeEvent(self, event):
        '''
        調整視窗大小
        '''
        super().resizeEvent(event)
        if self.context.images is not None:
            self.update_image(self.current_id)

    @handle_errors(title="Load TXRM Error")
    def load_tomo_txrm(self, *args):
        '''
        載入單一tomography txrm原始檔
        '''
        filename, _ = QFileDialog.getOpenFileName(self, "Open .txrm file", self.context.last_load_dir, "*.txrm")
        if not filename:
            return

        images, metadata, angles, ref = data_io.read_txm_raw(filename, mode='tomo')
        self.context.set_from_file(filename, 'tomo')
        self.context.images = TXM_Images(images, 'tomo', metadata, angles)
        self.context.images.apply_ref(ref)
        self.update_env()
        self.show_info_message("TXM Metadata", metadata)

    @handle_errors(title="Load Multiple TXRM Error")
    def load_multiple_txrm(self, *args):
        '''
        載入多個tomography txrm原始檔 並人工篩選重複的projections
        '''
        file_list, _ = QFileDialog.getOpenFileNames(self, "Select multiple .txrm file", self.context.last_load_dir, "*.txrm")
        if not file_list:
            return

        images, angles = data_io.read_multiple_txrm(file_list)
        self.context.set_from_file(file_list[0], 'tomo')
        duplicates = find_duplicate_angles(angles)

        if duplicates:
            images, angles = resolve_duplicates(images, angles, duplicates)

        self.context.images = TXM_Images(images, 'tomo', angles=angles)
        self.update_env()

    @handle_errors(title="Load XRM Error")
    def load_mosaic(self, *args):
        '''
        載入mosaic xrm原始檔
        '''
        filename, _ = QFileDialog.getOpenFileName(self, "Open .xrm file", self.context.last_load_dir, "*.xrm")
        if not filename:
            return

        images, metadata, ref = data_io.read_txm_raw(filename, mode='mosaic')
        self.context.set_from_file(filename, 'mosaic')
        self.context.images = TXM_Images(images, 'mosaic', metadata)
        self.context.images.apply_ref(ref)
        self.update_env()
        self.show_info_message("TXM Metadata", metadata)

    @handle_errors(title="Load TIFs Error")
    def load_tifs(self, mode):
        '''
        載入tomography或mosaic tif圖檔
        '''
        folder = QFileDialog.getExistingDirectory(self, "Choose folder", self.context.last_load_dir)
        if not folder:
            return

        images = data_io.load_tif_folder(folder)
        if images is None:
            raise FileLoadError("No TIF images found in the selected folder")
        
        self.context.set_from_folder(folder, mode)
        self.context.images = TXM_Images(images, 'tomo')
        self.update_env()

    @handle_errors(title="Load Reference Error")
    def load_ref(self, *args):
        '''
        載入reference xrm或tif檔
        '''
        filename, _ = QFileDialog.getOpenFileName(self, "Open reference file", "", "(*.xrm *.tif)")
        if not filename:
            return

        ref = data_io.load_ref(filename)
        self.context.images.apply_ref(ref)
        self.update_image(self.ui.imageSlider.value())

    def update_image(self, index=0):
        self.current_id = index
        img = self.context.images.get_image(index)
        img = norm_to_8bit(img, clip_lower=self.clip_lower, clip_upper=self.clip_upper)
        h, w = img.shape
        qimg = QImage(img.data, w, h, w, QImage.Format_Grayscale8)
        pixmap = QPixmap.fromImage(qimg)

        self.ui.imageLabel.setPixmap(pixmap.scaled(
            self.ui.imageLabel.width(),
            self.ui.imageLabel.height(),
            Qt.KeepAspectRatio))
        self.ui.imageIndexLabel.setText(f"{index+1} / {len(self.context.images)}")
        if self.context.mode == 'tomo':
            theta = self.context.images.get_theta(index)
            if theta is not None:
                self.setWindowTitle(f"{self.context.sample_name}, theta = {theta}")
        else:
            self.setWindowTitle(f"{self.context.sample_name}")

    def update_env(self):
        """Update UI state after loading images."""
        self.ui.action_reference.setEnabled(True)
        self.ui.action_save_img.setEnabled(True)
        self.ui.action_vertical_flip.setEnabled(True)
        self.ui.action_y_shift.setEnabled(True)
        self.ui.action_adjust_contrast.setEnabled(True)
        self.ui.action_alignment.setEnabled(self.context.mode == 'tomo')
        self.ui.action_reconstruction.setEnabled(self.context.mode == 'tomo')
        self.ui.action_full_view.setEnabled(self.context.mode == 'mosaic')

        self.ui.imageSlider.setMinimum(0)
        self.ui.imageSlider.setMaximum(len(self.context.images) - 1)
        self.update_image()

    def vertical_flip(self, *args):
        self.context.images.flip_vertical()
        self.update_image(self.current_id)

    @handle_errors(title="Y-Shift Error")
    def apply_y_shift(self, *args):
        img_array = self.context.get_images()
        image_height = img_array.shape[1]  # (N, H, W)

        dialog = YShiftDialog(image_height, self)
        if dialog.exec_() != QDialog.Accepted:
            return 

        shift_amount = dialog.get_shift_amount()

        if shift_amount == 0:
            return

        self.context.images.y_shift(shift_amount)
        self.update_image(self.current_id)
        self.statusBar().showMessage(f"Applied Y-shift: {shift_amount} pixels", 3000)

    def on_contrast_live_update(self, clip_lower, clip_upper):
        """Handle contrast adjustment updates from dialog."""
        self.clip_lower = clip_lower
        self.clip_upper = clip_upper
        self.update_image(self.current_id)

    def open_contrast_dialog(self):
        """Open contrast adjustment dialog."""
        ContrastDialog(
            init_clip_lower=self.clip_lower,
            init_clip_upper=self.clip_upper,
            live_update_callback=self.on_contrast_live_update,
            parent=self
        ).show()

    @handle_errors(title="Alignment Error")
    def open_align_viewer(self, *args):
        """Open manual alignment viewer."""
        dialog = AlignViewer(self.context.images, self.context.last_load_dir)
        if dialog.exec_() == QDialog.Accepted:
            self.update_image(self.current_id)

    @handle_errors(title="Reconstruction Error")
    def get_fbp_result(self, *args):
        """Start FBP reconstruction in background thread."""
        # Get original image size
        img_array = self.context.get_images()
        original_size = (img_array.shape[1], img_array.shape[2])  # (height, width)

        # Show resolution selection dialog
        resolution_dialog = FBPResolutionDialog(original_size, self)
        if resolution_dialog.exec_() != QDialog.Accepted:
            return  # User cancelled

        target_size = resolution_dialog.get_size()
        angle_interval = resolution_dialog.get_angle_interval()

        # Show progress dialog
        self.progress_dialog = QProgressDialog(
            "Reconstructing...", None, 0, 100, self
        )
        self.progress_dialog.setWindowTitle("FBP Reconstruction")
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.show()

        # Start reconstruction with selected resolution and angle interval
        self.worker = FBPWorker(img_array, self.context.images.angles, target_size=target_size, angle_interval=angle_interval)
        self.worker.progress.connect(self.progress_dialog.setValue)
        self.worker.finished.connect(self.on_fbp_finished)
        self.worker.start()

    def on_fbp_finished(self, recon):
        """Handle FBP reconstruction completion."""
        self.progress_dialog.close()
        dialog = FBPViewer(recon, self)
        dialog.exec_()

    @handle_errors(title="Mosaic Stitching Error")
    def mosaic_stitching(self, *args):
        """Display mosaic stitching preview."""
        mosaic = self.context.images.get_mosaic()
        if mosaic is not None:
            dialog = MosaicPreviewDialog(mosaic, self.context)
            dialog.exec_()

    @handle_errors(title="Save Image Error")
    def save_image(self, *args):
        """Save images as TIF sequence."""
        default_path = os.path.join(self.context.last_save_dir, f"{self.context.sample_name}.tif")
        filename, _ = QFileDialog.getSaveFileName(self, "Save images", default_path, "TIFF files (*.tif)")
        if not filename:
            return

        self.context.last_save_dir = os.path.dirname(filename)
        data_io.save_tif(self.context.last_save_dir, 
                         self.context.sample_name, 
                         self.context.get_images())

        self.show_info_message("Save image", f"Success! TIF images saved to '{self.context.last_save_dir}'.")
    
    def show_info_message(self, title, info):
        if isinstance(info, dict):
            text = "\n".join(f"{key}: {value}" for key, value in info.items())
        else: 
            text = info    
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setIcon(QMessageBox.Information)
        msg.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TXM_ToolBox()
    window.show()
    sys.exit(app.exec_())