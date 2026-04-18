from __future__ import annotations

import os

import cv2
import numpy as np
import open3d as o3d


def generate_simple_3d_model(mosaic_path: str, output_dir: str, base_name: str = "terrain_model") -> str:
    img = cv2.imread(mosaic_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError("Não foi possível ler imagem para gerar 3D.")

    h, w = img.shape
    scale = 0.2
    points = []
    colors = []

    small = cv2.resize(img, (max(80, w // 8), max(80, h // 8)))
    sh, sw = small.shape
    for y in range(sh):
        for x in range(sw):
            z = float(small[y, x]) / 255.0
            points.append([x * scale, y * scale, z * 10.0])
            c = z
            colors.append([c, c, c])

    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(np.array(points))
    pcd.colors = o3d.utility.Vector3dVector(np.array(colors))

    os.makedirs(output_dir, exist_ok=True)
    ply_path = os.path.join(output_dir, f"{base_name}.ply")
    o3d.io.write_point_cloud(ply_path, pcd)

    mesh, _ = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(pcd, depth=6)
    obj_path = os.path.join(output_dir, f"{base_name}.obj")
    o3d.io.write_triangle_mesh(obj_path, mesh)

    return obj_path
