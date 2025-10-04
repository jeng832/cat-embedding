from PIL import Image
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def get_simple_embedding(image_path):
    """간단한 이미지 임베딩 (RGB 평균값 사용)"""
    try:
        image = Image.open(image_path).convert("RGB")
        # 이미지를 작은 크기로 리사이즈
        image = image.resize((64, 64))
        # RGB 픽셀 값을 평탄화하여 벡터로 변환
        pixels = np.array(image).flatten()
        # 정규화
        embedding = pixels / 255.0
        return embedding.reshape(1, -1)
    except Exception as e:
        print(f"이미지 로드 중 오류: {e}")
        return None

def compare_images_simple(img1, img2, threshold=0.9):
    """간단한 이미지 비교 (CLIP 없이)"""
    emb1 = get_simple_embedding(img1)
    emb2 = get_simple_embedding(img2)
    
    if emb1 is None or emb2 is None:
        return 0.0, False
    
    sim = cosine_similarity(emb1, emb2)[0][0]
    return sim, sim > threshold