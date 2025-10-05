# src/cat_embedding/fuse.py
import numpy as np

def l2_normalize(v: np.ndarray, eps: float = 1e-9) -> np.ndarray:
    n = np.linalg.norm(v) + eps
    return v / n

def fuse_vectors(img: np.ndarray, geo: np.ndarray, human: np.ndarray,
                 w_img: float = 0.85, w_geo: float = 0.05, w_human: float = 0.10) -> np.ndarray:
    # 각 벡터 L2 정규화 후 가중합 → 다시 L2 정규화
    img_n = l2_normalize(img)
    geo_n = l2_normalize(geo) if geo.size > 0 else geo
    human_n = l2_normalize(human) if human.size > 0 else human
    combined = np.concatenate([w_img*img_n, w_geo*geo_n, w_human*human_n])
    return l2_normalize(combined)
