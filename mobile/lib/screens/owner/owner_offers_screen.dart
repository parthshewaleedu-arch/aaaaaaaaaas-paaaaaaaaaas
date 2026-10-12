import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';

class OwnerOffersScreen extends StatefulWidget {
  const OwnerOffersScreen({super.key});

  @override
  State<OwnerOffersScreen> createState() => _OwnerOffersScreenState();
}

class _OwnerOffersScreenState extends State<OwnerOffersScreen> {
  final List<Map<String, dynamic>> _offers = [
    {
      'id': 'off-1',
      'title': 'Monthly Mess Pass Early Bird Discount',
      'discount': '₹300 OFF',
      'code': 'AASPAAS-MESS300',
      'claims': 26,
      'status': 'ACTIVE',
      'valid_until': 'Oct 31, 2026',
    },
    {
      'id': 'off-2',
      'title': 'Group Study Dinner Deal (4+ Students)',
      'discount': '15% OFF',
      'code': 'CAMPUS-GROUP4',
      'claims': 14,
      'status': 'ACTIVE',
      'valid_until': 'Semester end',
    },
  ];

  void _showCreateOfferDialog() {
    final titleCtrl = TextEditingController();
    final discountCtrl = TextEditingController();
    final codeCtrl = TextEditingController();

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Post Student Deal'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: titleCtrl,
              decoration: const InputDecoration(labelText: 'Offer Title', hintText: 'e.g. 10% Off on Lunch Thali'),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: discountCtrl,
              decoration: const InputDecoration(labelText: 'Discount Text', hintText: 'e.g. 15% OFF or ₹50 OFF'),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: codeCtrl,
              decoration: const InputDecoration(labelText: 'Redemption Code', hintText: 'e.g. SHARMA15'),
            ),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')),
          ElevatedButton(
            onPressed: () {
              if (titleCtrl.text.isNotEmpty) {
                setState(() {
                  _offers.insert(0, {
                    'id': 'off-${DateTime.now().millisecondsSinceEpoch}',
                    'title': titleCtrl.text.trim(),
                    'discount': discountCtrl.text.trim().isEmpty ? '10% OFF' : discountCtrl.text.trim(),
                    'code': codeCtrl.text.trim().isEmpty ? 'STUDENTDEAL' : codeCtrl.text.trim(),
                    'claims': 0,
                    'status': 'ACTIVE',
                    'valid_until': '30 days',
                  });
                });
                Navigator.pop(ctx);
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Offer published to campus student feed!')),
                );
              }
            },
            child: const Text('Publish Deal'),
          ),
        ],
      ),
    );
  }

  void _validateCounterCode() {
    final codeCtrl = TextEditingController();
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Validate Student Pass'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text(
              'Enter the redemption code presented by the student:',
              style: TextStyle(fontSize: 13, color: AppTheme.textSecondary),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: codeCtrl,
              decoration: const InputDecoration(hintText: 'e.g. AASPAAS-MESS300'),
            ),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(ctx);
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  backgroundColor: AppTheme.success,
                  content: Text('✅ Valid Student Deal! MIT AOE ID confirmed. Apply discount.'),
                ),
              );
            },
            child: const Text('Verify Pass'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: const Text('Student Promotional Deals'),
        actions: [
          IconButton(
            icon: const Icon(Icons.qr_code_scanner, color: AppTheme.primary),
            tooltip: 'Verify Counter Pass',
            onPressed: _validateCounterCode,
          ),
        ],
      ),
      body: ListView.separated(
        padding: const EdgeInsets.all(16),
        itemCount: _offers.length,
        separatorBuilder: (_, __) => const SizedBox(height: 12),
        itemBuilder: (ctx, idx) {
          final o = _offers[idx];
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
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                      decoration: BoxDecoration(
                        color: AppTheme.primary,
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        o['discount'] as String,
                        style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 12),
                      ),
                    ),
                    Text(
                      '${o['claims']} Students Claimed',
                      style: const TextStyle(color: AppTheme.textSecondary, fontSize: 12, fontWeight: FontWeight.w600),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                Text(
                  o['title'] as String,
                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                ),
                const SizedBox(height: 8),
                Row(
                  children: [
                    const Icon(Icons.confirmation_number_outlined, size: 16, color: AppTheme.textSecondary),
                    const SizedBox(width: 4),
                    Text(
                      'Pass Code: ${o['code']}',
                      style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: AppTheme.textPrimary),
                    ),
                    const Spacer(),
                    Text('Expires: ${o['valid_until']}', style: const TextStyle(fontSize: 11, color: AppTheme.textMuted)),
                  ],
                ),
              ],
            ),
          );
        },
      ),
      floatingActionButton: FloatingActionButton.extended(
        backgroundColor: AppTheme.primary,
        icon: const Icon(Icons.add, color: Colors.white),
        label: const Text('Post Student Deal', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
        onPressed: _showCreateOfferDialog,
      ),
    );
  }
}
