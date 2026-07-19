# AutoMouseMover

30초마다 마우스 커서를 1픽셀 움직였다가 원래 위치로 되돌려 화면 보호기 진입을 막습니다. 실제 클릭은 하지 않습니다.

## 독립 실행 앱

`dist/AutoMouseMover.app`을 더블클릭하면 VS Code나 터미널 없이 실행됩니다. 앱 창에서 일시 중지, 재시작, 종료할 수 있습니다.

독립 실행 앱의 UI와 마우스 제어는 `native/AutoMouseMover.swift`에 Swift/AppKit으로 구현되어 있습니다.

앱을 다시 빌드하려면 다음 명령을 실행합니다.

```bash
./scripts/build_app.sh
```

## Python 버전 실행

VS Code에서 `app/main.py`를 연 뒤 `F5`를 누르거나 터미널에서 실행합니다.

```bash
.venv/bin/python -m app.main
```

종료하려면 실행 중인 터미널에서 `Ctrl+C`를 누릅니다.

이동 간격을 바꾸려면 초 단위로 지정합니다.

```bash
.venv/bin/python -m app.main --interval 10
```

## macOS 권한

처음 실행할 때 macOS가 접근성 권한을 요청할 수 있습니다. 커서가 움직이지 않으면 다음 위치에서 VS Code 또는 Terminal의 권한을 켜 주세요.

`시스템 설정 → 개인정보 보호 및 보안 → 손쉬운 사용`

## 테스트

```bash
.venv/bin/python -m unittest discover -s tests -v
```
