import numpy as np


def norm_to_8bit(img: np.ndarray, clip_percent=0.5, inverse=False):
    vmin = img.min()
    vmax = np.percentile(img, 100 - clip_percent) 
    img = (img - vmin)/(vmax - vmin)
    img = np.clip(img, 0, 1)
    if inverse:
        img = 1 - img
    img = (img * 255).astype(np.uint8)
    return img


def split_mosaic(img: np.ndarray, rows: int, cols: int):
    if img.ndim == 2:
        img = img[None, ...]  # 轉成 (1, H, W)

    N, H_total, W_total = img.shape
    H_patch = H_total // rows
    W_patch = W_total // cols

    patches = []

    for frame in img:
        for i in range(rows):
            for j in range(cols):
                patch = frame[
                    i * H_patch : (i + 1) * H_patch,
                    j * W_patch : (j + 1) * W_patch
                ]
                patches.append(patch)

    return np.stack(patches)


def mosaic_stitching(patches: np.ndarray, rows: int, cols: int):
    N, H, W = patches.shape
    assert N % (rows * cols) == 0, "patch 數量無法剛好組成 mosaic"

    mosaic = np.zeros((rows * H, cols * W), dtype=patches.dtype)

    for i in range(rows):
        for j in range(cols):
            patch_idx = i * cols + j
            patch = patches[patch_idx]
            row_idx = rows - 1 - i  # 從下往上
            mosaic[row_idx*H:(row_idx+1)*H, j*W:(j+1)*W] = patch

    return mosaic


def find_duplicate_angles(thetas):
    """
    回傳重複角度的索引集合 [[idx1, idx2], [idx3, idx4, idx5], ...]
    """
    from collections import defaultdict
    bucket = defaultdict(list)
    for idx, t in enumerate(thetas):
        bucket[t].append(idx)

    duplicates = [v for v in bucket.values() if len(v) > 1]
    return duplicates