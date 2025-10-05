# src/cat_embedding/schema.py
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

EarTip = Literal["none", "left", "right"]
NoseColor = Literal["pink", "black", "spotted", "other"]
EyeColor  = Literal["yellow", "green", "blue", "other"]
CoatType  = Literal["black", "ginger_tabby", "tuxedo", "calico", "white", "other"]

class CatMeta(BaseModel):
    # 레이블(학습/평가용). 실제 서비스에서는 없을 수 있음.
    cat_id: Optional[str] = Field(default=None, description="개체 식별자(알려진 경우)")

    # 파일/촬영 정보
    image_path: str
    timestamp: Optional[datetime] = None

    # 위치(정규화 전 원값)
    lat: Optional[float] = None
    lon: Optional[float] = None

    # 객관적 특징들
    ear_tip: EarTip = "none"       # TNR: none/left/right
    nose_color: NoseColor = "other"
    eye_color: EyeColor = "other"
    coat_type: CoatType = "other"  # 큰 카테고리
    has_stripes: bool = False      # 줄무늬 여부
