import 'package:flutter/material.dart';
import '../../core/services/app_repository.dart';
import '../../core/theme/app_theme.dart';

class AdminVerificationsScreen extends StatefulWidget {
  const AdminVerificationsScreen({super.key});

  @override
  State<AdminVerificationsScreen> createState() => _AdminVerificationsScreenState();
}

class _AdminVerificationsScreenState extends State<AdminVerificationsScreen> {
  List<Map<String, dynamic>> _pendingList = [];

  @override
  void initState() {
    super.initState();
    _loadPendingList();
  }

  void _loadPendingList() {
    _pendingList = AppRepository.getPendingBusinesses();
    setState(() {});
  }

  Future<void> _handleAction(String bizId, String bizName, bool approve) async {
    if (approve) {
      // Approving immediately makes it visible to all students!
      await AppRepository.approveBusiness(bizId);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          backgroundColor: AppTheme.success,
          content: Text('✅ "$bizName" approved! It is now LIVE and visible to students.'),
        ),
      );
    } else {
      await AppRepository.rejectBusiness(bizId);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          backgroundColor: AppTheme.error,
          content: Text('❌ "$bizName" was rejected.'),
        ),
      );
    }

    _loadPendingList();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: const Text('Pending Business Approvals'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded, color: AppTheme.primary),
            onPressed: _loadPendingList,
          ),
        ],
      ),
      body: _pendingList.isEmpty
          ? Center(
              child: Padding(
                padding: const EdgeInsets.all(32.0),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Container(
                      padding: const EdgeInsets.all(20),
                      decoration: BoxDecoration(
                        color: AppTheme.success.withOpacity(0.1),
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(Icons.check_circle_outline, size: 54, color: AppTheme.success),
                    ),
                    const SizedBox(height: 16),
                    const Text('No Pending Submissions', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
                    const SizedBox(height: 6),
                    const Text('All campus businesses have been verified and are active.', style: TextStyle(color: AppTheme.textSecondary, fontSize: 13)),
                  ],
                ),
              ),
            )
          : ListView.separated(
              padding: const EdgeInsets.all(16),
              itemCount: _pendingList.length,
              separatorBuilder: (_, __) => const SizedBox(height: 14),
              itemBuilder: (ctx, idx) {
                final item = _pendingList[idx];
                final id = item['id'] as String;
                final name = item['name'] as String;
                final cat = item['category_name'] as String;
                final fee = item['monthly_fee'] ?? 500;
                final addr = item['address'] as String;
                final phone = item['phone'] as String;
                final owner = item['owner_email'] as String;
                final mapUrl = item['google_maps_url'] ?? '';

                return Container(
                  padding: const EdgeInsets.all(16),
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
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                            decoration: BoxDecoration(
                              color: AppTheme.primary.withOpacity(0.1),
                              borderRadius: BorderRadius.circular(6),
                            ),
                            child: Text(cat, style: const TextStyle(color: AppTheme.primary, fontWeight: FontWeight.bold, fontSize: 11)),
                          ),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                            decoration: BoxDecoration(
                              color: const Color(0xFFF59E0B).withOpacity(0.12),
                              borderRadius: BorderRadius.circular(6),
                            ),
                            child: Text('Plan: ₹$fee/mo', style: const TextStyle(color: Color(0xFFB45309), fontWeight: FontWeight.bold, fontSize: 11)),
                          ),
                        ],
                      ),
                      const SizedBox(height: 10),
                      Text(name, style: const TextStyle(fontSize: 17, fontWeight: FontWeight.bold)),
                      const SizedBox(height: 4),
                      Text('👤 Owner: $owner ($phone)', style: const TextStyle(fontSize: 12, color: AppTheme.textSecondary)),
                      const SizedBox(height: 4),
                      Text('📍 $addr', style: const TextStyle(fontSize: 12, color: AppTheme.textSecondary)),
                      if (mapUrl.isNotEmpty) ...[
                        const SizedBox(height: 4),
                        Row(
                          children: [
                            const Icon(Icons.map, size: 14, color: AppTheme.primary),
                            const SizedBox(width: 4),
                            Expanded(child: Text(mapUrl, maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 11, color: AppTheme.primary))),
                          ],
                        ),
                      ],
                      const SizedBox(height: 16),
                      Row(
                        children: [
                          Expanded(
                            child: OutlinedButton(
                              style: OutlinedButton.styleFrom(
                                foregroundColor: AppTheme.error,
                                side: const BorderSide(color: AppTheme.error),
                              ),
                              onPressed: () => _handleAction(id, name, false),
                              child: const Text('Reject'),
                            ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: ElevatedButton(
                              style: ElevatedButton.styleFrom(backgroundColor: AppTheme.success),
                              onPressed: () => _handleAction(id, name, true),
                              child: const Text('Approve & Verify (Live)'),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                );
              },
            ),
    );
  }
}
