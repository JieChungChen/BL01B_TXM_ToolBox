import numpy as np
from src.logic.utils import mosaic_stitching, norm_to_8bit


class TXM_Images:
    """Container class for TXM image data with metadata and processing methods."""

    def __init__(self, images: np.ndarray, mode, metadata=None, angles=None):
        """
        Initialize TXM images container.

        Args:
            images: 3D numpy array of shape (N, H, W)
            mode: 'tomo' or 'mosaic'
            metadata: Dictionary of metadata
            angles: Array of rotation angles for tomography
        """
        self.images = images  # shape: (N, H, W)
        self.original = images.copy()  # Keep copy for reference restoration
        self.mode = mode
        self.metadata = metadata or {}
        self.ref = None

        if mode == 'tomo':
            if angles is None:
                self.angles = np.linspace(0, len(images) - 1, len(images))
            else:
                self.angles = angles
        
    def __len__(self):
        return self.images.shape[0]

    def get_image(self, idx):
        return self.images[idx]

    def get_theta(self, idx):
        if self.mode == 'tomo':
            return self.angles[idx]
        return None
    
    def get_full_view(self):
        if self.mode == 'mosaic':
            rows, cols = self.metadata['mosaic_row'], self.metadata['mosaic_column']
            mosaic = mosaic_stitching(self.images, rows, cols)
            mosaic = norm_to_8bit(mosaic, clip_percent=0.)
            return mosaic
        return None
    
    def set(self, idx, image):
        self.images[idx] = image

    def flip_vertical(self):
        self.images = np.flip(self.images, axis=1)

    def apply_ref(self, ref_image):
        if ref_image is not None:
            self.ref = ref_image
            self.images = self.original / ref_image

    def as_array(self):
        return self.images