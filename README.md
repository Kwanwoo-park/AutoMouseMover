# AutoMouseMover

설정한 간격마다 마우스 커서를 1픽셀 움직였다가 원래 위치로 되돌려 화면 보호기 진입을 막습니다. 실제 클릭은 하지 않습니다.

Windows에서는 단일 `.exe` GUI, macOS에서는 네이티브 `.app`, 두 운영체제 모두 Python CLI로 실행할 수 있습니다.

## Windows 실행 파일

빌드된 `dist/AutoMouseMover.exe`를 더블클릭하면 Python이나 터미널 없이 실행됩니다.

실행 창에서 다음 항목을 설정할 수 있습니다.

- 이동 간격: 마우스를 움직일 주기(초)
- 실행 시간: 자동으로 중지할 시간(분)
- 실행 시간 `0`: 사용자가 중지하거나 종료할 때까지 계속 실행
- 시작/재시작, 일시 중지, 종료

### EXE 빌드

필수 환경:

- Windows 10 이상
- Python 3.10 이상
- 인터넷 연결: 최초 PyInstaller 설치 시에만 필요

PowerShell에서 다음 명령을 실행합니다.

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build_exe.ps1
```

스크립트는 다음 작업을 자동으로 수행합니다.

1. `.venv`가 없으면 Python 가상환경 생성
2. `requirements-build.txt`의 PyInstaller 설치
3. 콘솔 창이 없는 단일 `dist/AutoMouseMover.exe` 생성

이미 빌드 의존성이 설치되어 있다면 재설치를 생략할 수 있습니다.

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build_exe.ps1 -SkipDependencyInstall
```

> Windows용 EXE는 Windows에서 빌드해야 합니다. 생성된 EXE를 실행하는 PC에는 Python이 필요하지 않습니다.

현재 빌드는 코드 서명을 포함하지 않으므로 다른 PC에 배포하면 Windows가 `알 수 없는 게시자` 경고를 표시할 수 있습니다. 외부 배포용 빌드는 신뢰할 수 있는 코드 서명 인증서로 서명하는 것을 권장합니다.

## Python CLI 실행

Windows:

```powershell
.\.venv\Scripts\python.exe -m app.main
```

macOS:

```bash
.venv/bin/python -m app.main
```

종료하려면 실행 중인 터미널에서 `Ctrl+C`를 누릅니다. 이동 간격을 바꾸려면 초 단위로 지정합니다.

```powershell
.\.venv\Scripts\python.exe -m app.main --interval 10
```

Python 코드는 실행 중인 운영체제를 확인해 macOS CoreGraphics 또는 Windows Win32 API를 자동으로 선택합니다.

## macOS 독립 실행 앱

`dist/AutoMouseMover.app`을 더블클릭하면 VS Code나 터미널 없이 실행됩니다. 앱 창에서 실행 시간을 분 단위로 입력한 뒤 재시작하면 설정이 적용됩니다. `0`을 입력하면 종료 버튼을 누를 때까지 계속 실행됩니다.

네이티브 앱의 UI와 마우스 제어는 `native/AutoMouseMover.swift`에 구현되어 있습니다.

```bash
./scripts/build_app.sh
```

### macOS 권한

처음 실행할 때 macOS가 접근성 권한을 요청할 수 있습니다. 커서가 움직이지 않으면 다음 위치에서 AutoMouseMover 또는 실행에 사용한 Terminal의 권한을 켜 주세요.

`시스템 설정 → 개인정보 보호 및 보안 → 손쉬운 사용`

## 테스트

Windows:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

macOS:

```bash
.venv/bin/python -m unittest discover -s tests -v
```

## 주요 파일

- `app/main.py`: macOS/Windows 공용 CLI와 마우스 제어
- `app/windows_app.py`: Windows GUI 진입점
- `AutoMouseMover.spec`: PyInstaller 패키징 설정
- `scripts/build_exe.ps1`: Windows EXE 빌드 자동화
- `native/AutoMouseMover.swift`: macOS 네이티브 앱
- `scripts/build_app.sh`: macOS APP 빌드 자동화
