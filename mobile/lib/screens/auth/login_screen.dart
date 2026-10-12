import 'package:flutter/material.dart';
import '../../core/services/api_service.dart';
import '../../core/services/storage_service.dart';
import '../../core/theme/app_theme.dart';
import '../admin/admin_navigation_screen.dart';
import '../main_navigation_screen.dart';
import '../owner/owner_navigation_screen.dart';
import 'register_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  // 3 Role Types: 'STUDENT', 'OWNER', 'ADMIN'
  String _selectedRole = 'STUDENT';

  final _emailController = TextEditingController(text: 'student@mitaoe.ac.in');
  final _passwordController = TextEditingController(text: 'Password123!');
  bool _rememberMe = true;
  bool _isLoading = false;
  bool _obscurePassword = true;
  String? _errorMessage;

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  void _onRoleChanged(String role) {
    setState(() {
      _selectedRole = role;
      _errorMessage = null;
      if (role == 'STUDENT') {
        _emailController.text = 'student@mitaoe.ac.in';
      } else if (role == 'OWNER') {
        _emailController.text = 'owner@sharmamess.com';
      } else if (role == 'ADMIN') {
        _emailController.text = 'admin@aaspaas.com';
      }
    });
  }

  Future<void> _handleLogin() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    final res = await ApiService.login(
      email: _emailController.text.trim(),
      password: _passwordController.text,
      role: _selectedRole,
    );

    if (!mounted) return;
    setState(() => _isLoading = false);

    if (res.success) {
      // Remember session state
      if (_rememberMe) {
        await StorageService.setUserRole(_selectedRole);
      }

      _routeToRoleDashboard(_selectedRole);
    } else {
      setState(() {
        _errorMessage = res.error ?? 'Invalid email or password';
      });
    }
  }

  void _routeToRoleDashboard(String role) {
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
  }

  void _showServerConfigDialog() {
    final controller = TextEditingController(text: StorageService.getBaseUrl());
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Server Configuration'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Set the backend API URL:',
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
            const SizedBox(height: 8),
            const Text(
              'Tip: Use 10.0.2.2:8000 for Android Emulator, or your local LAN IP for physical device testing.',
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
              if (!mounted) return;
              Navigator.pop(ctx);
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Server URL updated')),
              );
            },
            child: const Text('Save'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    Color activeRoleColor;
    IconData activeRoleIcon;
    String roleTitle;
    String roleSubtitle;

    if (_selectedRole == 'OWNER') {
      activeRoleColor = const Color(0xFF0F766E);
      activeRoleIcon = Icons.storefront_rounded;
      roleTitle = 'Shop Owner Portal';
      roleSubtitle = 'List your business, manage pricing, and offer student deals';
    } else if (_selectedRole == 'ADMIN') {
      activeRoleColor = const Color(0xFF1E293B);
      activeRoleIcon = Icons.admin_panel_settings_rounded;
      roleTitle = 'Administrator Login';
      roleSubtitle = 'Review business verifications, audits, and moderation';
    } else {
      activeRoleColor = AppTheme.primary;
      activeRoleIcon = Icons.school_rounded;
      roleTitle = 'Student Marketplace';
      roleSubtitle = 'Discover verified businesses, reviews & campus discounts';
    }

    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: Colors.white,
        actions: [
          IconButton(
            tooltip: 'Server Settings',
            icon: const Icon(Icons.settings_ethernet, color: AppTheme.textSecondary),
            onPressed: _showServerConfigDialog,
          ),
        ],
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 12.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Center(
                child: Container(
                  width: 68,
                  height: 68,
                  decoration: BoxDecoration(
                    color: activeRoleColor.withOpacity(0.12),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Icon(
                    activeRoleIcon,
                    size: 38,
                    color: activeRoleColor,
                  ),
                ),
              ),
              const SizedBox(height: 16),
              Center(
                child: Text(
                  roleTitle,
                  style: const TextStyle(
                    fontSize: 22,
                    fontWeight: FontWeight.w800,
                    color: AppTheme.textPrimary,
                  ),
                ),
              ),
              const SizedBox(height: 6),
              Center(
                child: Text(
                  roleSubtitle,
                  textAlign: TextAlign.center,
                  style: const TextStyle(fontSize: 13, color: AppTheme.textSecondary),
                ),
              ),
              const SizedBox(height: 24),

              // 3-Role Type Selector
              Container(
                padding: const EdgeInsets.all(4),
                decoration: BoxDecoration(
                  color: AppTheme.background,
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(color: AppTheme.border),
                ),
                child: Row(
                  children: [
                    _buildRoleSegment(
                      label: 'Student',
                      role: 'STUDENT',
                      icon: Icons.school_outlined,
                    ),
                    _buildRoleSegment(
                      label: 'Shop Owner',
                      role: 'OWNER',
                      icon: Icons.storefront_outlined,
                    ),
                    _buildRoleSegment(
                      label: 'Admin',
                      role: 'ADMIN',
                      icon: Icons.shield_outlined,
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 24),

              if (_errorMessage != null) ...[
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: AppTheme.error.withOpacity(0.08),
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(color: AppTheme.error.withOpacity(0.3)),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.error_outline, color: AppTheme.error, size: 20),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          _errorMessage!,
                          style: const TextStyle(color: AppTheme.error, fontSize: 13),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),
              ],

              // Email field
              Text(
                _selectedRole == 'STUDENT'
                    ? 'College Email'
                    : (_selectedRole == 'OWNER' ? 'Business Owner Email' : 'Admin Email'),
                style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: AppTheme.textPrimary),
              ),
              const SizedBox(height: 6),
              TextField(
                controller: _emailController,
                keyboardType: TextInputType.emailAddress,
                decoration: InputDecoration(
                  hintText: _selectedRole == 'STUDENT' ? 'name@mitaoe.ac.in' : 'email@address.com',
                  prefixIcon: const Icon(Icons.email_outlined, color: AppTheme.textMuted),
                ),
              ),
              const SizedBox(height: 16),

              // Password field
              const Text(
                'Password',
                style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: AppTheme.textPrimary),
              ),
              const SizedBox(height: 6),
              TextField(
                controller: _passwordController,
                obscureText: _obscurePassword,
                decoration: InputDecoration(
                  hintText: '••••••••',
                  prefixIcon: const Icon(Icons.lock_outline, color: AppTheme.textMuted),
                  suffixIcon: IconButton(
                    icon: Icon(
                      _obscurePassword ? Icons.visibility_off : Icons.visibility,
                      color: AppTheme.textMuted,
                    ),
                    onPressed: () => setState(() => _obscurePassword = !_obscurePassword),
                  ),
                ),
              ),
              const SizedBox(height: 14),

              // Remember Me Checkbox
              Row(
                children: [
                  Checkbox(
                    value: _rememberMe,
                    activeColor: activeRoleColor,
                    onChanged: (val) => setState(() => _rememberMe = val ?? true),
                  ),
                  const Text('Remember login on this device', style: TextStyle(fontSize: 13, color: AppTheme.textPrimary)),
                ],
              ),
              const SizedBox(height: 16),

              // Sign In Button
              ElevatedButton(
                style: ElevatedButton.styleFrom(backgroundColor: activeRoleColor),
                onPressed: _isLoading ? null : _handleLogin,
                child: _isLoading
                    ? const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                      )
                    : Text('Sign In as ${_selectedRole == "STUDENT" ? "Student" : (_selectedRole == "OWNER" ? "Shop Owner" : "Admin")}'),
              ),
              const SizedBox(height: 16),

              // Guest explore option for students
              if (_selectedRole == 'STUDENT') ...[
                OutlinedButton.icon(
                  icon: const Icon(Icons.explore_outlined, size: 18),
                  label: const Text('Explore Campus as Guest'),
                  onPressed: () {
                    _routeToRoleDashboard('STUDENT');
                  },
                ),
                const SizedBox(height: 20),
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Text("New student? ", style: TextStyle(color: AppTheme.textSecondary)),
                    GestureDetector(
                      onTap: () {
                        Navigator.of(context).push(
                          MaterialPageRoute(builder: (_) => const RegisterScreen()),
                        );
                      },
                      child: const Text(
                        'Register Here',
                        style: TextStyle(color: AppTheme.primary, fontWeight: FontWeight.w700),
                      ),
                    ),
                  ],
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildRoleSegment({
    required String label,
    required String role,
    required IconData icon,
  }) {
    final isSelected = _selectedRole == role;
    return Expanded(
      child: GestureDetector(
        onTap: () => _onRoleChanged(role),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 10),
          decoration: BoxDecoration(
            color: isSelected ? Colors.white : Colors.transparent,
            borderRadius: BorderRadius.circular(10),
            boxShadow: isSelected
                ? [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.06),
                      blurRadius: 4,
                      offset: const Offset(0, 2),
                    ),
                  ]
                : null,
          ),
          child: Column(
            children: [
              Icon(
                icon,
                size: 20,
                color: isSelected ? AppTheme.primary : AppTheme.textSecondary,
              ),
              const SizedBox(height: 4),
              Text(
                label,
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: isSelected ? FontWeight.bold : FontWeight.w500,
                  color: isSelected ? AppTheme.textPrimary : AppTheme.textSecondary,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
