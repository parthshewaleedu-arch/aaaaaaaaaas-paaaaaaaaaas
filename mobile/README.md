# AAS PAAS — Mobile Application (Flutter)

A cross-platform mobile marketplace application connecting verified college students with local campus businesses.

---

## 📱 Features

- **🎓 Campus Discovery**: Centered around MIT Academy of Engineering (MIT AOE), Alandi, Pune within an initial 3 km radius.
- **🔍 Intent-Driven Search**: Search mess, printing/xerox, cafes, laundry, medicals, salons, and repairs with natural keywords and multi-attribute filters.
- **⭐ Structured Review System**: Transparent 5-dimension rating breakdown (Food Quality, Hygiene, Quantity, Value for Money, Service).
- **🏷️ Exclusive Student Offers**: Browse verified student discounts and claim redemption passes.
- **🔖 Saved Bookmarks**: Save favorite campus spots for quick offline access.
- **⚙️ Live Backend Endpoint Config**: Easily switch backend URL between emulator (`10.0.2.2:8000`), local network IP (`192.168.x.x:8000`), or cloud deployment directly inside the app.

---

## 📦 How to Get the Downloadable APK

### Method 1: Instant Download via GitHub Actions (Recommended)
1. Push this repository to GitHub:
   ```bash
   git add .
   git commit -m "feat(mobile): add AAS PAAS Flutter application"
   git push origin main
   ```
2. Navigate to the **Actions** tab on [github.com/parthshewaleedu-arch/AAS-PAAS](https://github.com/parthshewaleedu-arch/AAS-PAAS).
3. The **Build Android APK** workflow automatically runs and compiles `app-release.apk`.
4. Click on the completed workflow run and download **`AAS-PAAS-Release-APK`**.

### Method 2: Local Build
1. Install [Flutter SDK](https://docs.flutter.dev/get-started/install/windows) (Flutter 3.x+).
2. Install Android Studio with Android SDK Command-line Tools and Build-Tools.
3. Open a terminal in `aas paas/mobile` and run:
   ```bash
   flutter pub get
   flutter build apk --release
   ```
4. Output file will be generated at:
   `build/app/outputs/flutter-apk/app-release.apk`
