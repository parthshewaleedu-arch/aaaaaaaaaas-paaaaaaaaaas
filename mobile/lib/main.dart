import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'core/services/storage_service.dart';
import 'core/theme/app_theme.dart';
import 'screens/splash/splash_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Set status bar colors
  SystemChrome.setSystemUIOverlayStyle(
    const SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
      statusBarIconBrightness: Brightness.dark,
    ),
  );

  // Initialize persistent storage
  await StorageService.init();

  runApp(const AasPaasApp());
}

class AasPaasApp extends StatelessWidget {
  const AasPaasApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AAS PAAS',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      home: const SplashScreen(),
    );
  }
}
