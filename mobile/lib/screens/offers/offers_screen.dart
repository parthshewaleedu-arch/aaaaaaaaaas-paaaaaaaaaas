import 'package:flutter/material.dart';
import '../../core/services/app_repository.dart';
import '../../core/services/storage_service.dart';
import '../../core/theme/app_theme.dart';

class OffersScreen extends StatefulWidget {
  const OffersScreen({super.key});

  @override
  State<OffersScreen> createState() => _OffersScreenState();
}

class _OffersScreenState extends State<OffersScreen> {
  List<Map<String, dynamic>> _offers = [];

  @override
  void initState() {
    super.initState();
    _loadOffersInstantly();
  }

  void _loadOffersInstantly() {
    _offers = AppRepository.getAllActiveOffers();
    setState(() {});
  }

  void _showClaimDialog(Map<String, dynamic> offer) {
    final title = offer['title'] ?? 'Student Deal';
    final bizName = offer['business_name'] ?? 'Campus Partner';
    final code = offer['code'] ?? 'AASPAAS-DEAL';
    final max = (offer['max_claims'] as num?)?.toInt() ?? 10;
    final claimed = (offer['claimed_count'] as num?)?.toInt() ?? 0;
    final isFull = claimed >= max;

    if (isFull) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          backgroundColor: AppTheme.error,
          content: Text('⚠️ Sorry, all passes for this deal have been claimed!'),
        ),
      );
      return;
    }

    // Claim
    final email = StorageService.getCurrentUserEmail();
    AppRepository.claimOffer(offer['id'], email.isEmpty ? 'student@mitaoe.ac.in' : email);
    _loadOffersInstantly();

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: Row(
          children: const [
            Icon(Icons.verified, color: AppTheme.primary),
            SizedBox(width: 8),
            Text('Student Deal Claimed!', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(title, textAlign: TextAlign.center, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
            const SizedBox(height: 6),
            Text(bizName, style: const TextStyle(color: AppTheme.textSecondary, fontSize: 13)),
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: AppTheme.primary.withOpacity(0.06),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: AppTheme.primary.withOpacity(0.2)),
              ),
              child: Column(
                children: [
                  const Text('SHOW CODE AT SHOP COUNTER', style: TextStyle(letterSpacing: 1.2, fontSize: 10, fontWeight: FontWeight.bold, color: AppTheme.textSecondary)),
                  const SizedBox(height: 8),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: AppTheme.border),
                    ),
                    child: Text(
                      code,
                      style: const TextStyle(
                        fontSize: 22,
                        fontWeight: FontWeight.w900,
                        letterSpacing: 2.0,
                        color: AppTheme.primary,
                      ),
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text('Quota remaining: ${max - (claimed + 1)} of $max passes left', style: const TextStyle(color: AppTheme.textMuted, fontSize: 11)),
                ],
              ),
            ),
            const SizedBox(height: 12),
            const Text(
              '⚠️ Flash along with your College ID card to verify enrolled student status.',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 11, color: AppTheme.textSecondary),
            ),
          ],
        ),
        actions: [
          ElevatedButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Got It'),
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
        title: const Text('Campus Deals & Offers'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded, color: AppTheme.primary),
            onPressed: _loadOffersInstantly,
          ),
        ],
      ),
      body: _offers.isEmpty
          ? Center(
              child: Padding(
                padding: const EdgeInsets.all(32.0),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: const [
                    Icon(Icons.local_offer_outlined, size: 48, color: AppTheme.textMuted),
                    SizedBox(height: 12),
                    Text('No Campus Deals Active', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
                    SizedBox(height: 6),
                    Text('Local shops post exclusive discounts for MIT AOE students here.', textAlign: TextAlign.center, style: TextStyle(color: AppTheme.textSecondary, fontSize: 13)),
                  ],
                ),
              ),
            )
          : ListView.separated(
              padding: const EdgeInsets.all(16),
              itemCount: _offers.length,
              separatorBuilder: (_, __) => const SizedBox(height: 14),
              itemBuilder: (ctx, idx) {
                final offer = _offers[idx];
                final title = offer['title'] ?? 'Student Deal';
                final bizName = offer['business_name'] ?? 'Local Shop';
                final discount = offer['discount_text'] ?? '15% OFF';
                final max = (offer['max_claims'] as num?)?.toInt() ?? 10;
                final claimed = (offer['claimed_count'] as num?)?.toInt() ?? 0;
                final isFull = claimed >= max;

                return Container(
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: AppTheme.border),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Padding(
                        padding: const EdgeInsets.all(16.0),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                                  decoration: BoxDecoration(
                                    color: isFull ? AppTheme.textMuted : AppTheme.primary,
                                    borderRadius: BorderRadius.circular(8),
                                  ),
                                  child: Text(
                                    discount,
                                    style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 12),
                                  ),
                                ),
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                                  decoration: BoxDecoration(
                                    color: isFull ? AppTheme.error.withOpacity(0.1) : AppTheme.success.withOpacity(0.12),
                                    borderRadius: BorderRadius.circular(6),
                                  ),
                                  child: Text(
                                    isFull ? 'Deal Quota Filled' : '$claimed of $max Claimed',
                                    style: TextStyle(
                                      color: isFull ? AppTheme.error : AppTheme.success,
                                      fontWeight: FontWeight.bold,
                                      fontSize: 11,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 12),
                            Text(
                              title,
                              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppTheme.textPrimary),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              bizName,
                              style: const TextStyle(color: AppTheme.primary, fontWeight: FontWeight.w600, fontSize: 13),
                            ),
                            const SizedBox(height: 6),
                            Text(
                              'Limited quota: Valid for the first $max students only',
                              style: const TextStyle(color: AppTheme.textSecondary, fontSize: 11),
                            ),
                          ],
                        ),
                      ),
                      const Divider(height: 1, color: AppTheme.border),
                      Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            const Row(
                              children: [
                                Icon(Icons.shield_outlined, size: 14, color: AppTheme.success),
                                SizedBox(width: 4),
                                Text('Verified Student Deal', style: TextStyle(color: AppTheme.success, fontSize: 11, fontWeight: FontWeight.w600)),
                              ],
                            ),
                            ElevatedButton(
                              style: ElevatedButton.styleFrom(
                                backgroundColor: isFull ? AppTheme.textMuted : AppTheme.primary,
                                minimumSize: const Size(110, 36),
                                padding: const EdgeInsets.symmetric(horizontal: 14),
                              ),
                              onPressed: isFull ? null : () => _showClaimDialog(offer),
                              child: Text(isFull ? 'Sold Out' : 'Claim Pass', style: const TextStyle(fontSize: 13)),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                );
              },
            ),
    );
  }
}
