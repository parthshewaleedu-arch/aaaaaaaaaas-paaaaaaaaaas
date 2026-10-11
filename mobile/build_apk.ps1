# AAS PAAS Android APK Build Script (PowerShell)
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "       AAS PAAS - Android Release APK Builder           " -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

if (-not (Get-Command flutter -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Flutter SDK is not detected in your PATH." -ForegroundColor Red
    Write-Host ""
    Write-Host "Options to get your downloadable APK:" -ForegroundColor Yellow
    Write-Host "1. Automated Cloud Build: Push code to GitHub repository (github.com/parthshewaleedu-arch/AAS-PAAS)."
    Write-Host "   The GitHub Actions workflow (.github/workflows/build-apk.yml) compiles app-release.apk automatically!"
    Write-Host "2. Local Build: Install Flutter from https://flutter.dev and run this script again."
    Write-Host ""
    exit 1
}

Write-Host "[1/3] Resolving dependencies with 'flutter pub get'..." -ForegroundColor Green
flutter pub get

Write-Host "[2/3] Compiling Release APK..." -ForegroundColor Green
flutter build apk --release

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "[SUCCESS] APK generated successfully!" -ForegroundColor Green
    Write-Host "Output: $(Get-Location)\build\app\outputs\flutter-apk\app-release.apk" -ForegroundColor Cyan
} else {
    Write-Host "[ERROR] APK compilation failed." -ForegroundColor Red
}
