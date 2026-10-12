import 'package:flutter/material.dart';
import '../../core/services/api_service.dart';
import '../../core/services/storage_service.dart';
import '../../core/theme/app_theme.dart';

class OwnerDashboardScreen extends StatefulWidget {
  final Function(int) onNavigateTab;
  const OwnerDashboardScreen({super.key, required this.onNavigateTab});

  @override
  State<OwnerDashboardScreen> createState() => _OwnerDashboardScreenState();
}

class _OwnerDashboardScreenState extends State<OwnerDashboardScreen> {
  bool _isLoading = false;
  String _businessName = 'Sharma Mess & Tiffin Service';
  String _verificationStatus = 'VERIFIED'; // VERIFIED, PENDING_REVIEW, UNVERIFIED

  // Metric KPIs
  int _viewsCount = 1420;
  int _directionsCount = 284;
  int _callsCount = 68;
  int _reviewsCount = 42;
  double _rating = 4.6;
  int _activeOffersCount = 2;

  @override
  void initState() {
    super.initState();
    _fetchDashboard();
  }

  Future<void> _fetchDashboard() async {
    setState(() => _isLoading = true);
    final res = await ApiService.getOwnerDashboard();
    if (res.success && res.data != null) {
      final summary = res.data!['summary'];
      if (summary != null) {
        _viewsCount = summary['total_views'] ?? _viewsCount;
        _directionsCount = summary['directions_requested'] ?? _directionsCount;
        _callsCount = summary['calls_initiated'] ?? _callsCount;
      }
    }
    if (mounted) setState(() => _isLoading = false);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Shop Owner Dashboard',
              style: TextStyle(fontSize: 17, fontWeight: FontWeight.w800, color: AppTheme.textPrimary),
            ),
            Text(
              _businessName,
              style: const TextStyle(fontSize: 12, color: AppTheme.textSecondary),
            ),
          ],
        ),
        actions: [
          Container(
            margin: const EdgeInsets.only(right: 16),
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
            decoration: BoxDecoration(
              color: _verificationStatus == 'VERIFIED'
                  ? AppTheme.success.withOpacity(0.12)
                  : AppTheme.secondary.withOpacity(0.15),
              borderRadius: BorderRadius.circular(20),
            ),
            child: Row(
              children: [
                Icon(
                  _verificationStatus == 'VERIFIED' ? Icons.verified : Icons.pending_actions,
                  size: 14,
                  color: _verificationStatus == 'VERIFIED' ? AppTheme.success : AppTheme.secondary,
                ),
                const SizedBox(width: 4),
                Text(
                  _verificationStatus == 'VERIFIED' ? 'Verified Partner' : 'Pending Review',
                  style: TextStyle(
                    color: _verificationStatus == 'VERIFIED' ? AppTheme.success : const Color(0xFFB45309),
                    fontWeight: FontWeight.bold,
                    fontSize: 11,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _fetchDashboard,
        color: AppTheme.primary,
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Welcome Banner
              Container(
                padding: const EdgeInsets.all(18),
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [Color(0xFF0F766E), Color(0xFF14B8A6)],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(16),
                  boxShadow: [
                    BoxShadow(
                      color: AppTheme.primary.withOpacity(0.2),
                      blurRadius: 10,
                      offset: const Offset(0, 4),
                    ),
                  ],
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Campus Marketplace Reach',
                      style: TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.w600),
                    ),
                    const SizedBox(height: 6),
                    const Text(
                      '3,000+ Enrolled MIT AOE Students',
                      style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.w800),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Keep your opening hours and student prices updated to attract daily lunch and dinner crowds.',
                      style: TextStyle(color: Colors.white.withOpacity(0.9), fontSize: 12),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 20),

              // KPI Grid (Views, Directions, Calls, Reviews)
              const Text(
                '30-Day Performance Overview',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: AppTheme.textPrimary),
              ),
              const SizedBox(height: 12),

              Row(
                children: [
                  Expanded(
                    child: _buildKpiCard(
                      title: 'Student Views',
                      value: '$_viewsCount',
                      icon: Icons.visibility_rounded,
                      color: const Color(0xFF0EA5E9),
                      subtitle: '+18% this week',
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: _buildKpiCard(
                      title: 'Directions',
                      value: '$_directionsCount',
                      icon: Icons.directions_walk_rounded,
                      color: const Color(0xFF10B981),
                      subtitle: 'from Campus gates',
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: _buildKpiCard(
                      title: 'Phone Calls',
                      value: '$_callsCount',
                      icon: Icons.call_rounded,
                      color: const Color(0xFF8B5CF6),
                      subtitle: 'Inquiries & orders',
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: _buildKpiCard(
                      title: 'Student Rating',
                      value: '$_rating ⭐',
                      icon: Icons.star_rounded,
                      color: const Color(0xFFF59E0B),
                      subtitle: '$_reviewsCount reviews',
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 24),

              // Quick Actions
              const Text(
                'Quick Actions',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: AppTheme.textPrimary),
              ),
              const SizedBox(height: 12),

              Row(
                children: [
                  Expanded(
                    child: _buildActionBtn(
                      icon: Icons.restaurant_menu_rounded,
                      label: 'Manage Menu',
                      onTap: () => widget.onNavigateTab(2),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: _buildActionBtn(
                      icon: Icons.local_offer_rounded,
                      label: 'Post Offer',
                      onTap: () => widget.onNavigateTab(3),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: _buildActionBtn(
                      icon: Icons.edit_note_rounded,
                      label: 'Edit Listing',
                      onTap: () => widget.onNavigateTab(1),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: _buildActionBtn(
                      icon: Icons.access_time_rounded,
                      label: 'Shop Hours',
                      onTap: () {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('Opening Hours: 08:30 AM - 10:30 PM (Mon-Sun)')),
                        );
                      },
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 24),

              // Recent Student Interactions
              const Text(
                'Recent Student Activity',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: AppTheme.textPrimary),
              ),
              const SizedBox(height: 12),

              Container(
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: AppTheme.border),
                ),
                child: Column(
                  children: [
                    _buildActivityTile(
                      icon: Icons.star,
                      iconColor: AppTheme.secondary,
                      title: '5-Star Review received',
                      subtitle: 'Snehal K.: "Best unlimited thali near campus!"',
                      time: '2 hours ago',
                    ),
                    const Divider(height: 1, color: AppTheme.border),
                    _buildActivityTile(
                      icon: Icons.local_offer,
                      iconColor: AppTheme.primary,
                      title: 'Student Discount Claimed',
                      subtitle: 'Code: AASPAAS-MESS300 (MIT AOE Student ID verified)',
                      time: '4 hours ago',
                    ),
                    const Divider(height: 1, color: AppTheme.border),
                    _buildActivityTile(
                      icon: Icons.directions_walk,
                      iconColor: AppTheme.success,
                      title: 'Walking navigation started',
                      subtitle: 'Student located at MIT AOE Academic Block',
                      time: 'Yesterday',
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildKpiCard({
    required String title,
    required String value,
    required IconData icon,
    required Color color,
    required String subtitle,
  }) {
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
          Text(
            value,
            style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w800, color: AppTheme.textPrimary),
          ),
          const SizedBox(height: 4),
          Text(subtitle, style: const TextStyle(fontSize: 11, color: AppTheme.textMuted)),
        ],
      ),
    );
  }

  Widget _buildActionBtn({
    required IconData icon,
    required String label,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: AppTheme.border),
        ),
        child: Row(
          children: [
            Icon(icon, color: AppTheme.primary, size: 20),
            const SizedBox(width: 8),
            Text(label, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: AppTheme.textPrimary)),
          ],
        ),
      ),
    );
  }

  Widget _buildActivityTile({
    required IconData icon,
    required Color iconColor,
    required String title,
    required String subtitle,
    required String time,
  }) {
    return ListTile(
      leading: CircleAvatar(
        radius: 18,
        backgroundColor: iconColor.withOpacity(0.12),
        child: Icon(icon, size: 18, color: iconColor),
      ),
      title: Text(title, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
      subtitle: Text(subtitle, style: const TextStyle(fontSize: 12, color: AppTheme.textSecondary), maxLines: 1, overflow: TextOverflow.ellipsis),
      trailing: Text(time, style: const TextStyle(fontSize: 11, color: AppTheme.textMuted)),
    );
  }
}
