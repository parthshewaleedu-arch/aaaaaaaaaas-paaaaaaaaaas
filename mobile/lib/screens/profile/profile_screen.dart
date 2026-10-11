import 'package:flutter/material.dart';
import '../../core/constants/api_constants.dart';
import '../../core/services/api_service.dart';
import '../../core/services/storage_service.dart';
import '../../core/theme/app_theme.dart';
import '../auth/login_screen.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  String _campusName = ApiConstants.defaultCampusName;
  String _baseUrl = ApiConstants.defaultBaseUrl;
  bool _isLoggedIn = false;

  @override
  void initState() {
    super.initState();
    _loadState();
  }

  void _loadState() {
    setState(() {
      _campusName = StorageService.getCampusName();
      _baseUrl = StorageService.getBaseUrl();
      _isLoggedIn = StorageService.hasValidSession();
    });
  }

  void _showServerConfigDialog() {
    final controller = TextEditingController(text: _baseUrl);
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Backend API URL'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Configure the FastAPI backend server address:',
              style: TextStyle(fontSize: 13, color: AppTheme.textSecondary),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: controller,
              decoration: const InputDecoration(
                hintText: 'http://10.0.2.2:8000/api/v1',
                labelText: 'Base URL',
              ),
            ),
            const SizedBox(height: 10),
            const Text(
              'Default options:\n• Android Emulator: http://10.0.2.2:8000/api/v1\n• Local Wi-Fi: http://192.168.x.x:8000/api/v1',
              style: TextStyle(fontSize: 11, color: AppTheme.textMuted),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () async {
              await StorageService.setBaseUrl(controller.text.trim());
              Navigator.pop(ctx);
              _loadState();
              if (!mounted) return;
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Server endpoint updated!')),
              );
            },
            child: const Text('Save'),
          ),
        ],
      ),
    );
  }

  Future<void> _handleLogout() async {
    await ApiService.logout();
    if (!mounted) return;
    Navigator.of(context).pushAndRemoveUntil(
      MaterialPageRoute(builder: (_) => const LoginScreen()),
      (route) => false,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: const Text('Student Profile'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Student Identity Card
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
                    child: const Icon(Icons.school_rounded, size: 38, color: AppTheme.primary),
                  ),
                  const SizedBox(height: 12),
                  const Text(
                    'Parth Shewale',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppTheme.textPrimary),
                  ),
                  const SizedBox(height: 2),
                  const Text(
                    'student@mitaoe.ac.in',
                    style: TextStyle(fontSize: 13, color: AppTheme.textSecondary),
                  ),
                  const SizedBox(height: 12),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                    decoration: BoxDecoration(
                      color: AppTheme.success.withOpacity(0.12),
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(color: AppTheme.success.withOpacity(0.3)),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: const [
                        Icon(Icons.verified, size: 16, color: AppTheme.success),
                        SizedBox(width: 6),
                        Text(
                          'Verified MIT AOE Student',
                          style: TextStyle(color: AppTheme.success, fontWeight: FontWeight.bold, fontSize: 12),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 20),

            // Campus Information Tile
            Container(
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: AppTheme.border),
              ),
              child: Column(
                children: [
                  ListTile(
                    leading: const Icon(Icons.location_city_rounded, color: AppTheme.primary),
                    title: const Text('Campus Context', style: TextStyle(fontWeight: FontWeight.w600, fontSize: 14)),
                    subtitle: Text(_campusName, style: const TextStyle(fontSize: 12, color: AppTheme.textSecondary)),
                    trailing: const Text('Pilot (3 km)', style: TextStyle(color: AppTheme.primary, fontWeight: FontWeight.bold, fontSize: 11)),
                  ),
                  const Divider(height: 1, color: AppTheme.border),
                  ListTile(
                    leading: const Icon(Icons.dns_rounded, color: AppTheme.primary),
                    title: const Text('Backend API Server', style: TextStyle(fontWeight: FontWeight.w600, fontSize: 14)),
                    subtitle: Text(_baseUrl, style: const TextStyle(fontSize: 12, color: AppTheme.textSecondary), overflow: TextOverflow.ellipsis),
                    trailing: const Icon(Icons.edit, size: 18, color: AppTheme.textSecondary),
                    onTap: _showServerConfigDialog,
                  ),
                ],
              ),
            ),

            const SizedBox(height: 20),

            // App Settings & Info Tile
            Container(
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: AppTheme.border),
              ),
              child: Column(
                children: [
                  ListTile(
                    leading: const Icon(Icons.security_rounded, color: AppTheme.primary),
                    title: const Text('Trust & Review Integrity', style: TextStyle(fontWeight: FontWeight.w600, fontSize: 14)),
                    subtitle: const Text('Zero fake reviews • Student verified only', style: TextStyle(fontSize: 12, color: AppTheme.textSecondary)),
                    onTap: () {},
                  ),
                  const Divider(height: 1, color: AppTheme.border),
                  ListTile(
                    leading: const Icon(Icons.info_outline_rounded, color: AppTheme.primary),
                    title: const Text('About AAS PAAS', style: TextStyle(fontWeight: FontWeight.w600, fontSize: 14)),
                    subtitle: const Text('v1.0.0 (Production Pilot)', style: TextStyle(fontSize: 12, color: AppTheme.textSecondary)),
                    trailing: const Text('MIT AOE', style: TextStyle(color: AppTheme.textMuted, fontSize: 12)),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 24),

            // Auth button (Logout / Login)
            if (_isLoggedIn)
              OutlinedButton.icon(
                style: OutlinedButton.styleFrom(
                  foregroundColor: AppTheme.error,
                  side: const BorderSide(color: AppTheme.error),
                ),
                icon: const Icon(Icons.logout, size: 18),
                label: const Text('Sign Out'),
                onPressed: _handleLogout,
              )
            else
              ElevatedButton.icon(
                icon: const Icon(Icons.login, size: 18),
                label: const Text('Sign In as Student'),
                onPressed: () {
                  Navigator.of(context).push(
                    MaterialPageRoute(builder: (_) => const LoginScreen()),
                  );
                },
              ),
          ],
        ),
      ),
    );
  }
}
