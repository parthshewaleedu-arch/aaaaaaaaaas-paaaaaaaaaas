import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';

class AdminVerificationsScreen extends StatefulWidget {
  const AdminVerificationsScreen({super.key});

  @override
  State<AdminVerificationsScreen> createState() => _AdminVerificationsScreenState();
}

class _AdminVerificationsScreenState extends State<AdminVerificationsScreen> {
  final List<Map<String, dynamic>> _pendingList = [
    {
      'id': 'v-1',
      'name': 'Gajanan Mess & Dining Hall',
      'owner': 'Gajanan Patil (+91 94220 11223)',
      'category': 'Food & Mess',
      'address': 'Dnyaneshwar Nagar, Alandi (450 m from MIT AOE)',
      'docs': 'Shop Act License #MH-2024-8849',
      'time': 'Submitted 4 hours ago',
    },
    {
      'id': 'v-2',
      'name': 'SpeedXerox & Digital Printers',
      'owner': 'Mahesh Joshi (+91 98810 33445)',
      'category': 'Stationery/Xerox',
      'address': 'Main Gate Market, Alandi (150 m)',
      'docs': 'Electricity Bill & GST Reg',
      'time': 'Submitted yesterday',
    },
    {
      'id': 'v-3',
      'name': 'Campus Cuts Unisex Salon',
      'owner': 'Suresh Salunkhe (+91 97654 66778)',
      'category': 'Salon',
      'address': 'Opp. MIT AOE Girls Hostel',
      'docs': 'Udyam Registration Certificate',
      'time': 'Submitted 2 days ago',
    },
  ];

  void _handleAction(int index, bool approve) {
    final biz = _pendingList[index];
    setState(() => _pendingList.removeAt(index));

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        backgroundColor: approve ? AppTheme.success : AppTheme.error,
        content: Text(
          approve
              ? '✅ ${biz['name']} approved & verified on campus marketplace!'
              : '❌ ${biz['name']} rejected. Notice sent to shop owner.',
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: const Text('Pending Business Approvals'),
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
                    const Text('Verification Queue Clear!', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
                    const SizedBox(height: 6),
                    const Text('All campus business submissions have been processed.', style: TextStyle(color: AppTheme.textSecondary, fontSize: 13)),
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
                            child: Text(item['category'] as String, style: const TextStyle(color: AppTheme.primary, fontWeight: FontWeight.bold, fontSize: 11)),
                          ),
                          Text(item['time'] as String, style: const TextStyle(fontSize: 11, color: AppTheme.textMuted)),
                        ],
                      ),
                      const SizedBox(height: 10),
                      Text(item['name'] as String, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                      const SizedBox(height: 4),
                      Text('👤 Owner: ${item['owner']}', style: const TextStyle(fontSize: 12, color: AppTheme.textSecondary)),
                      const SizedBox(height: 4),
                      Text('📍 ${item['address']}', style: const TextStyle(fontSize: 12, color: AppTheme.textSecondary)),
                      const SizedBox(height: 4),
                      Text('📄 Docs: ${item['docs']}', style: const TextStyle(fontSize: 12, color: Color(0xFF0F766E), fontWeight: FontWeight.w600)),
                      const SizedBox(height: 16),
                      Row(
                        children: [
                          Expanded(
                            child: OutlinedButton(
                              style: OutlinedButton.styleFrom(foregroundColor: AppTheme.error, side: const BorderSide(color: AppTheme.error)),
                              onPressed: () => _handleAction(idx, false),
                              child: const Text('Reject'),
                            ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: ElevatedButton(
                              style: ElevatedButton.styleFrom(backgroundColor: AppTheme.success),
                              onPressed: () => _handleAction(idx, true),
                              child: const Text('Approve & Verify'),
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
