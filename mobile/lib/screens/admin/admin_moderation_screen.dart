import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';

class AdminModerationScreen extends StatefulWidget {
  const AdminModerationScreen({super.key});

  @override
  State<AdminModerationScreen> createState() => _AdminModerationScreenState();
}

class _AdminModerationScreenState extends State<AdminModerationScreen> {
  final List<Map<String, dynamic>> _reports = [
    {
      'id': 'rep-1',
      'reason': 'Offensive language & unverified transaction claim',
      'target': 'Review on "Campus FastFood"',
      'content': '"Terrible quality, food was rotten and uncle was rude!"',
      'reporter': 'Business Owner',
      'author': 'Student (Mechanical Dept)',
      'status': 'PENDING',
    },
    {
      'id': 'rep-2',
      'reason': 'Pricing dispute: Menu stated ₹80 but charged ₹110',
      'target': 'Price Discrepancy on "Om Xerox"',
      'content': '"Spiral binding advertised at ₹20 was billed at ₹35."',
      'reporter': 'Student (Computer Dept)',
      'author': 'Om Xerox Hub',
      'status': 'PENDING',
    },
  ];

  void _resolveReport(int index, String resolution) {
    setState(() => _reports.removeAt(index));
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('Dispute resolved: $resolution')),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: const Text('Review Moderation & Disputes'),
      ),
      body: _reports.isEmpty
          ? Center(
              child: Padding(
                padding: const EdgeInsets.all(32.0),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Container(
                      padding: const EdgeInsets.all(20),
                      decoration: BoxDecoration(color: AppTheme.success.withOpacity(0.1), shape: BoxShape.circle),
                      child: const Icon(Icons.verified_user_outlined, size: 54, color: AppTheme.success),
                    ),
                    const SizedBox(height: 16),
                    const Text('No Moderation Flags', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
                    const SizedBox(height: 6),
                    const Text('Review ecosystem is clean and trusted.', style: TextStyle(color: AppTheme.textSecondary, fontSize: 13)),
                  ],
                ),
              ),
            )
          : ListView.separated(
              padding: const EdgeInsets.all(16),
              itemCount: _reports.length,
              separatorBuilder: (_, __) => const SizedBox(height: 14),
              itemBuilder: (ctx, idx) {
                final r = _reports[idx];
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
                              color: AppTheme.error.withOpacity(0.1),
                              borderRadius: BorderRadius.circular(6),
                            ),
                            child: const Text('FLAGGED DISPUTE', style: TextStyle(color: AppTheme.error, fontSize: 10, fontWeight: FontWeight.bold)),
                          ),
                          Text('Reported by ${r['reporter']}', style: const TextStyle(fontSize: 11, color: AppTheme.textMuted)),
                        ],
                      ),
                      const SizedBox(height: 10),
                      Text(r['target'] as String, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
                      const SizedBox(height: 4),
                      Text('Flag Reason: ${r['reason']}', style: const TextStyle(fontSize: 12, color: AppTheme.error, fontWeight: FontWeight.w600)),
                      const SizedBox(height: 8),
                      Container(
                        padding: const EdgeInsets.all(10),
                        decoration: BoxDecoration(color: AppTheme.background, borderRadius: BorderRadius.circular(8)),
                        child: Text(r['content'] as String, style: const TextStyle(fontSize: 12, fontStyle: FontStyle.italic)),
                      ),
                      const SizedBox(height: 14),
                      Row(
                        children: [
                          Expanded(
                            child: OutlinedButton(
                              onPressed: () => _resolveReport(idx, 'Dismissed report (Content preserved)'),
                              child: const Text('Dismiss Report'),
                            ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: ElevatedButton(
                              style: ElevatedButton.styleFrom(backgroundColor: AppTheme.error),
                              onPressed: () => _resolveReport(idx, 'Content removed & violation recorded'),
                              child: const Text('Remove Content'),
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
