from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Tuple

Point = Tuple[int, int]


@dataclass
class ClientData:
    nome_cliente: str
    nome_propriedade: str
    cidade: str
    data: str = field(default_factory=lambda: datetime.now().strftime("%d/%m/%Y"))
    observacoes: str = ""


@dataclass
class AnalysisResult:
    area_m2: float
    area_ha: float
    polygon_points: List[Point]
    score_produtiva: float
    score_baixa: float
    score_degradada: float
    score_agua: float
    score_erosao: float
    altitude_map_path: str
    zone_map_path: str
    diagnostics: List[str]
    recommendations: List[str]
    paddocks: List[List[Point]]
    road_path: List[Point]
    build_location: Point
