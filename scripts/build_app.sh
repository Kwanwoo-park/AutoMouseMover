#!/bin/zsh
set -euo pipefail

ROOT_DIR="${0:A:h:h}"
APP_NAME="AutoMouseMover"
APP_DIR="$ROOT_DIR/dist/$APP_NAME.app"
BUILD_APP_DIR="/private/tmp/AutoMouseMoverBuild.app"
CONTENTS_DIR="$BUILD_APP_DIR/Contents"
MACOS_DIR="$CONTENTS_DIR/MacOS"
MODULE_CACHE_DIR="$ROOT_DIR/.build/ModuleCache"
COMPATIBLE_SDK="/Library/Developer/CommandLineTools/SDKs/MacOSX15.4.sdk"

if [[ -n "${SDKROOT:-}" ]]; then
  SDK_PATH="$SDKROOT"
elif [[ -d "$COMPATIBLE_SDK" ]]; then
  # 이 Mac의 최신 SDK와 Swift 패치 버전이 달라 호환되는 설치 SDK를 사용합니다.
  SDK_PATH="$COMPATIBLE_SDK"
else
  SDK_PATH="$(xcrun --sdk macosx --show-sdk-path)"
fi

mkdir -p "$MACOS_DIR" "$MODULE_CACHE_DIR"

swiftc \
  "$ROOT_DIR/native/AutoMouseMover.swift" \
  -o "$MACOS_DIR/AutoMouseMover" \
  -sdk "$SDK_PATH" \
  -target arm64-apple-macosx12.0 \
  -parse-as-library \
  -module-cache-path "$MODULE_CACHE_DIR" \
  -framework AppKit \
  -framework ApplicationServices

cp "$ROOT_DIR/native/Info.plist" "$CONTENTS_DIR/Info.plist"
chmod +x "$MACOS_DIR/AutoMouseMover"
xattr -cr "$BUILD_APP_DIR"
codesign --force --deep --sign - "$BUILD_APP_DIR"

mkdir -p "$ROOT_DIR/dist"
ditto "$BUILD_APP_DIR" "$APP_DIR"

echo "완료: $APP_DIR"
