import 'package:flutter/material.dart';
import '../../core/services/app_repository.dart';
import '../../core/theme/app_theme.dart';

class AdminDashboardScreen extends StatefulWidget {
  final Function(int) onNavigateTab;
  const AdminDashboardScreen({super.key, required this.onNavigateTab});

  @override
  State<AdminDashboardScreen> createState() => _AdminDashboardScreenState();
}

class _AdminDashboardScreenState extends State<AdminDashboardScreen> {
  int _totalStudents = 1;
  int _totalBusinesses = 0;
  int _pendingVerifications = 0;
  int _verifiedBusinesses = 0;
  List<Map<String, dynamic>> _allBusinesses = [];

  @override
  void initState() {
    super.initState();
    _loadRealDataInstantly();
  }

  void _loadRealDataInstantly() {
    _totalStudents = AppRepository.getUniqueStudentsCount();
    _allBusinesses = AppRepository.getAllBusinesses();
    _totalBusinesses = _allBusinesses.length;
    _pendingVerifications = AppRepository.getPendingBusinesses().length;
    _verifiedBusinesses = AppRepository.getVerifiedBusinesses().length;
    setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: const Text('Platform Administrator'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded, color: AppTheme.primary),
            onPressed: _loadRealDataInstantly,
          ),
        ],
      ),
      body: SingleChildScrollView(
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
                  const Text('Real-time campus marketplace stats, business approvals, and dispute moderation.', style: TextStyle(color: Colors.white70, fontSize: 12)),
                ],
              ),
            ),

            const SizedBox(height: 20),

            const Text('Live Campus Health Metrics', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: AppTheme.textPrimary)),
            const SizedBox(height: 12),

            Row(
              children: [
                Expanded(
                  child: _buildMetricTile(
                    'Unique Students Logged In',
                    '$_totalStudents',
                    Icons.school_rounded,
                    AppTheme.primary,
                    'Real verified accounts',
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildMetricTile(
                    'Total Businesses Listed',
                    '$_totalBusinesses',
                    Icons.storefront_rounded,
                    const Color(0xFF0EA5E9),
                    '$_verifiedBusinesses verified live',
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: _buildMetricTile(
                    'Active on Marketplace',
                    '$_verifiedBusinesses',
                    Icons.check_circle_rounded,
                    AppTheme.success,
                    'Visible to students',
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: GestureDetector(
                    onTap: () => widget.onNavigateTab(1),
                    child: _buildMetricTile(
                      'Pending Approvals',
                      '$_pendingVerifications',
                      Icons.pending_actions_rounded,
                      _pendingVerifications > 0 ? AppTheme.error : AppTheme.textSecondary,
                      'Tap to review',
                    ),
                  ),
                ),
              ],
            ),

            const SizedBox(height: 24),

            // Pending action notice if any
            if (_pendingVerifications > 0) ...[
              GestureDetector(
                onTap: () => widget.onNavigateTab(1),
                child: Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: AppTheme.error.withOpacity(0.4)),
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
                            Text('$_pendingVerifications Businesses Awaiting Verification', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
                            const SizedBox(height: 2),
                            const Text('Review categories, pricing plans & approve for student feed', style: TextStyle(color: AppTheme.textSecondary, fontSize: 12)),
                          ],
                        ),
                      ),
                      const Icon(Icons.chevron_right, color: AppTheme.textMuted),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 24),
            ],

            // List of ALL businesses in the platform (User Requirement!)
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text('All Registered Businesses', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: AppTheme.textPrimary)),
                Text('Total: $_totalBusinesses', style: const TextStyle(color: AppTheme.textSecondary, fontSize: 13, fontWeight: FontWeight.bold)),
              ],
            ),
            const SizedBox(height: 12),

            ListView.separated(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: _allBusinesses.length,
              separatorBuilder: (_, __) => const SizedBox(height: 10),
              itemBuilder: (ctx, idx) {
                final b = _allBusinesses[idx];
                final isApproved = b['status'] == 'VERIFIED';
                return Container(
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(14),
                    border: Border.all(color: AppTheme.border),
                  ),
                  child: Row(
                    children: [
                      CircleAvatar(
                        radius: 20,
                        backgroundColor: (isApproved ? AppTheme.success : AppTheme.secondary).withOpacity(0.12),
                        child: Icon(
                          isApproved ? Icons.verified : Icons.hourglass_top,
                          color: isApproved ? AppTheme.success : const Color(0xFFB45309),
                          size: 20,
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(b['name'] ?? 'Shop', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
                            const SizedBox(height: 2),
                            Text('${b['category_name']} • Plan: ₹${b['monthly_fee'] ?? 500}/mo', style: const TextStyle(fontSize: 12, color: AppTheme.textSecondary)),
                            const SizedBox(height: 2),
                            Text(b['address'] ?? '', maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 11, color: AppTheme.textMuted)),
                          ],
                        ),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                        decoration: BoxDecoration(
                          color: (isApproved ? AppTheme.success : AppTheme.secondary).withOpacity(0.1),
                          borderRadius: BorderRadius.circular(6),
                        ),
                        child: Text(
                          isApproved ? 'LIVE' : 'PENDING',
                          style: TextStyle(
                            color: isApproved ? AppTheme.success : const Color(0xFFB45309),
                            fontWeight: FontWeight.bold,
                            fontSize: 10,
                          ),
                        ),
                      ),
                    ],
                  ),
                );
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMetricTile(String title, String value, IconData icon, Color color, String sub) {
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
              Flexible(child: Text(title, style: const TextStyle(fontSize: 11, color: AppTheme.textSecondary, fontWeight: FontWeight.w600), overflow: TextOverflow.ellipsis)),
              Icon(icon, size: 18, color: color),
            ],
          ),
          const SizedBox(height: 8),
          Text(value, style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w800, color: AppTheme.textPrimary)),
          const SizedBox(height: 2),
          Text(sub, style: const TextStyle(fontSize: 10, color: AppTheme.textMuted)),
        ],
      ),
    );
  }
}
