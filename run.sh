#!/bin/bash

# Cat Embedding 실행 스크립트
# 가상환경 설정부터 실행까지 자동화

set -e  # 에러 발생 시 스크립트 종료

echo "🐱 Cat Embedding 실행 시작..."

# 현재 디렉토리 확인
if [ ! -f "pyproject.toml" ]; then
    echo "❌ 오류: 프로젝트 루트 디렉토리에서 실행해주세요."
    exit 1
fi

# Python 버전 확인 (3.12 우선 사용)
PYTHON_CMD=""
if command -v python3.12 &> /dev/null; then
    PYTHON_CMD="python3.12"
    echo "✅ Python 3.12 발견"
elif command -v python3.11 &> /dev/null; then
    PYTHON_CMD="python3.11"
    echo "✅ Python 3.11 발견"
elif command -v python3.10 &> /dev/null; then
    PYTHON_CMD="python3.10"
    echo "✅ Python 3.10 발견"
elif command -v python3.9 &> /dev/null; then
    PYTHON_CMD="python3.9"
    echo "✅ Python 3.9 발견"
elif command -v python3.8 &> /dev/null; then
    PYTHON_CMD="python3.8"
    echo "✅ Python 3.8 발견"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    echo "⚠️  일반 python3 사용 (버전 확인 필요)"
else
    echo "❌ 오류: Python 3가 설치되지 않았습니다."
    echo "Python 3.8-3.12를 설치해주세요."
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version | cut -d' ' -f2)
echo "✅ 사용할 Python: $PYTHON_CMD ($PYTHON_VERSION)"

# Python 3.13 경고
if [[ $PYTHON_VERSION == 3.13* ]]; then
    echo "⚠️  경고: Python 3.13 감지됨"
    echo "   PyTorch 호환성 문제로 인해 CLIP 모델을 사용할 수 없습니다."
    echo "   최적 성능을 위해 Python 3.8-3.12 사용을 권장합니다."
    echo ""
    read -p "계속 진행하시겠습니까? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "설치가 취소되었습니다."
        echo "Python 3.12 설치 방법:"
        echo "  pyenv install 3.12.7 && pyenv local 3.12.7"
        exit 1
    fi
fi

# 가상환경 생성 (없을 경우)
if [ ! -d "venv" ]; then
    echo "📦 가상환경 생성 중..."
    $PYTHON_CMD -m venv venv
    echo "✅ 가상환경 생성 완료"
else
    echo "✅ 기존 가상환경 발견"
fi

# 가상환경 활성화
echo "🔧 가상환경 활성화 중..."
source venv/bin/activate

# 의존성 설치/업데이트
echo "📚 의존성 설치 중..."
pip install --upgrade pip
pip install -e .
echo "✅ 의존성 설치 완료"

# 필수 파일 확인 및 안내
echo "📋 필수 파일 확인 중..."

# 이미지 파일 확인
if [ ! -f "cat1.jpg" ] || [ ! -f "cat2.jpg" ]; then
    echo "⚠️  경고: cat1.jpg 또는 cat2.jpg 파일이 없습니다."
    echo "   테스트 이미지를 프로젝트 루트에 준비해주세요."
fi

# 메타데이터 파일 확인
if [ ! -f "metadata.json" ]; then
    echo "ℹ️  메타데이터 파일이 없습니다."
    echo "   다음 명령어로 예시 파일을 생성할 수 있습니다:"
    echo ""
    echo "   cat > metadata.json << 'EOF'"
    echo "["
    echo "  {"
    echo "    \"cat_id\": \"cat_001\","
    echo "    \"image_path\": \"cat1.jpg\","
    echo "    \"timestamp\": \"2024-10-04T10:00:00\","
    echo "    \"lat\": 37.5665,"
    echo "    \"lon\": 126.9780,"
    echo "    \"ear_tip\": \"left\","
    echo "    \"nose_color\": \"pink\","
    echo "    \"eye_color\": \"yellow\","
    echo "    \"coat_type\": \"ginger_tabby\","
    echo "    \"has_stripes\": true"
    echo "  }"
    echo "]"
    echo "EOF"
    echo ""
fi

# 사용법 안내
echo ""
echo "🚀 Cat Embedding 준비 완료!"
echo "----------------------------------------"
echo "💡 사용법:"
echo ""
echo "🚀 빠른 시작 (권장):"
echo "   cat-embedding init --with-images    # 이미지 파일 자동 감지 및 초기화"
echo "   cat-embedding init                  # 예시 파일 생성"
echo ""
echo "📋 전체 워크플로우:"
echo "1. 프로젝트 초기화:"
echo "   cat-embedding init --with-images"
echo ""
echo "2. 갤러리 구축 (수동):"
echo "   cat-embedding build --meta metadata.json --out gallery.npz"
echo ""
echo "3. 쿼리 매칭:"
echo "   cat-embedding match --gallery gallery.npz --query query.json"
echo ""
echo "4. 임베딩 데이터 정리:"
echo "   cat-embedding clean --all"
echo ""
echo "5. 도움말:"
echo "   cat-embedding --help"
echo "----------------------------------------"
echo ""
echo "💡 팁:"
echo "   - 메타데이터 예시: test_metadata.json 참고"
echo "   - 쿼리 예시: query.json 참고"
echo ""
echo "🔄 대화형 모드로 전환합니다..."
echo "가상환경이 활성화된 상태로 셸을 시작합니다."
echo "종료하려면 'exit' 또는 Ctrl+D를 누르세요."
echo ""

# 대화형 셸 시작 (venv 활성화 상태 유지)
exec bash