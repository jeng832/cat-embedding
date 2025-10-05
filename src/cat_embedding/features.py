# src/cat_embedding/features.py
import numpy as np
from .schema import CatMeta

EAR_TIP_MAP = {"none": [1,0,0], "left": [0,1,0], "right":[0,0,1]}
NOSE_MAP    = {"pink":[1,0,0,0], "black":[0,1,0,0], "spotted":[0,0,1,0], "other":[0,0,0,1]}
EYE_MAP     = {"yellow":[1,0,0,0], "green":[0,1,0,0], "blue":[0,0,1,0], "other":[0,0,0,1]}
COAT_MAP    = {"black":[1,0,0,0,0,0], "ginger_tabby":[0,1,0,0,0,0], "tuxedo":[0,0,1,0,0,0],
               "calico":[0,0,0,1,0,0], "white":[0,0,0,0,1,0], "other":[0,0,0,0,0,1]}

def human_feature_vector(meta: CatMeta) -> np.ndarray:
    ear = np.array(EAR_TIP_MAP.get(meta.ear_tip, EAR_TIP_MAP["none"]), dtype=float)
    nose = np.array(NOSE_MAP.get(meta.nose_color, NOSE_MAP["other"]), dtype=float)
    eye = np.array(EYE_MAP.get(meta.eye_color, EYE_MAP["other"]), dtype=float)
    coat = np.array(COAT_MAP.get(meta.coat_type, COAT_MAP["other"]), dtype=float)
    stripes = np.array([1.0 if meta.has_stripes else 0.0], dtype=float)
    return np.concatenate([ear, nose, eye, coat, stripes])  # 길이: 3+4+4+6+1 = 18
