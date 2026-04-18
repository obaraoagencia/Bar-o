from __future__ import annotations

import os
from typing import Dict, List, Tuple

import cv2
import matplotlib.pyplot as plt
import numpy as np

from backend.models import AnalysisResult

Point = Tuple[int, int]


def polygon_area_m2(points: List[Point], meters_per_pixel: float = 0.2) -> float:
    if len(points) < 3:
        return 0.0
    x = np.array([p[0] for p in points])
    y = np.array([p[1] for p in points])
    area_pixels = 0.5 * np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))
    return float(area_pixels * (meters_per_pixel**2))


def _mask_from_polygon(shape: Tuple[int, int], points: List[Point]) -> np.ndarray:
    mask = np.zeros(shape[:2], dtype=np.uint8)
    if len(points) >= 3:
        pts = np.array(points, dtype=np.int32)
        cv2.fillPoly(mask, [pts], 255)
    return mask


def classify_terrain(mosaic_bgr: np.ndarray, polygon_points: List[Point]) -> Dict[str, float]:
    hsv = cv2.cvtColor(mosaic_bgr, cv2.COLOR_BGR2HSV)
    mask = _mask_from_polygon(mosaic_bgr.shape, polygon_points)
    valid = mask == 255

    h, s, v = cv2.split(hsv)

    total = np.count_nonzero(valid)
    if total == 0:
        return {"produtiva": 0.0, "baixa": 0.0, "degradada": 0.0, "agua": 0.0, "erosao": 0.0}

    green = np.count_nonzero((h > 35) & (h < 90) & (s > 40) & valid)
    low_veg = np.count_nonzero((h > 20) & (h < 110) & (s <= 40) & valid)
    degraded = np.count_nonzero(((h < 25) | (s < 25)) & (v > 60) & valid)
    water = np.count_nonzero((h > 85) & (h < 140) & (s > 50) & (v < 170) & valid)

    gray = cv2.cvtColor(mosaic_bgr, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 80, 140)
    erosion = np.count_nonzero((edges > 0) & valid)

    return {
        "produtiva": green / total,
        "baixa": low_veg / total,
        "degradada": degraded / total,
        "agua": water / total,
        "erosao": erosion / total,
    }


def generate_altitude_estimation_map(mosaic_bgr: np.ndarray, output_path: str) -> str:
    gray = cv2.cvtColor(mosaic_bgr, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (0, 0), 5)
    grad = cv2.Laplacian(blur, cv2.CV_32F)
    normalized = cv2.normalize(grad, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

    plt.figure(figsize=(8, 6))
    plt.imshow(normalized, cmap="terrain")
    plt.title("Estimativa visual de relevo (tons claros = mais altos)")
    plt.axis("off")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=160, bbox_inches="tight")
    plt.close()
    return output_path


def generate_zone_map(mosaic_bgr: np.ndarray, polygon_points: List[Point], output_path: str) -> str:
    hsv = cv2.cvtColor(mosaic_bgr, cv2.COLOR_BGR2HSV)
    zones = np.zeros_like(mosaic_bgr)

    # Regras simples para zonas
    plantio = ((hsv[:, :, 0] > 35) & (hsv[:, :, 0] < 90) & (hsv[:, :, 1] > 50))
    pasto = ((hsv[:, :, 0] > 25) & (hsv[:, :, 0] <= 35) & (hsv[:, :, 1] > 35))
    degradada = ((hsv[:, :, 0] < 25) & (hsv[:, :, 1] < 80))
    risco = ((hsv[:, :, 0] > 85) & (hsv[:, :, 0] < 140))

    zones[plantio] = (0, 180, 0)
    zones[pasto] = (0, 255, 255)
    zones[degradada] = (42, 42, 165)
    zones[risco] = (0, 0, 255)

    # preservação: bordas do polígono
    poly = np.array(polygon_points, dtype=np.int32)
    if len(poly) >= 3:
        cv2.polylines(zones, [poly], isClosed=True, color=(255, 0, 255), thickness=4)

    blended = cv2.addWeighted(mosaic_bgr, 0.55, zones, 0.45, 0)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cv2.imwrite(output_path, blended)
    return output_path


def suggest_build_location(polygon_points: List[Point]) -> Point:
    pts = np.array(polygon_points, dtype=np.int32)
    center = np.mean(pts, axis=0)
    return int(center[0]), int(center[1])


def generate_paddocks(polygon_points: List[Point], count: int = 4) -> List[List[Point]]:
    if len(polygon_points) < 3:
        return []
    pts = np.array(polygon_points, dtype=np.int32)
    x_min, y_min = pts.min(axis=0)
    x_max, y_max = pts.max(axis=0)

    w = (x_max - x_min) // count if count > 0 else (x_max - x_min)
    paddocks = []
    for i in range(count):
        x0 = x_min + i * w
        x1 = x_min + (i + 1) * w if i < count - 1 else x_max
        paddocks.append([(x0, y_min), (x1, y_min), (x1, y_max), (x0, y_max)])
    return paddocks


def suggest_road(polygon_points: List[Point]) -> List[Point]:
    pts = np.array(polygon_points, dtype=np.int32)
    x_min, y_min = pts.min(axis=0)
    x_max, y_max = pts.max(axis=0)
    return [(x_min, y_max), (x_max, y_min)]


def build_diagnostics(scores: Dict[str, float]) -> Tuple[List[str], List[str]]:
    diagnostics: List[str] = []
    recommendations: List[str] = []

    diagnostics.append(f"Área produtiva estimada: {scores['produtiva']*100:.1f}%")
    diagnostics.append(f"Área com baixa produtividade: {scores['baixa']*100:.1f}%")
    diagnostics.append(f"Área degradada (solo exposto): {scores['degradada']*100:.1f}%")
    diagnostics.append(f"Indício de água parada: {scores['agua']*100:.1f}%")
    diagnostics.append(f"Indício de erosão: {scores['erosao']*100:.1f}%")

    if scores["degradada"] > 0.20:
        recommendations.append("Priorizar recuperação de solo com cobertura vegetal e curvas de nível.")
    if scores["agua"] > 0.05:
        recommendations.append("Avaliar drenagem em áreas com possível água parada.")
    if scores["erosao"] > 0.03:
        recommendations.append("Implantar contenção de erosão (terraceamento e manejo de tráfego).")
    if scores["produtiva"] < 0.35:
        recommendations.append("Rever adubação e manejo para elevar produtividade da área útil.")

    if not recommendations:
        recommendations.append("Condição geral estável; manter monitoramento trimestral por drone.")

    return diagnostics, recommendations


def full_analysis(mosaic_bgr: np.ndarray, polygon_points: List[Point], output_dir: str) -> AnalysisResult:
    area_m2 = polygon_area_m2(polygon_points)
    area_ha = area_m2 / 10_000
    scores = classify_terrain(mosaic_bgr, polygon_points)

    altitude_map_path = generate_altitude_estimation_map(mosaic_bgr, os.path.join(output_dir, "altitude_map.png"))
    zone_map_path = generate_zone_map(mosaic_bgr, polygon_points, os.path.join(output_dir, "zone_map.png"))

    diagnostics, recommendations = build_diagnostics(scores)
    paddocks = generate_paddocks(polygon_points)
    road = suggest_road(polygon_points)
    build_loc = suggest_build_location(polygon_points)

    return AnalysisResult(
        area_m2=area_m2,
        area_ha=area_ha,
        polygon_points=polygon_points,
        score_produtiva=scores["produtiva"],
        score_baixa=scores["baixa"],
        score_degradada=scores["degradada"],
        score_agua=scores["agua"],
        score_erosao=scores["erosao"],
        altitude_map_path=altitude_map_path,
        zone_map_path=zone_map_path,
        diagnostics=diagnostics,
        recommendations=recommendations,
        paddocks=paddocks,
        road_path=road,
        build_location=build_loc,
    )
