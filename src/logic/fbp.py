import numpy as np
from PIL import Image
from PyQt5.QtCore import QThread, pyqtSignal


# ===== 原有的濾波器計算 =====
def get_hann_filter(img_size):
    n = np.concatenate((
        np.arange(1, img_size//2 + 1, 2),
        np.arange(img_size//2 - 1, 0, -2)
    ))
    f = np.zeros(img_size)
    f[0] = 0.25
    f[1::2] = -1 / (np.pi * n) ** 2
    ramp = 2 * np.real(np.fft.fft(f))
    hann = np.hanning(img_size)
    hann = np.fft.fftshift(hann)
    return ramp * hann

# ===== 預先計算幾何參數 =====
def prepare_fbp_geometry(L, angles_deg):
    center = L // 2
    x, y = np.meshgrid(np.arange(L) - center, np.arange(L) - center, indexing='ij')
    angles = np.deg2rad(angles_deg)
    cos_vals = np.cos(angles + np.pi/2)
    sin_vals = np.sin(angles + np.pi/2)
    return center, x, y, cos_vals, sin_vals

# ===== 單切片重建 =====
def filter_back_projection_fast(sino, cos_vals, sin_vals, center, x, y, hann=None, filtered=True, circle=False):
    n_proj, L = sino.shape

    if filtered and hann is not None:
        pad_width = hann.size - L
        sino_padded = np.pad(sino, ((0, 0), (0, pad_width)), mode='constant', constant_values=0)
        sino_fft = np.fft.fft(sino_padded, axis=-1)
        sino = np.real(np.fft.ifft(sino_fft * hann, axis=-1))[:, :L]

    recon = np.zeros((L, L), dtype=np.float32)

    for i in range(n_proj):
        t = x * cos_vals[i] + y * sin_vals[i]
        t_idx = np.round(t + center).astype(np.int32)
        valid = (t_idx >= 0) & (t_idx < L)
        recon[valid] += sino[i, t_idx[valid]]

    if circle:
        Y, X = np.ogrid[:L, :L]
        dist_from_center = np.sqrt((X - center) ** 2 + (Y - center) ** 2)
        mask = dist_from_center > center
        recon[mask] = 0

    return recon

# ===== QThread Worker =====
class FBPWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(np.ndarray)

    def __init__(self, images, angles, target_size=None):
        """
        Initialize FBP reconstruction worker.

        Args:
            images: Input projection images (N, H, W)
            angles: Rotation angles for each projection
            target_size: Target resolution for reconstruction (int or None)
                        If None, uses original resolution
                        If int, resizes to (target_size, target_size)
        """
        super().__init__()
        self.angles = angles

        # Resize images if target_size is specified
        if target_size is not None:
            self.images = []
            for i in range(len(images)):
                img_temp = Image.fromarray(images[i])
                img_temp = img_temp.resize((target_size, target_size), Image.Resampling.LANCZOS)
                self.images.append(np.array(img_temp))
            self.images = np.array(self.images)
        else:
            # Use original resolution
            self.images = images.copy()

    def run(self):
        n, h, w = self.images.shape
        recon = np.zeros((h, w, w))
        
        img_size_padded = max(64, 2 ** int(np.ceil(np.log2(2 * w))))
        hann = get_hann_filter(img_size_padded)
        center, x, y, cos_vals, sin_vals = prepare_fbp_geometry(w, self.angles)

        empty_sino = np.ones((n, w))
        recon_0 = filter_back_projection_fast(empty_sino, cos_vals, sin_vals, center, x, y, hann)
        for i in range(h):
            sino = self.images[:, i, :]
            temp = filter_back_projection_fast(sino, cos_vals, sin_vals, center, x, y, hann, filtered=True, circle=False)
            
            temp /= recon_0
            recon[i] = temp
            self.progress.emit(int((i + 1) / h * 100))

        recon -= recon.min()
        recon /= recon.max()
        recon = (recon * 255).astype(np.uint8)
        self.finished.emit(recon)