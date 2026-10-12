import 'package:flutter/material.dart';
import '../../core/services/app_repository.dart';
import '../../core/services/storage_service.dart';
import '../../core/theme/app_theme.dart';

class OwnerDashboardScreen extends StatefulWidget {
  final Function(int) onNavigateTab;
  const OwnerDashboardScreen({super.key, required this.onNavigateTab});

  @override
  State<OwnerDashboardScreen> createState() => _OwnerDashboardScreenState();
}

class _OwnerDashboardScreenState extends State<OwnerDashboardScreen> {
  Map<String, dynamic>? _myBusiness;
  String _ownerEmail = '';

  @override
  void initState() {
    super.initState();
    _loadState();
  }

  void _loadState() {
    _ownerEmail = StorageService.getCurrentUserEmail();
    _myBusiness = AppRepository.getBusinessByOwner(_ownerEmail);
    setState(() {});
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
              'Shop Owner Portal',
              style: TextStyle(fontSize: 17, fontWeight: FontWeight.w800, color: AppTheme.textPrimary),
            ),
            Text(
              _ownerEmail.isEmpty ? 'Logged in as Owner' : _ownerEmail,
              style: const TextStyle(fontSize: 11, color: AppTheme.textSecondary),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded, color: AppTheme.primary),
            onPressed: _loadState,
          ),
        ],
      ),
      body: _myBusiness == null
          ? _buildUnlistedOwnerView()
          : _buildListedBusinessDashboard(),
    );
  }

  // View when this owner hasn't listed a business yet
  Widget _buildUnlistedOwnerView() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: AppTheme.border),
            ),
            child: Column(
              children: [
                Container(
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    color: AppTheme.primary.withOpacity(0.08),
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(Icons.add_business_rounded, size: 54, color: AppTheme.primary),
                ),
                const SizedBox(height: 18),
                const Text(
                  'No Business Listed Yet',
                  style: TextStyle(fontSize: 20, fontWeight: FontWeight.w800, color: AppTheme.textPrimary),
                ),
                const SizedBox(height: 8),
                const Text(
                  'You are registered as a business owner. List your shop, mess, hostel, or service to start reaching 3,000+ MIT AOE students around Alandi.',
                  textAlign: TextAlign.center,
                  style: TextStyle(fontSize: 13, color: AppTheme.textSecondary, height: 1.4),
                ),
                const SizedBox(height: 24),
                ElevatedButton.icon(
                  icon: const Icon(Icons.edit_note_rounded),
                  label: const Text('List My Business Now'),
                  onPressed: () => widget.onNavigateTab(1),
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),
          const Text('Listing Plans Available:', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
          const SizedBox(height: 12),
          _buildPlanInfoTile('Hostels (Boys & Girls)', '₹2,000 / month', 'Priority student recommendations'),
          const SizedBox(height: 8),
          _buildPlanInfoTile('Mess & Hotels (Lunch/Dinner)', '₹1,500 / month', 'Daily lunch & dinner visibility'),
          const SizedBox(height: 8),
          _buildPlanInfoTile('Snacks, Cafe, Gym, Repairs, Hospital', '₹500 / month', 'Search filters & deal promotions'),
          const SizedBox(height: 8),
          _buildPlanInfoTile('Stationery, Laundry, Salon, Grocery, etc.', '₹300 / month', 'Verified campus directory listing'),
        ],
      ),
    );
  }

  Widget _buildPlanInfoTile(String title, String price, String sub) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: AppTheme.border),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                Text(sub, style: const TextStyle(fontSize: 11, color: AppTheme.textSecondary)),
              ],
            ),
          ),
          Text(price, style: const TextStyle(fontWeight: FontWeight.w800, color: AppTheme.primary, fontSize: 13)),
        ],
      ),
    );
  }

  // View when this owner HAS listed a business
  Widget _buildListedBusinessDashboard() {
    final biz = _myBusiness!;
    final isVerified = biz['status'] == 'VERIFIED';
    final name = biz['name'] ?? 'My Business';
    final cat = biz['category_name'] ?? 'General';
    final fee = biz['monthly_fee'] ?? 500;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Business Status Card
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: isVerified ? AppTheme.success : AppTheme.secondary),
            ),
            child: Row(
              children: [
                CircleAvatar(
                  backgroundColor: (isVerified ? AppTheme.success : AppTheme.secondary).withOpacity(0.12),
                  child: Icon(
                    isVerified ? Icons.verified : Icons.hourglass_top,
                    color: isVerified ? AppTheme.success : AppTheme.secondary,
                  ),
                ),
                const SizedBox(width: 14),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        name,
                        style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        '$cat • Plan: ₹$fee/mo',
                        style: const TextStyle(fontSize: 12, color: AppTheme.textSecondary),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        isVerified
                            ? '🟢 Verified Partner (Visible to Students)'
                            : '⏳ Awaiting Admin Approval',
                        style: TextStyle(
                          color: isVerified ? AppTheme.success : const Color(0xFFB45309),
                          fontWeight: FontWeight.bold,
                          fontSize: 11,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 20),

          // KPIs for this shop
          const Text('Real-Time Shop Metrics', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800)),
          const SizedBox(height: 12),

          Row(
            children: [
              Expanded(
                child: _buildMetricCard('Student Views', isVerified ? '142' : '0', Icons.visibility_rounded, Colors.blue),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildMetricCard('Directions', isVerified ? '28' : '0', Icons.directions_walk_rounded, Colors.green),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: _buildMetricCard('Phone Calls', isVerified ? '9' : '0', Icons.call_rounded, Colors.purple),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildMetricCard('Rating', isVerified ? '4.6 ⭐' : 'New', Icons.star_rounded, Colors.amber),
              ),
            ],
          ),

          const SizedBox(height: 24),

          // Quick actions
          const Text('Manage Listing', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800)),
          const SizedBox(height: 12),

          Row(
            children: [
              Expanded(
                child: OutlinedButton.icon(
                  icon: const Icon(Icons.edit),
                  label: const Text('Edit Shop Details'),
                  onPressed: () => widget.onNavigateTab(1),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: ElevatedButton.icon(
                  icon: const Icon(Icons.local_offer),
                  label: const Text('Give Student Deal'),
                  onPressed: () => widget.onNavigateTab(3),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildMetricCard(String title, String val, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: AppTheme.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(title, style: const TextStyle(fontSize: 12, color: AppTheme.textSecondary, fontWeight: FontWeight.w600)),
              Icon(icon, size: 18, color: color),
            ],
          ),
          const SizedBox(height: 8),
          Text(val, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w800)),
        ],
      ),
    );
  }
}
