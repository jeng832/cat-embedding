try:
    from .embedding import compare_images
    use_clip = True
    print("CLIP 모델 사용")
except ImportError:
    from .embedding_simple import compare_images_simple as compare_images
    use_clip = False
    print("간단한 픽셀 기반 비교 사용")

def main():
    print("Cat Embedding 시작!")
    try:
        sim, same = compare_images("cat1.jpg", "cat2.jpg")
        print(f"Similarity: {sim:.4f}")
        print("결과:", "같은 고양이 ✅" if same else "다른 고양이 ❌")
        if not use_clip:
            print("⚠️  주의: PyTorch/CLIP 미설치로 간단한 픽셀 비교만 수행됨")
    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    main()
