import 'package:flutter/material.dart';
import '../../core/services/api_service.dart';
import '../../core/theme/app_theme.dart';
import '../../models/business_model.dart';
import '../business/business_detail_screen.dart';

class SearchScreen extends StatefulWidget {
  final String? initialCategory;
  const SearchScreen({super.key, this.initialCategory});

  @override
  State<SearchScreen> createState() => _SearchScreenState();
}

class _SearchScreenState extends State<SearchScreen> {
  final _searchController = TextEditingController();
  bool _isLoading = false;
  List<BusinessModel> _results = [];

  // Filter state
  double? _minRating;
  String? _priceLevel;
  bool _studentDiscountOnly = false;
  bool _openNowOnly = false;
  String _sort = 'relevance';

  final List<String> _quickTags = [
    'Cheap mess',
    'Xerox / Printing',
    'Cafe with Wi-Fi',
    'Laundry',
    'Medical open now',
    'Gym',
    'Haircut',
    'Laptop repair',
  ];

  @override
  void initState() {
    super.initState();
    _performSearch();
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _performSearch() async {
    setState(() => _isLoading = true);

    final res = await ApiService.getBusinesses(
      search: _searchController.text.trim().isEmpty ? null : _searchController.text.trim(),
      minRating: _minRating,
      priceLevel: _priceLevel,
      studentDiscount: _studentDiscountOnly ? true : null,
      openNow: _openNowOnly ? true : null,
      sort: _sort == 'relevance' ? 'newest' : _sort,
    );

    if (res.success && res.data != null) {
      final items = (res.data!['items'] as List?) ?? [];
      _results = items.map((b) => BusinessModel.fromJson(b as Map<String, dynamic>)).toList();
    } else {
      // Fallback sample data for offline preview
      _results = _getMockSearchResults(_searchController.text.trim().toLowerCase());
    }

    if (mounted) {
      setState(() => _isLoading = false);
    }
  }

  List<BusinessModel> _getMockSearchResults(String query) {
    final all = [
      BusinessModel(
        id: 's-1',
        name: 'Sharma Mess & Tiffin Service',
        categoryName: 'Food & Mess',
        address: 'Near MIT AOE Back Gate, Alandi',
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
        id: 's-2',
        name: 'Campus Xerox & Stationery Hub',
        categoryName: 'Printing/Xerox',
        address: 'Opposite Main Gate, Alandi',
        rating: 4.8,
        reviewCount: 189,
        priceLevel: '₹',
        distanceMeters: 120,
        isOpenNow: true,
        isVerified: true,
        hasStudentDiscount: true,
        discountDetails: 'Spiral binding ₹20',
      ),
      BusinessModel(
        id: 's-3',
        name: 'Chai Shai & Cafe 24',
        categoryName: 'Cafe',
        address: 'Dnyaneshwar Nagar, Alandi',
        rating: 4.4,
        reviewCount: 245,
        priceLevel: '₹₹',
        distanceMeters: 620,
        isOpenNow: true,
        isVerified: true,
        hasStudentDiscount: true,
      ),
      BusinessModel(
        id: 's-4',
        name: 'Sanjeevani Medical & Pharmacy',
        categoryName: 'Medical',
        address: 'Dehu Phata, Alandi',
        rating: 4.7,
        reviewCount: 88,
        priceLevel: '₹₹',
        distanceMeters: 450,
        isOpenNow: true,
        isVerified: true,
        hasStudentDiscount: false,
      ),
      BusinessModel(
        id: 's-5',
        name: 'Iron Core Gym & Fitness',
        categoryName: 'Gym',
        address: 'Near Alandi Bus Stand',
        rating: 4.5,
        reviewCount: 120,
        priceLevel: '₹₹',
        distanceMeters: 1100,
        isOpenNow: false,
        isVerified: true,
        hasStudentDiscount: true,
        discountDetails: '₹800/mo Student Membership',
      ),
    ];

    if (query.isEmpty) return all;
    return all.where((b) {
      return b.name.toLowerCase().contains(query) ||
          b.categoryName.toLowerCase().contains(query) ||
          (b.discountDetails?.toLowerCase().contains(query) ?? false);
    }).toList();
  }

  void _resetFilters() {
    setState(() {
      _searchController.clear();
      _minRating = null;
      _priceLevel = null;
      _studentDiscountOnly = false;
      _openNowOnly = false;
      _sort = 'relevance';
    });
    _performSearch();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: const Text('Discover Local Places'),
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(60),
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
            child: TextField(
              controller: _searchController,
              onSubmitted: (_) => _performSearch(),
              textInputAction: TextInputAction.search,
              decoration: InputDecoration(
                hintText: 'Search mess, salon, cafe, xerox...',
                prefixIcon: const Icon(Icons.search_rounded, color: AppTheme.primary),
                suffixIcon: _searchController.text.isNotEmpty
                    ? IconButton(
                        icon: const Icon(Icons.close, color: AppTheme.textMuted),
                        onPressed: () {
                          _searchController.clear();
                          _performSearch();
                        },
                      )
                    : null,
              ),
            ),
          ),
        ),
      ),
      body: Column(
        children: [
          // Filter Chips Horizontal Scroll
          Container(
            color: Colors.white,
            padding: const EdgeInsets.symmetric(vertical: 8),
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: Row(
                children: [
                  // Student Discount filter
                  FilterChip(
                    label: const Text('🎓 Student Discount'),
                    selected: _studentDiscountOnly,
                    selectedColor: AppTheme.primary.withOpacity(0.15),
                    checkmarkColor: AppTheme.primary,
                    labelStyle: TextStyle(
                      color: _studentDiscountOnly ? AppTheme.primary : AppTheme.textPrimary,
                      fontWeight: _studentDiscountOnly ? FontWeight.bold : FontWeight.normal,
                      fontSize: 12,
                    ),
                    onSelected: (val) {
                      setState(() => _studentDiscountOnly = val);
                      _performSearch();
                    },
                  ),
                  const SizedBox(width: 8),

                  // Open Now filter
                  FilterChip(
                    label: const Text('🟢 Open Now'),
                    selected: _openNowOnly,
                    selectedColor: AppTheme.success.withOpacity(0.15),
                    checkmarkColor: AppTheme.success,
                    labelStyle: TextStyle(
                      color: _openNowOnly ? AppTheme.success : AppTheme.textPrimary,
                      fontWeight: _openNowOnly ? FontWeight.bold : FontWeight.normal,
                      fontSize: 12,
                    ),
                    onSelected: (val) {
                      setState(() => _openNowOnly = val);
                      _performSearch();
                    },
                  ),
                  const SizedBox(width: 8),

                  // 4+ Rating filter
                  FilterChip(
                    label: const Text('⭐ 4.0+'),
                    selected: _minRating == 4.0,
                    selectedColor: AppTheme.secondary.withOpacity(0.2),
                    onSelected: (val) {
                      setState(() => _minRating = val ? 4.0 : null);
                      _performSearch();
                    },
                  ),
                  const SizedBox(width: 8),

                  // Price ₹ filter
                  FilterChip(
                    label: const Text('₹ Budget Friendly'),
                    selected: _priceLevel == '₹',
                    selectedColor: AppTheme.primary.withOpacity(0.15),
                    onSelected: (val) {
                      setState(() => _priceLevel = val ? '₹' : null);
                      _performSearch();
                    },
                  ),
                ],
              ),
            ),
          ),

          // Quick tag suggestions if search query is empty
          if (_searchController.text.isEmpty)
            Container(
              padding: const EdgeInsets.symmetric(vertical: 8),
              child: SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                padding: const EdgeInsets.symmetric(horizontal: 16),
                child: Row(
                  children: _quickTags.map((tag) {
                    return Padding(
                      padding: const EdgeInsets.only(right: 8.0),
                      child: ActionChip(
                        label: Text(tag, style: const TextStyle(fontSize: 11, color: AppTheme.textSecondary)),
                        backgroundColor: Colors.white,
                        side: const BorderSide(color: AppTheme.border),
                        onPressed: () {
                          _searchController.text = tag;
                          _performSearch();
                        },
                      ),
                    );
                  }).toList(),
                ),
              ),
            ),

          const Divider(height: 1, color: AppTheme.border),

          // Results List
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : _results.isEmpty
                    ? _buildEmptyState()
                    : ListView.separated(
                        padding: const EdgeInsets.all(16),
                        itemCount: _results.length,
                        separatorBuilder: (_, __) => const SizedBox(height: 12),
                        itemBuilder: (ctx, idx) {
                          final biz = _results[idx];
                          return _buildSearchResultItem(biz);
                        },
                      ),
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
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
              child: const Icon(Icons.search_off_rounded, size: 48, color: AppTheme.primary),
            ),
            const SizedBox(height: 16),
            const Text(
              'No Places Found',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppTheme.textPrimary),
            ),
            const SizedBox(height: 8),
            const Text(
              'Try adjusting your search keywords or clearing active filters.',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 13, color: AppTheme.textSecondary),
            ),
            const SizedBox(height: 20),
            OutlinedButton(
              onPressed: _resetFilters,
              child: const Text('Reset All Filters'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSearchResultItem(BusinessModel biz) {
    return GestureDetector(
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
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
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
                      Row(
                        children: [
                          Expanded(
                            child: Text(
                              biz.name,
                              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                            ),
                          ),
                          if (biz.isVerified)
                            const Icon(Icons.verified, size: 16, color: AppTheme.success),
                        ],
                      ),
                      const SizedBox(height: 3),
                      Text(
                        '${biz.categoryName} • ${biz.priceLevel} • ${biz.address}',
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(color: AppTheme.textSecondary, fontSize: 12),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: AppTheme.secondary.withOpacity(0.15),
                    borderRadius: BorderRadius.circular(6),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.star_rounded, size: 14, color: AppTheme.secondary),
                      const SizedBox(width: 2),
                      Text(biz.rating.toStringAsFixed(1), style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12)),
                    ],
                  ),
                ),
                const SizedBox(width: 6),
                Text('(${biz.reviewCount})', style: const TextStyle(color: AppTheme.textMuted, fontSize: 11)),
                const SizedBox(width: 12),
                Icon(Icons.location_on_outlined, size: 14, color: AppTheme.textSecondary),
                Text(biz.formattedDistance, style: const TextStyle(fontSize: 12, color: AppTheme.textSecondary)),
                const Spacer(),
                if (biz.isOpenNow)
                  const Text('🟢 Open Now', style: TextStyle(color: AppTheme.success, fontSize: 11, fontWeight: FontWeight.bold))
                else
                  const Text('Closed', style: TextStyle(color: AppTheme.textMuted, fontSize: 11)),
              ],
            ),
            if (biz.hasStudentDiscount && biz.discountDetails != null) ...[
              const SizedBox(height: 8),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                decoration: BoxDecoration(
                  color: AppTheme.primary.withOpacity(0.06),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.school, size: 14, color: AppTheme.primary),
                    const SizedBox(width: 6),
                    Expanded(
                      child: Text(
                        biz.discountDetails!,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(color: AppTheme.primary, fontSize: 11, fontWeight: FontWeight.bold),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
