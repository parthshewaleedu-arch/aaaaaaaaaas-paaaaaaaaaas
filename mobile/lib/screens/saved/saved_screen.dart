import 'package:flutter/material.dart';
import '../../core/services/storage_service.dart';
import '../../core/theme/app_theme.dart';
import '../../models/business_model.dart';
import '../business/business_detail_screen.dart';

class SavedScreen extends StatefulWidget {
  const SavedScreen({super.key});

  @override
  State<SavedScreen> createState() => _SavedScreenState();
}

class _SavedScreenState extends State<SavedScreen> {
  List<BusinessModel> _savedList = [];

  @override
  void initState() {
    super.initState();
    _loadSaved();
  }

  void _loadSaved() {
    final savedIds = StorageService.getSavedBusinessIds();
    // In real app, fetches from backend; for immediate display use cached/sample set
    _savedList = [
      BusinessModel(
        id: 'sample-1',
        name: 'Sharma Mess & Tiffin Service',
        address: 'Near MIT AOE Back Gate, Alandi',
        categoryName: 'Food & Mess',
        rating: 4.6,
        reviewCount: 312,
        priceLevel: '₹',
        distanceMeters: 350,
        isOpenNow: true,
        isVerified: true,
        hasStudentDiscount: true,
        discountDetails: '15% Off Monthly Mess Pass',
      ),
      BusinessModel(
        id: 'sample-2',
        name: 'Campus Xerox & Stationery Hub',
        address: 'Opposite Main Gate, Alandi',
        categoryName: 'Printing/Xerox',
        rating: 4.8,
        reviewCount: 189,
        priceLevel: '₹',
        distanceMeters: 120,
        isOpenNow: true,
        isVerified: true,
        hasStudentDiscount: true,
      ),
    ].where((b) => savedIds.isEmpty || savedIds.contains(b.id)).toList();

    setState(() {});
  }

  Future<void> _removeSaved(String id) async {
    await StorageService.toggleSavedBusiness(id);
    _loadSaved();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: const Text('Saved Places'),
      ),
      body: _savedList.isEmpty
          ? Center(
              child: Padding(
                padding: const EdgeInsets.all(32.0),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Container(
                      padding: const EdgeInsets.all(20),
                      decoration: BoxDecoration(
                        color: AppTheme.primary.withOpacity(0.08),
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(Icons.bookmark_border_rounded, size: 48, color: AppTheme.primary),
                    ),
                    const SizedBox(height: 16),
                    const Text(
                      'No Saved Places Yet',
                      style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppTheme.textPrimary),
                    ),
                    const SizedBox(height: 8),
                    const Text(
                      'Bookmark your favorite mess, cafes, or print shops for quick 1-tap access.',
                      textAlign: TextAlign.center,
                      style: TextStyle(fontSize: 13, color: AppTheme.textSecondary),
                    ),
                  ],
                ),
              ),
            )
          : ListView.separated(
              padding: const EdgeInsets.all(16),
              itemCount: _savedList.length,
              separatorBuilder: (_, __) => const SizedBox(height: 12),
              itemBuilder: (ctx, idx) {
                final biz = _savedList[idx];
                return Dismissible(
                  key: Key(biz.id),
                  direction: DismissDirection.endToStart,
                  background: Container(
                    alignment: Alignment.centerRight,
                    padding: const EdgeInsets.only(right: 20),
                    decoration: BoxDecoration(
                      color: AppTheme.error,
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: const Icon(Icons.delete_outline, color: Colors.white),
                  ),
                  onDismissed: (_) => _removeSaved(biz.id),
                  child: GestureDetector(
                    onTap: () {
                      Navigator.of(context).push(
                        MaterialPageRoute(builder: (_) => BusinessDetailScreen(businessId: biz.id, initialBusiness: biz)),
                      );
                    },
                    child: Container(
                      padding: const EdgeInsets.all(14),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(color: AppTheme.border),
                      ),
                      child: Row(
                        children: [
                          Container(
                            width: 54,
                            height: 54,
                            decoration: BoxDecoration(
                              color: AppTheme.primary.withOpacity(0.08),
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: const Icon(Icons.storefront_rounded, color: AppTheme.primary, size: 28),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  biz.name,
                                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                                ),
                                const SizedBox(height: 2),
                                Text(
                                  '${biz.categoryName} • ${biz.formattedDistance}',
                                  style: const TextStyle(color: AppTheme.textSecondary, fontSize: 12),
                                ),
                                const SizedBox(height: 4),
                                Row(
                                  children: [
                                    const Icon(Icons.star_rounded, size: 14, color: AppTheme.secondary),
                                    const SizedBox(width: 2),
                                    Text(biz.rating.toStringAsFixed(1), style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12)),
                                    const SizedBox(width: 6),
                                    Text('(${biz.reviewCount})', style: const TextStyle(color: AppTheme.textMuted, fontSize: 11)),
                                  ],
                                ),
                              ],
                            ),
                          ),
                          IconButton(
                            icon: const Icon(Icons.bookmark, color: AppTheme.primary),
                            onPressed: () => _removeSaved(biz.id),
                          ),
                        ],
                      ),
                    ),
                  ),
                );
              },
            ),
    );
  }
}
