@echo off
echo ========================================================
echo       AAS PAAS - Android Release APK Builder
echo ========================================================
echo.

where flutter >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Flutter SDK is not found in your system PATH.
    echo.
    echo To build this APK locally:
    echo 1. Download Flutter SDK from https://docs.flutter.dev/get-started/install/windows
    echo 2. Add 'flutter\bin' to your PATH environment variable.
    echo 3. Alternatively, push to your GitHub repo to trigger automated APK compilation via GitHub Actions!
    echo.
    pause
    exit /b 1
)

echo [1/3] Getting Flutter packages...
call flutter pub get

echo.
echo [2/3] Compiling Release APK...
call flutter build apk --release

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================================
    echo [SUCCESS] APK compiled successfully!
    echo Location: build\app\outputs\flutter-apk\app-release.apk
    echo ========================================================
) else (
    echo.
    echo [ERROR] APK build encountered an error.
)

pause
