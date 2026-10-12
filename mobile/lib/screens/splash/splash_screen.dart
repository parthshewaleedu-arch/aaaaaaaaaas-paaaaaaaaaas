import 'package:flutter/material.dart';
import '../../core/services/storage_service.dart';
import '../../core/theme/app_theme.dart';
import '../admin/admin_navigation_screen.dart';
import '../auth/login_screen.dart';
import '../main_navigation_screen.dart';
import '../owner/owner_navigation_screen.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() {
    super.initState();
    _checkInitialState();
  }

  Future<void> _checkInitialState() async {
    await StorageService.init();
    await Future.delayed(const Duration(milliseconds: 1000));

    if (!mounted) return;

    final hasSession = StorageService.hasValidSession();

    if (hasSession) {
      // Remembered session: Route directly to role-specific dashboard
      final role = StorageService.getUserRole();
      Widget target;
      if (role == 'OWNER') {
        target = const OwnerNavigationScreen();
      } else if (role == 'ADMIN') {
        target = const AdminNavigationScreen();
      } else {
        target = const MainNavigationScreen();
      }

      Navigator.of(context).pushReplacement(
        MaterialPageRoute(builder: (_) => target),
      );
    } else {
      // First time open or logged out: Show 3-role login window
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(builder: (_) => const LoginScreen()),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.primary,
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 96,
              height: 96,
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(24),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.15),
                    blurRadius: 20,
                    offset: const Offset(0, 10),
                  ),
                ],
              ),
              child: const Icon(
                Icons.location_on_rounded,
                size: 56,
                color: AppTheme.primary,
              ),
            ),
            const SizedBox(height: 24),
            const Text(
              'AAS PAAS',
              style: TextStyle(
                fontSize: 32,
                fontWeight: FontWeight.w900,
                color: Colors.white,
                letterSpacing: 2.0,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Everything You Need, Aas Paas.',
              style: TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.w500,
                color: Colors.white.withOpacity(0.85),
                letterSpacing: 0.5,
              ),
            ),
            const SizedBox(height: 48),
            const SizedBox(
              width: 28,
              height: 28,
              child: CircularProgressIndicator(
                strokeWidth: 2.5,
                valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
