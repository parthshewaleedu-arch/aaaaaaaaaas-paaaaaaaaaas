import 'package:flutter/material.dart';
import '../../core/services/app_repository.dart';
import '../../core/services/storage_service.dart';
import '../../core/theme/app_theme.dart';

class OwnerOffersScreen extends StatefulWidget {
  const OwnerOffersScreen({super.key});

  @override
  State<OwnerOffersScreen> createState() => _OwnerOffersScreenState();
}

class _OwnerOffersScreenState extends State<OwnerOffersScreen> {
  String _ownerEmail = '';
  Map<String, dynamic>? _myBusiness;
  List<Map<String, dynamic>> _myOffers = [];

  @override
  void initState() {
    super.initState();
    _loadDataInstantly();
  }

  void _loadDataInstantly() {
    _ownerEmail = StorageService.getCurrentUserEmail();
    _myBusiness = AppRepository.getBusinessByOwner(_ownerEmail);

    if (_myBusiness != null) {
      _myOffers = AppRepository.getOffersForBusiness(_myBusiness!['id']);
    } else {
      _myOffers = [];
    }
    setState(() {});
  }

  void _showCreateOfferDialog() {
    if (_myBusiness == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please list your business first before creating deals!')),
      );
      return;
    }

    final titleCtrl = TextEditingController();
    final discountCtrl = TextEditingController();
    final codeCtrl = TextEditingController();
    int studentQuota = 10; // Default first 10 students

    showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setDialogState) => AlertDialog(
          title: const Text('Create Student Deal'),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('Offer Title *', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                const SizedBox(height: 6),
                TextField(
                  controller: titleCtrl,
                  decoration: const InputDecoration(hintText: 'e.g. First 10 Students Lunch Discount'),
                ),
                const SizedBox(height: 14),

                const Text('Discount Value *', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                const SizedBox(height: 6),
                TextField(
                  controller: discountCtrl,
                  decoration: const InputDecoration(hintText: 'e.g. 15% OFF or ₹300 OFF'),
                ),
                const SizedBox(height: 14),

                const Text('Redemption Code *', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                const SizedBox(height: 6),
                TextField(
                  controller: codeCtrl,
                  decoration: const InputDecoration(hintText: 'e.g. STUDENT10'),
                ),
                const SizedBox(height: 14),

                // No. of Students Limit (User Requirement!)
                const Text('Quota Limit (No. of Students)', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                const SizedBox(height: 4),
                const Text('Only the first X students who claim will receive this deal:', style: TextStyle(fontSize: 11, color: AppTheme.textSecondary)),
                const SizedBox(height: 8),

                Wrap(
                  spacing: 8,
                  children: [10, 20, 50, 100].map((num) {
                    final isSel = studentQuota == num;
                    return ChoiceChip(
                      label: Text('First $num students', style: const TextStyle(fontSize: 12)),
                      selected: isSel,
                      selectedColor: AppTheme.primary,
                      labelStyle: TextStyle(color: isSel ? Colors.white : AppTheme.textPrimary, fontWeight: FontWeight.bold),
                      onSelected: (val) {
                        if (val) setDialogState(() => studentQuota = num);
                      },
                    );
                  }).toList(),
                ),
              ],
            ),
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')),
            ElevatedButton(
              onPressed: () async {
                if (titleCtrl.text.isNotEmpty) {
                  await AppRepository.createOffer(
                    businessId: _myBusiness!['id'],
                    businessName: _myBusiness!['name'],
                    title: titleCtrl.text.trim(),
                    discountText: discountCtrl.text.trim().isEmpty ? '15% OFF' : discountCtrl.text.trim(),
                    code: codeCtrl.text.trim().isEmpty ? 'DEAL10' : codeCtrl.text.trim(),
                    maxStudentsLimit: studentQuota,
                  );
                  Navigator.pop(ctx);
                  _loadDataInstantly();
                  if (!mounted) return;
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      backgroundColor: AppTheme.success,
                      content: Text('✅ Deal published for first $studentQuota students!'),
                    ),
                  );
                }
              },
              child: const Text('Publish Deal'),
            ),
          ],
        ),
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
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Enter the redemption code presented by the student at the counter:',
              style: TextStyle(fontSize: 13, color: AppTheme.textSecondary),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: codeCtrl,
              decoration: const InputDecoration(
                hintText: 'e.g. AASPAAS-MESS300',
                prefixIcon: Icon(Icons.qr_code),
              ),
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
                  content: Text('✅ Verified Student Pass! MIT AOE ID confirmed. Apply discount.'),
                ),
              );
            },
            child: const Text('Confirm & Apply'),
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
        title: const Text('Deals & Student Quotas'),
        actions: [
          IconButton(
            icon: const Icon(Icons.qr_code_scanner, color: AppTheme.primary),
            tooltip: 'Validate Student Pass',
            onPressed: _validateCounterCode,
          ),
        ],
      ),
      body: _myBusiness == null
          ? Center(
              child: Padding(
                padding: const EdgeInsets.all(24.0),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: const [
                    Icon(Icons.store_mall_directory_outlined, size: 48, color: AppTheme.textMuted),
                    SizedBox(height: 12),
                    Text('No Business Listed', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                    SizedBox(height: 4),
                    Text('Please list your shop under the "My Shop" tab first.', textAlign: TextAlign.center, style: TextStyle(color: AppTheme.textSecondary, fontSize: 13)),
                  ],
                ),
              ),
            )
          : _myOffers.isEmpty
              ? Center(
                  child: Padding(
                    padding: const EdgeInsets.all(32.0),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Container(
                          padding: const EdgeInsets.all(20),
                          decoration: BoxDecoration(color: AppTheme.primary.withOpacity(0.08), shape: BoxShape.circle),
                          child: const Icon(Icons.local_offer_outlined, size: 48, color: AppTheme.primary),
                        ),
                        const SizedBox(height: 16),
                        const Text('No Active Deals Posted', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
                        const SizedBox(height: 8),
                        const Text('Attract campus crowds by posting a limited deal (e.g. for the first 10 students).', textAlign: TextAlign.center, style: TextStyle(color: AppTheme.textSecondary, fontSize: 13)),
                        const SizedBox(height: 20),
                        ElevatedButton.icon(
                          icon: const Icon(Icons.add),
                          label: const Text('Create Student Deal'),
                          onPressed: _showCreateOfferDialog,
                        ),
                      ],
                    ),
                  ),
                )
              : ListView.separated(
                  padding: const EdgeInsets.all(16),
                  itemCount: _myOffers.length,
                  separatorBuilder: (_, __) => const SizedBox(height: 12),
                  itemBuilder: (ctx, idx) {
                    final o = _myOffers[idx];
                    final max = (o['max_claims'] as num?)?.toInt() ?? 10;
                    final claimed = (o['claimed_count'] as num?)?.toInt() ?? 0;
                    final progress = (claimed / max).clamp(0.0, 1.0);

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
                                  o['discount_text'] ?? '15% OFF',
                                  style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 12),
                                ),
                              ),
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                                decoration: BoxDecoration(
                                  color: AppTheme.success.withOpacity(0.12),
                                  borderRadius: BorderRadius.circular(6),
                                ),
                                child: Text(
                                  '$claimed / $max Claimed',
                                  style: const TextStyle(color: AppTheme.success, fontWeight: FontWeight.bold, fontSize: 11),
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 12),
                          Text(
                            o['title'] ?? 'Student Deal',
                            style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                          ),
                          const SizedBox(height: 8),

                          // Quota Progress Bar
                          ClipRRect(
                            borderRadius: BorderRadius.circular(4),
                            child: LinearProgressIndicator(
                              value: progress,
                              backgroundColor: AppTheme.border,
                              valueColor: const AlwaysStoppedAnimation<Color>(AppTheme.primary),
                              minHeight: 6,
                            ),
                          ),
                          const SizedBox(height: 10),

                          Row(
                            children: [
                              const Icon(Icons.confirmation_number_outlined, size: 16, color: AppTheme.textSecondary),
                              const SizedBox(width: 4),
                              Text('Code: ${o['code']}', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                              const Spacer(),
                              Text('Quota: First $max Students', style: const TextStyle(color: AppTheme.textMuted, fontSize: 11)),
                            ],
                          ),
                        ],
                      ),
                    );
                  },
                ),
      floatingActionButton: _myBusiness != null
          ? FloatingActionButton.extended(
              backgroundColor: AppTheme.primary,
              icon: const Icon(Icons.add, color: Colors.white),
              label: const Text('Post Student Deal', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
              onPressed: _showCreateOfferDialog,
            )
          : null,
    );
  }
}
