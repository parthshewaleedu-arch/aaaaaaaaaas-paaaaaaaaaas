import 'package:flutter/material.dart';
import '../../core/services/api_service.dart';
import '../../core/theme/app_theme.dart';
import '../../models/offer_model.dart';

class OffersScreen extends StatefulWidget {
  const OffersScreen({super.key});

  @override
  State<OffersScreen> createState() => _OffersScreenState();
}

class _OffersScreenState extends State<OffersScreen> {
  bool _isLoading = true;
  List<OfferModel> _offers = [];

  @override
  void initState() {
    super.initState();
    _loadOffers();
  }

  Future<void> _loadOffers() async {
    setState(() => _isLoading = true);

    final res = await ApiService.getOffers();
    if (res.success && res.data != null) {
      _offers = res.data!.map((o) => OfferModel.fromJson(o as Map<String, dynamic>)).toList();
    }

    if (_offers.isEmpty) {
      _offers = _getSampleOffers();
    }

    if (mounted) {
      setState(() => _isLoading = false);
    }
  }

  List<OfferModel> _getSampleOffers() {
    return [
      OfferModel(
        id: 'off-1',
        title: 'Monthly Mess Subscription Discount',
        description: 'Get ₹300 off on your first monthly mess pass by verifying MIT AOE student credentials.',
        businessId: 'sample-1',
        businessName: 'Sharma Mess & Tiffin Service',
        discountText: '₹300 OFF',
        code: 'AASPAAS-MESS300',
        validUntil: 'Valid this month',
      ),
      OfferModel(
        id: 'off-2',
        title: 'Project Printing & Hardcover Bundle',
        description: 'Complete final year project print bundle: 3 bound copies at student rates + free digital PDF copy.',
        businessId: 'sample-2',
        businessName: 'Campus Xerox & Stationery Hub',
        discountText: '25% OFF',
        code: 'CAMPUS-PRINT25',
        validUntil: 'Valid during submissions',
      ),
      OfferModel(
        id: 'off-3',
        title: 'Late Night Study Combo',
        description: 'Hot Masala Chai + Bun Maska + Wi-Fi coupon valid after 8:00 PM on presentation of student ID.',
        businessId: 'sample-3',
        businessName: 'Chai Shai & Cafe 24',
        discountText: 'COMBO @ ₹49',
        code: 'CHAI49',
        validUntil: 'Every weekday',
      ),
      OfferModel(
        id: 'off-4',
        title: 'Semester Gym Membership Pass',
        description: 'Unlimited access to cardio and weight room with complimentary locker storage.',
        businessId: 'sample-5',
        businessName: 'Iron Core Gym & Fitness',
        discountText: '₹799/MO',
        code: 'STUDENT-FIT',
        validUntil: 'Semester special',
      ),
    ];
  }

  void _showClaimDialog(OfferModel offer) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: Row(
          children: [
            const Icon(Icons.verified, color: AppTheme.primary),
            const SizedBox(width: 8),
            const Text('Student Deal Pass', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              offer.title,
              textAlign: TextAlign.center,
              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
            ),
            const SizedBox(height: 6),
            Text(
              offer.businessName,
              style: const TextStyle(color: AppTheme.textSecondary, fontSize: 13),
            ),
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
                  const Text('SHOW THIS CODE AT COUNTER', style: TextStyle(letterSpacing: 1.2, fontSize: 10, fontWeight: FontWeight.bold, color: AppTheme.textSecondary)),
                  const SizedBox(height: 8),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: AppTheme.border),
                    ),
                    child: Text(
                      offer.code ?? 'AASPAAS-DEAL',
                      style: const TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.w900,
                        letterSpacing: 2.0,
                        color: AppTheme.primary,
                      ),
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(offer.validUntil, style: const TextStyle(color: AppTheme.textMuted, fontSize: 11)),
                ],
              ),
            ),
            const SizedBox(height: 12),
            const Text(
              '⚠️ Flash along with your College ID to verify enrolled student status.',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 11, color: AppTheme.textSecondary),
            ),
          ],
        ),
        actions: [
          ElevatedButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Done'),
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
      ),
      body: RefreshIndicator(
        onRefresh: _loadOffers,
        color: AppTheme.primary,
        child: _isLoading
            ? const Center(child: CircularProgressIndicator())
            : ListView.separated(
                padding: const EdgeInsets.all(16),
                itemCount: _offers.length,
                separatorBuilder: (_, __) => const SizedBox(height: 14),
                itemBuilder: (ctx, idx) {
                  final offer = _offers[idx];
                  return _buildOfferCard(offer);
                },
              ),
      ),
    );
  }

  Widget _buildOfferCard(OfferModel offer) {
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
                        color: AppTheme.primary,
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: Text(
                        offer.discountText,
                        style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 12),
                      ),
                    ),
                    Text(
                      offer.validUntil,
                      style: const TextStyle(color: AppTheme.textMuted, fontSize: 11),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                Text(
                  offer.title,
                  style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppTheme.textPrimary),
                ),
                const SizedBox(height: 4),
                Text(
                  offer.businessName,
                  style: const TextStyle(color: AppTheme.primary, fontWeight: FontWeight.w600, fontSize: 13),
                ),
                if (offer.description != null) ...[
                  const SizedBox(height: 8),
                  Text(
                    offer.description!,
                    style: const TextStyle(color: AppTheme.textSecondary, fontSize: 12, height: 1.3),
                  ),
                ],
              ],
            ),
          ),
          const Divider(height: 1, color: AppTheme.border),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: const [
                    Icon(Icons.shield_outlined, size: 14, color: AppTheme.success),
                    SizedBox(width: 4),
                    Text('Verified Student Deal', style: TextStyle(color: AppTheme.success, fontSize: 11, fontWeight: FontWeight.w600)),
                  ],
                ),
                ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    minimumSize: const Size(110, 36),
                    padding: const EdgeInsets.symmetric(horizontal: 14),
                  ),
                  onPressed: () => _showClaimDialog(offer),
                  child: const Text('Claim Deal', style: TextStyle(fontSize: 13)),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
