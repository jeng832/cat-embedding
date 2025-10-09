# src/cat_embedding/gallery.py
import json, numpy as np
from pathlib import Path
from typing import List, Dict, Tuple
from sklearn.metrics.pairwise import cosine_similarity

from .schema import CatMeta
from .features import human_feature_vector
from .geo import normalize_latlon, extract_gps_from_image
from .embedding_extractor import image_embedding
from .fuse import fuse_vectors

def load_metadata(path: str) -> List[CatMeta]:
    metas = []
    p = Path(path)
    if p.suffix == ".jsonl":
        for line in p.read_text(encoding="utf-8").splitlines():
            metas.append(CatMeta.model_validate_json(line))
    else:
        data = json.loads(p.read_text(encoding="utf-8"))
        for row in data:
            metas.append(CatMeta(**row))
    return metas

def build_vector(meta: CatMeta, bounds=None, weights=(0.85, 0.05, 0.10)) -> np.ndarray:
    img = image_embedding(meta.image_path)
    # If lat/lon missing, try EXIF GPS extraction from the image
    lat, lon = meta.lat, meta.lon
    if lat is None or lon is None:
        gps = extract_gps_from_image(meta.image_path)
        if gps is not None:
            lat, lon = gps
    geo = normalize_latlon(lat, lon, bounds=bounds)
    human = human_feature_vector(meta)
    return fuse_vectors(img, geo, human, *weights)

def build_gallery(metadata_path: str, out_path: str, bounds=None) -> Dict[str, List[np.ndarray]]:
    metas = load_metadata(metadata_path)
    gallery: Dict[str, List[np.ndarray]] = {}
    for m in metas:
        vec = build_vector(m, bounds=bounds)
        key = m.cat_id or "__unknown__"
        gallery.setdefault(key, []).append(vec)
    
    # 저장할 데이터 준비
    save_data = {k: np.vstack(v) for k, v in gallery.items()}
    
    # bounds 정보가 있으면 함께 저장
    if bounds is not None:
        save_data['bounds'] = np.array(bounds)
    
    # 저장(간단히 npz)
    np.savez_compressed(out_path, **save_data)
    return gallery

def load_gallery(npz_path: str) -> Dict[str, np.ndarray]:
    d = np.load(npz_path, allow_pickle=False)
    # bounds 정보는 제외하고 고양이 임베딩만 반환
    return {k: d[k] for k in d.files if k != 'bounds'}

def cosine_top2(query: np.ndarray, mat: np.ndarray) -> Tuple[float,float]:
    sims = cosine_similarity(query.reshape(1,-1), mat)[0]  # (N,)
    if len(sims) == 1: return sims[0], -1.0
    idx = np.argsort(-sims)
    return sims[idx[0]], sims[idx[1]]

def match_query(query_vec: np.ndarray, gallery: Dict[str, np.ndarray],
                threshold: float = 0.80, margin: float = 0.05) -> Tuple[str,float]:
    # 갤러리의 각 ID에 대해 top1 sim 계산 → 가장 높은 ID 선택
    best_id, best_sim, best_second = None, -1.0, -1.0
    for cat_id, mat in gallery.items():
        s1, s2 = cosine_top2(query_vec, mat)
        if s1 > best_sim:
            best_id, best_sim, best_second = cat_id, s1, max(best_second, s2)
    # Open-set 판정
    if best_sim < threshold or (best_sim - best_second) < margin:
        return "UNKNOWN", best_sim
    return best_id, best_sim
