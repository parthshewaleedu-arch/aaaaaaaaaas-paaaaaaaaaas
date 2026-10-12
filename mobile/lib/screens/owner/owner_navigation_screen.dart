import 'package:flutter/material.dart';
import '../../core/services/storage_service.dart';
import '../../core/theme/app_theme.dart';
import '../auth/login_screen.dart';
import 'owner_dashboard_screen.dart';
import 'owner_business_screen.dart';
import 'owner_services_screen.dart';
import 'owner_offers_screen.dart';

class OwnerNavigationScreen extends StatefulWidget {
  final int initialIndex;
  const OwnerNavigationScreen({super.key, this.initialIndex = 0});

  @override
  State<OwnerNavigationScreen> createState() => _OwnerNavigationScreenState();
}

class _OwnerNavigationScreenState extends State<OwnerNavigationScreen> {
  late int _currentIndex;

  @override
  void initState() {
    super.initState();
    _currentIndex = widget.initialIndex;
  }

  void switchTab(int index) {
    setState(() => _currentIndex = index);
  }

  Future<void> _handleLogout() async {
    await StorageService.clearSession();
    if (!mounted) return;
    Navigator.of(context).pushAndRemoveUntil(
      MaterialPageRoute(builder: (_) => const LoginScreen()),
      (route) => false,
    );
  }

  @override
  Widget build(BuildContext context) {
    final screens = [
      OwnerDashboardScreen(onNavigateTab: switchTab),
      const OwnerBusinessScreen(),
      const OwnerServicesScreen(),
      const OwnerOffersScreen(),
      _buildOwnerAccountScreen(),
    ];

    return Scaffold(
      body: IndexedStack(
        index: _currentIndex,
        children: screens,
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) => setState(() => _currentIndex = index),
        type: BottomNavigationBarType.fixed,
        selectedItemColor: AppTheme.primary,
        unselectedItemColor: AppTheme.textSecondary,
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.dashboard_outlined),
            activeIcon: Icon(Icons.dashboard_rounded),
            label: 'Overview',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.storefront_outlined),
            activeIcon: Icon(Icons.storefront_rounded),
            label: 'My Shop',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.receipt_long_outlined),
            activeIcon: Icon(Icons.receipt_long_rounded),
            label: 'Services & Rates',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.local_offer_outlined),
            activeIcon: Icon(Icons.local_offer_rounded),
            label: 'Deals',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.manage_accounts_outlined),
            activeIcon: Icon(Icons.manage_accounts_rounded),
            label: 'Account',
          ),
        ],
      ),
    );
  }

  Widget _buildOwnerAccountScreen() {
    final email = StorageService.getCurrentUserEmail();
    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: const Text('Business Owner Account'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: AppTheme.border),
              ),
              child: Column(
                children: [
                  CircleAvatar(
                    radius: 36,
                    backgroundColor: AppTheme.primary.withOpacity(0.12),
                    child: const Icon(Icons.store_mall_directory_rounded, size: 36, color: AppTheme.primary),
                  ),
                  const SizedBox(height: 12),
                  Text(email.isEmpty ? 'Campus Business Partner' : email, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 8),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color: AppTheme.success.withOpacity(0.12),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: const Text('Role: Shop Owner', style: TextStyle(color: AppTheme.success, fontWeight: FontWeight.bold, fontSize: 12)),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),
            OutlinedButton.icon(
              style: OutlinedButton.styleFrom(
                foregroundColor: AppTheme.error,
                side: const BorderSide(color: AppTheme.error),
              ),
              icon: const Icon(Icons.logout, size: 18),
              label: const Text('Sign Out'),
              onPressed: _handleLogout,
            ),
          ],
        ),
      ),
    );
  }
}
