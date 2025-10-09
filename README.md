# 🐱 Cat Embedding

고양이 이미지 임베딩 및 유사도 비교 도구

이 프로젝트는 두 고양이 이미지를 비교하여 같은 고양이인지 판별하는 Python 패키지입니다.

## ✨ 주요 기능

- 🎯 **이미지 임베딩**: CLIP 모델 기반 고품질 이미지 벡터화
- 📊 **유사도 계산**: 코사인 유사도를 통한 정확한 비교
- 🔄 **Fallback 지원**: PyTorch 미설치 시 픽셀 기반 비교로 자동 전환
- 🖥️ **콘솔 명령어**: 간편한 CLI 인터페이스

## 🚀 빠른 시작

### 설치 및 실행

```bash
# 저장소 클론
git clone https://github.com/jeng832/cat-embedding.git
cd cat-embedding

# 자동 설정 및 대화형 모드 시작
./run.sh

# 또는 수동 설정
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e .
cat-embedding
```

## 📋 요구사항

- **Python 3.8 이상, 3.13 미만** (PyTorch 호환성으로 인한 제한)
- 비교할 고양이 이미지 파일

## 🛠️ 의존성

### 필수 패키지
- `rich` - 콘솔 출력 향상
- `pillow` - 이미지 처리
- `scikit-learn` - 머신러닝 유틸리티
- `numpy` - 수치 계산

### 고품질 임베딩용 (포함됨)
- `torch` - PyTorch (딥러닝 프레임워크)
- `clip-by-openai` - OpenAI CLIP 모델 (멀티모달 임베딩)

> **중요**: Python 3.13에서는 PyTorch 호환성 문제로 인해 자동으로 픽셀 기반 fallback을 사용합니다. 최적 성능을 위해 Python 3.8-3.12를 사용하세요.

## 💻 사용법

### 🚀 빠른 시작 (권장)

**첫 사용자라면 이 방법을 사용하세요:**

```bash
# 1. 프로젝트 초기화 (이미지 파일이 있는 경우)
cat-embedding init --with-images

# 2. 바로 매칭 테스트
cat-embedding match --gallery gallery.npz --query query.json
```

**이미지 파일이 없는 경우:**
```bash
# 1. 예시 파일 생성
cat-embedding init

# 2. 갤러리 구축
cat-embedding build --meta metadata.json --out gallery.npz

# 3. 쿼리 매칭
cat-embedding match --gallery gallery.npz --query query.json
```

### 📋 전체 명령어 목록

**프로젝트 초기화:**
```bash
cat-embedding init                    # 예시 파일 생성
cat-embedding init --with-images      # 이미지 파일 자동 감지 및 초기화
```

**갤러리 관리:**
```bash
# 자동 bounds로 갤러리 구축 (권장)
cat-embedding build --meta metadata.json --out gallery.npz

# 수동 bounds 지정으로 갤러리 구축
cat-embedding build --meta metadata.json --out gallery.npz --bounds "[37.513261,37.5685,126.979,127.100134]"

# 자동 bounds로 매칭 (권장)
cat-embedding match --gallery gallery.npz --query query.json

# 수동 bounds 지정으로 매칭
cat-embedding match --gallery gallery.npz --query query.json --bounds "[37.513261,37.5685,126.979,127.100134]"

cat-embedding clean --all            # 모든 임베딩 파일 삭제
```

### 🔧 고급 사용법

**1. 콘솔 명령어 (권장)**
```bash
cat-embedding
```

**2. Python 모듈로 실행**
```bash
python -m cat_embedding
```

**3. 프로그래밍 방식으로 사용**
```python
from cat_embedding import main

# 메인 함수 실행
main()

# 또는 직접 함수 호출
try:
    from cat_embedding.embedding import compare_images
except ImportError:
    from cat_embedding.embedding_simple import compare_images_simple as compare_images

similarity, is_same = compare_images("cat1.jpg", "cat2.jpg")
print(f"유사도: {similarity:.4f}")
print("결과:", "같은 고양이 ✅" if is_same else "다른 고양이 ❌")
```

## 📊 출력 예시

```
간단한 픽셀 기반 비교 사용
Cat Embedding 시작!
Similarity: 0.9498
결과: 같은 고양이 ✅
⚠️  주의: PyTorch/CLIP 미설치로 간단한 픽셀 비교만 수행됨
```

## 🔧 개발 환경 설정

### 개발 의존성 설치
```bash
pip install -e ".[dev]"
```

### 코드 품질 검사
```bash
# 린팅
ruff check .

# 포맷팅
ruff format .
```

### 테스트 실행
```bash
pytest
```

## 📁 프로젝트 구조

```
cat-embedding/
├── pyproject.toml          # 패키지 설정
├── requirements.txt        # 의존성 목록
├── src/
│   └── cat_embedding/      # 메인 패키지
│       ├── __init__.py
│       ├── __main__.py     # CLI 진입점
│       ├── embedding.py    # CLIP 기반 임베딩
│       └── embedding_simple.py # 픽셀 기반 비교
├── cat1.jpg               # 테스트 이미지 1
├── cat2.jpg               # 테스트 이미지 2
└── README.md
```

## ⚙️ 설정

### 임계값 조정
기본 유사도 임계값은 0.8입니다. 코드에서 수정할 수 있습니다:

```python
# embedding.py 또는 embedding_simple.py에서
def compare_images(img1, img2, threshold=0.9):  # 임계값 변경
    # ...
```

### 이미지 파일 변경
현재는 `cat1.jpg`, `cat2.jpg`로 하드코딩되어 있습니다. 다른 이미지를 사용하려면 `__main__.py`를 수정하세요.

## 🧭 매칭 결과에 따른 후속 조치

### 1) 기존 개체로 판정된 경우 (`pred` != `"UNKNOWN"`)
- **의미**: 새 사진이 갤러리의 어떤 `cat_id`와 충분히 유사합니다.
- **권장 동작**:
  1) 메타데이터(`metadata.json` 또는 `.jsonl`)에 같은 `cat_id`로 새 사진을 추가합니다.
  2) 갤러리를 재생성합니다: 
     ```bash
     cat-embedding build --meta metadata.json --out gallery.npz
     ```

예시(append):
```json
{
  "cat_id": "cat_001",
  "image_path": "path/to/new_photo.jpg",
  "lat": 37.5665,
  "lon": 126.9780,
  "ear_tip": "left",
  "nose_color": "pink",
  "eye_color": "yellow",
  "coat_type": "ginger_tabby",
  "has_stripes": true
}
```

### 2) 새로운 개체로 판정된 경우 (`pred` == `"UNKNOWN"`)

**🆕 자동 추가 기능 (권장):**
- 새로운 개체로 감지되면 자동으로 갤러리에 추가 제안
- 사용자 확인 후 메타데이터 자동 업데이트 및 갤러리 재구축
- 새로운 ID 자동 생성 (`cat_003`, `cat_004` 등)

```bash
# 새로운 개체 감지 시 자동 처리
cat-embedding match --gallery gallery.npz --query query.json

# 출력 예시:
{"pred": "UNKNOWN", "sim": 0.65}

🆕 새로운 개체로 확인되었습니다! (유사도: 0.6500)
이 개체를 갤러리에 추가하시겠습니까?
📝 추가할 개체 정보:
   - ID: cat_003
   - 이미지: cat1.jpg
   - 위치: (37.5665, 126.978)

metadata.json에 추가하고 갤러리를 재구축하시겠습니까? (y/N): y
✅ metadata.json에 cat_003 추가됨
🔄 갤러리 재구축 중...
✅ 갤러리 재구축 완료: gallery.npz
💡 이제 cat_003로 매칭할 수 있습니다!
```

**수동 처리 (고급 사용자):**
- **의미**: 갤러리에 유사한 개체가 없습니다(오픈셋).
- **권장 동작**:
  1) 새 `cat_id`를 부여해 메타데이터에 등록합니다.
  2) 가능하면 여러 장을 수집하여 멀티샷 쿼리/갤러리로 품질을 높입니다.
  3) 갤러리를 재생성합니다:
     ```bash
     cat-embedding build --meta metadata.json --out gallery.npz
     ```

예시(append):
```json
{
  "cat_id": "cat_123",
  "image_path": "path/to/new_photo.jpg",
  "lat": 37.5665,
  "lon": 126.9780,
  "ear_tip": "none",
  "nose_color": "other",
  "eye_color": "other",
  "coat_type": "other",
  "has_stripes": false
}
```

매칭 실행 예:
```bash
cat-embedding match --gallery gallery.npz --query query.json --thr 0.80 --margin 0.05
# 출력: {"pred": "cat_001", "sim": 0.93}  또는  {"pred": "UNKNOWN", "sim": 0.67}
```

추가 팁:
- 멀티샷 쿼리(여러 장 평균 임베딩): `query.json`을 배열 형태로 제공하세요.
- 위치 정보가 유효하면 `--bounds '[minLat,maxLat,minLon,maxLon]'`로 정규화 범위를 지정하면 도움이 됩니다.
- 애매한 케이스에서는 `--thr`(임계값)과 `--margin`(마진)을 조정해 보세요.

### 📍 위치 정보 정규화 (--bounds 옵션)

위치 정보를 임베딩에 포함하여 지리적 근접성을 고려한 매칭을 수행할 수 있습니다.

**기본 사용법:**
```bash
# 갤러리 구축 시 bounds 지정
cat-embedding build --meta metadata.json --out gallery.npz --bounds "[37.513261,37.5685,126.979,127.100134]"

# 매칭 시 bounds 지정
cat-embedding match --gallery gallery.npz --query query.json --bounds "[37.513261,37.5685,126.979,127.100134]"
```

**bounds 형식:**
- `[min_lat, max_lat, min_lon, max_lon]` (JSON 배열)
- 위경도 좌표를 0~1 범위로 정규화하는 데 사용
- 갤러리의 모든 고양이 위치를 포함하는 범위여야 함

**자동 bounds 설정:**
- `--bounds` 옵션을 생략하면 메타데이터의 위치 정보를 기반으로 자동 계산
- 위치 정보가 없으면 위치 기반 매칭은 비활성화됨

**위치 정보 가중치:**
- CLIP 임베딩: 85%
- 위치 정보: 5% 
- 인간 정의 특징: 10%

**예시 - 서울 지역 고양이들:**
```bash
# 서울 지역 bounds (강남구~서초구)
--bounds "[37.513261,37.5685,126.979,127.100134]"

# 전국 단위 bounds (한반도 전체)
--bounds "[33.0,38.5,124.0,132.0]"
```

### 🗑️ 임베딩 데이터 정리

```bash
# 특정 갤러리 파일 삭제
cat-embedding clean --gallery gallery.npz

# 모든 임베딩 관련 파일 삭제 (확인 후)
cat-embedding clean --all

# 강제 삭제 (확인 없이)
cat-embedding clean --all --force
```

**삭제되는 파일들:**
- `.npz` 파일 (갤러리, 임베딩 벡터)
- `*_gallery*.npz`, `*_embedding*.npz` 패턴
- `test_metadata.json`, `query.json`, `metadata.json` (--all 옵션 시)

### 📍 위치 데이터(EXIF GPS)

- **자동 추출**: 메타데이터에 `lat`/`lon`이 누락되었거나 `null`이면, 이미지의 EXIF GPS에서 위경도를 자동으로 추출해 사용합니다.
- **우선순위**: 메타데이터에 `lat`/`lon`이 명시되어 있으면 EXIF값보다 메타데이터 값을 사용합니다.
- **없을 때의 처리**: EXIF GPS가 없거나 파싱에 실패하면 위치 벡터는 0으로 처리됩니다(위치 정보 비사용과 동일).
- **정규화 범위**: `--bounds '[minLat,maxLat,minLon,maxLon]'`를 지정하면 위치를 구간 내에서 0~1로 정규화합니다.
- **주의**: 일부 편집/리사이즈 도구는 EXIF를 제거합니다. 이미지에 GPS가 포함되어 있어야 자동 추출이 가능합니다.

예시(위치 누락 → EXIF 사용):

```json
{
  "cat_id": "cat_001",
  "image_path": "path/to/photo_with_gps.jpg",
  "ear_tip": "left",
  "nose_color": "pink",
  "eye_color": "yellow",
  "coat_type": "ginger_tabby",
  "has_stripes": true
}
```

## 🔗 관련 링크

- [OpenAI CLIP](https://github.com/openai/CLIP)
- [PyTorch](https://pytorch.org/)
- [Python Packaging Guide](https://packaging.python.org/)

## ⚠️ 알려진 이슈

- **Python 3.13 제한**: PyTorch가 아직 Python 3.13을 공식 지원하지 않아 **Python 3.8-3.12 사용을 강력히 권장**합니다.
- **GPU 지원**: 현재는 CPU만 지원하며, GPU 가속은 향후 업데이트에서 추가될 예정입니다.

### Python 버전 변경 방법

현재 Python 3.13을 사용 중이라면 다음과 같이 변경하세요:

```bash
# pyenv 사용 (권장)
pyenv install 3.12.7
pyenv local 3.12.7

# 또는 새로운 가상환경 생성
python3.12 -m venv venv_312
source venv_312/bin/activate
pip install -e .
```

## 🐾 예시 이미지 설명 및 임베딩 정보

아래 표는 레포지토리 루트의 `cat1.jpg`, `cat2.jpg`에 대한 사람 정의 특징(임베딩 구성 요소)을 요약합니다.

| 특징 | cat1.jpg | cat2.jpg | cat3.jpg |
|---|---|---|---|
| **이미지** | ![cat1.jpg](cat1.jpg) | ![cat2.jpg](cat2.jpg) | ![cat3.jpg](cat3.jpg) |
| **TNR 여부** | 없음 | 없음 | 없음 |
| **코 색깔** | pink | pink | pink |
| **눈 색깔** | other | yellow | yellow |
| **털 모양** | ginger_tabby | tuxedo | ginger_tabby |
| **줄무늬 여부** | 예 | 예 | 예 |
| **위치 정보** | 없음 | 없음 | 37.513261, 127.100134 |

---

🤖 Generated with [Claude Code](https://claude.ai/code)