@echo off
chcp 65001 >nul

REM Cat Embedding 실행 스크립트 (Windows)
REM 가상환경 설정부터 실행까지 자동화

echo 🐱 Cat Embedding 실행 시작...

REM 현재 디렉토리 확인
if not exist "pyproject.toml" (
    echo ❌ 오류: 프로젝트 루트 디렉토리에서 실행해주세요.
    pause
    exit /b 1
)

REM Python 버전 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 오류: Python이 설치되지 않았습니다.
    echo Python 3.8-3.12를 설치해주세요.
    pause
    exit /b 1
)

echo ✅ Python 버전:
python --version

REM Python 3.13 경고 (Windows에서는 간단한 경고만)
for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PYTHON_VERSION=%%v
if "%PYTHON_VERSION:~0,4%"=="3.13" (
    echo ⚠️  경고: Python 3.13 감지됨
    echo    PyTorch 호환성 문제로 인해 CLIP 모델을 사용할 수 없습니다.
    echo    최적 성능을 위해 Python 3.8-3.12 사용을 권장합니다.
    echo.
    set /p "CONTINUE=계속 진행하시겠습니까? (y/N): "
    if /i not "%CONTINUE%"=="y" (
        echo 설치가 취소되었습니다.
        echo Python 3.12 설치를 권장합니다.
        pause
        exit /b 1
    )
)

REM 가상환경 생성 (없을 경우)
if not exist "venv" (
    echo 📦 가상환경 생성 중...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ 가상환경 생성 실패
        pause
        exit /b 1
    )
    echo ✅ 가상환경 생성 완료
) else (
    echo ✅ 기존 가상환경 발견
)

REM 가상환경 활성화
echo 🔧 가상환경 활성화 중...
call venv\Scripts\activate.bat

REM 의존성 설치/업데이트
echo 📚 의존성 설치 중...
python -m pip install --upgrade pip
pip install -e .
if errorlevel 1 (
    echo ❌ 의존성 설치 실패
    pause
    exit /b 1
)
echo ✅ 의존성 설치 완료

REM 테스트 이미지 확인
if not exist "cat1.jpg" (
    echo ⚠️  경고: cat1.jpg 파일이 없습니다.
)
if not exist "cat2.jpg" (
    echo ⚠️  경고: cat2.jpg 파일이 없습니다.
)

REM 사용법 안내
echo.
echo 🚀 Cat Embedding 준비 완료!
echo ----------------------------------------
echo 💡 사용법:
echo.
echo 1. 갤러리 구축:
echo    cat-embedding build --meta metadata.json --out gallery.npz
echo.
echo 2. 쿼리 매칭:
echo    cat-embedding match --gallery gallery.npz --query query.json
echo.
echo 3. 도움말:
echo    cat-embedding --help
echo ----------------------------------------
echo.
echo 💡 팁:
echo    - 메타데이터 예시: test_metadata.json 참고
echo    - 쿼리 예시: query.json 참고
echo    - 가상환경 수동 활성화: venv\Scripts\activate
echo.
pause