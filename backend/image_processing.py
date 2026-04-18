from __future__ import annotations

import glob
import os
from typing import List

import cv2
import numpy as np


def load_images_from_folder(folder: str) -> List[np.ndarray]:
    patterns = ["*.jpg", "*.jpeg", "*.png", "*.tif", "*.tiff", "*.bmp"]
    image_paths = []
    for pattern in patterns:
        image_paths.extend(glob.glob(os.path.join(folder, pattern)))
    image_paths = sorted(image_paths)

    images = []
    for path in image_paths:
        img = cv2.imread(path)
        if img is not None:
            images.append(img)
    return images


def create_simple_mosaic(images: List[np.ndarray]) -> np.ndarray:
    if not images:
        raise ValueError("Nenhuma imagem encontrada para criar mapa.")

    if len(images) == 1:
        return images[0]

    stitcher = cv2.Stitcher_create(cv2.Stitcher_SCANS)
    status, pano = stitcher.stitch(images)

    if status == cv2.Stitcher_OK and pano is not None:
        return pano

    # fallback simples: grade horizontal redimensionada
    min_h = min(img.shape[0] for img in images)
    resized = [cv2.resize(img, (int(img.shape[1] * min_h / img.shape[0]), min_h)) for img in images]
    return cv2.hconcat(resized)


def save_image(img: np.ndarray, output_path: str) -> str:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cv2.imwrite(output_path, img)
    return output_path
