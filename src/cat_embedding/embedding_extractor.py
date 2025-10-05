# src/cat_embedding/embedding_extractor.py
import numpy as np
from PIL import Image
from sklearn.metrics.pairwise import cosine_similarity

# PyTorch/CLIP fallback 처리
try:
    import torch, clip
    _device = "cuda" if torch.cuda.is_available() else "cpu"
    _model, _preprocess = clip.load("ViT-B/32", device=_device)
    CLIP_AVAILABLE = True
    print("✅ CLIP 모델 로드됨")
except ImportError:
    CLIP_AVAILABLE = False
    print("⚠️  PyTorch/CLIP 미설치 - 간단한 픽셀 임베딩 사용")

def _simple_image_embedding(path: str) -> np.ndarray:
    """간단한 픽셀 기반 임베딩 (CLIP 대체용)"""
    try:
        image = Image.open(path).convert("RGB")
        # 이미지를 작은 크기로 리사이즈
        image = image.resize((64, 64))
        # RGB 픽셀 값을 평탄화하여 벡터로 변환
        pixels = np.array(image).flatten()
        # 정규화
        embedding = pixels / 255.0
        # L2 정규화
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        return embedding
    except Exception as e:
        print(f"이미지 로드 중 오류: {e}")
        return np.random.randn(12288)  # 64*64*3 크기

def image_embedding(path: str) -> np.ndarray:
    if CLIP_AVAILABLE:
        img = _preprocess(Image.open(path).convert("RGB")).unsqueeze(0).to(_device)
        with torch.no_grad():
            emb = _model.encode_image(img).cpu().numpy()  # (1, 512) 또는 (1, 768)
        return emb[0]
    else:
        return _simple_image_embedding(path)
