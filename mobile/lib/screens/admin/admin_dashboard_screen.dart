import 'package:flutter/material.dart';
import '../../core/services/api_service.dart';
import '../../core/theme/app_theme.dart';

class AdminDashboardScreen extends StatefulWidget {
  final Function(int) onNavigateTab;
  const AdminDashboardScreen({super.key, required this.onNavigateTab});

  @override
  State<AdminDashboardScreen> createState() => _AdminDashboardScreenState();
}

class _AdminDashboardScreenState extends State<AdminDashboardScreen> {
  bool _isLoading = false;
  int _totalStudents = 1842;
  int _totalBusinesses = 68;
  int _totalReviews = 892;
  int _pendingVerifications = 3;

  @override
  void initState() {
    super.initState();
    _fetchKpis();
  }

  Future<void> _fetchKpis() async {
    setState(() => _isLoading = true);
    final res = await ApiService.getAdminDashboard();
    if (res.success && res.data != null) {
      final d = res.data!['data'];
      if (d != null) {
        _totalStudents = d['total_students'] ?? _totalStudents;
        _totalBusinesses = d['total_businesses'] ?? _totalBusinesses;
        _totalReviews = d['total_reviews'] ?? _totalReviews;
        _pendingVerifications = d['pending_verifications'] ?? _pendingVerifications;
      }
    }
    if (mounted) setState(() => _isLoading = false);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: const Text('Platform Administrator'),
      ),
      body: RefreshIndicator(
        onRefresh: _fetchKpis,
        color: AppTheme.primary,
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Admin Header
              Container(
                padding: const EdgeInsets.all(18),
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [Color(0xFF1E293B), Color(0xFF334155)],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('AAS PAAS CONTROL CENTER', style: TextStyle(color: Colors.white70, fontSize: 11, fontWeight: FontWeight.bold, letterSpacing: 1.2)),
                    const SizedBox(height: 6),
                    const Text('Pilot: MIT AOE, Alandi (Pune)', style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.w800)),
                    const SizedBox(height: 4),
                    const Text('Monitor campus marketplace integrity, business approvals, and dispute moderation.', style: TextStyle(color: Colors.white70, fontSize: 12)),
                  ],
                ),
              ),

              const SizedBox(height: 20),

              const Text('Campus Health Metrics', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: AppTheme.textPrimary)),
              const SizedBox(height: 12),

              Row(
                children: [
                  Expanded(
                    child: _buildMetricTile('Verified Students', '$_totalStudents', Icons.school, AppTheme.primary),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: _buildMetricTile('Active Businesses', '$_totalBusinesses', Icons.storefront, const Color(0xFF0EA5E9)),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: _buildMetricTile('Student Reviews', '$_totalReviews', Icons.rate_review, const Color(0xFFF59E0B)),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: GestureDetector(
                      onTap: () => widget.onNavigateTab(1),
                      child: _buildMetricTile('Pending Approvals', '$_pendingVerifications', Icons.pending_actions, AppTheme.error),
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 24),

              // Action shortcut
              GestureDetector(
                onTap: () => widget.onNavigateTab(1),
                child: Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: AppTheme.border),
                  ),
                  child: Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(10),
                        decoration: BoxDecoration(
                          color: AppTheme.error.withOpacity(0.1),
                          shape: BoxShape.circle,
                        ),
                        child: const Icon(Icons.notifications_active, color: AppTheme.error, size: 24),
                      ),
                      const SizedBox(width: 14),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text('3 Businesses Awaiting Verification', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
                            const SizedBox(height: 2),
                            const Text('Review licenses, phone verification & physical store location', style: TextStyle(color: AppTheme.textSecondary, fontSize: 12)),
                          ],
                        ),
                      ),
                      const Icon(Icons.chevron_right, color: AppTheme.textMuted),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildMetricTile(String title, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppTheme.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(title, style: const TextStyle(fontSize: 12, color: AppTheme.textSecondary, fontWeight: FontWeight.w600)),
              Icon(icon, size: 20, color: color),
            ],
          ),
          const SizedBox(height: 8),
          Text(value, style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w800, color: AppTheme.textPrimary)),
        ],
      ),
    );
  }
}
