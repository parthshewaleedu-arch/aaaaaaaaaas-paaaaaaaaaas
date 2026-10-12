import 'package:flutter/material.dart';
import '../../core/constants/api_constants.dart';
import '../../core/services/api_service.dart';
import '../../core/services/app_repository.dart';
import '../../core/services/storage_service.dart';
import '../../core/theme/app_theme.dart';
import '../../models/business_model.dart';
import '../business/business_detail_screen.dart';

class HomeScreen extends StatefulWidget {
  final VoidCallback onNavigateToSearch;
  const HomeScreen({super.key, required this.onNavigateToSearch});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  bool _isLoading = true;
  String _campusName = ApiConstants.defaultCampusName;
  List<BusinessModel> _popularBusinesses = [];
  List<BusinessModel> _topRatedBusinesses = [];

  final List<Map<String, dynamic>> _quickCategories = [
    {'name': 'Food & Mess', 'icon': Icons.restaurant_rounded, 'color': Color(0xFFF97316)},
    {'name': 'Cafes', 'icon': Icons.local_cafe_rounded, 'color': Color(0xFF8B5CF6)},
    {'name': 'Laundry', 'icon': Icons.local_laundry_service_rounded, 'color': Color(0xFF0EA5E9)},
    {'name': 'Medical', 'icon': Icons.local_pharmacy_rounded, 'color': Color(0xFFEF4444)},
    {'name': 'Gym & Fitness', 'icon': Icons.fitness_center_rounded, 'color': Color(0xFF10B981)},
    {'name': 'Salons', 'icon': Icons.content_cut_rounded, 'color': Color(0xFFEC4899)},
    {'name': 'Stationery/Xerox', 'icon': Icons.print_rounded, 'color': Color(0xFF6366F1)},
    {'name': 'Repairs', 'icon': Icons.build_rounded, 'color': Color(0xFFF59E0B)},
  ];

  @override
  void initState() {
    super.initState();
    _loadDataInstantly();
  }

  void _loadData() => _loadDataInstantly();

  void _loadDataInstantly() {
    _campusName = StorageService.getCampusName();
    final verifiedMaps = AppRepository.getVerifiedBusinesses();
    final parsed = verifiedMaps.map((b) => BusinessModel.fromJson(b)).toList();
    _popularBusinesses = parsed;
    _topRatedBusinesses = List.from(parsed)..sort((a, b) => b.rating.compareTo(a.rating));
    _isLoading = false;
    setState(() {});
  }

  List<BusinessModel> _getSampleCampusBusinesses() {
    return [
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
        discountDetails: '15% Off Monthly Mess Pass with MIT AOE ID',
        dimensionRatings: {'Food Quality': 4.7, 'Hygiene': 4.4, 'Quantity': 4.8, 'Value': 4.9},
      ),
      BusinessModel(
        id: 'sample-2',
        name: 'Campus Xerox & Stationery Hub',
        address: 'Opposite Main Gate, Alandi',
        categoryName: 'Stationery/Xerox',
        rating: 4.8,
        reviewCount: 189,
        priceLevel: '₹',
        distanceMeters: 120,
        isOpenNow: true,
        isVerified: true,
        hasStudentDiscount: true,
        discountDetails: '₹1.50/page Spiral Binding discount',
        dimensionRatings: {'Speed': 4.9, 'Value': 4.8, 'Quality': 4.7},
      ),
      BusinessModel(
        id: 'sample-3',
        name: 'Chai Shai & Cafe 24',
        address: 'Dnyaneshwar Nagar, Alandi',
        categoryName: 'Cafes',
        rating: 4.4,
        reviewCount: 245,
        priceLevel: '₹₹',
        distanceMeters: 620,
        isOpenNow: true,
        isVerified: true,
        hasStudentDiscount: true,
        discountDetails: 'Free Wi-Fi & 10% on Student Combos',
        dimensionRatings: {'Ambience': 4.6, 'Wifi': 4.5, 'Taste': 4.3},
      ),
      BusinessModel(
        id: 'sample-4',
        name: 'Alandi QuickWash & Dry Clean',
        address: 'Markal Road, Alandi',
        categoryName: 'Laundry',
        rating: 4.3,
        reviewCount: 98,
        priceLevel: '₹₹',
        distanceMeters: 800,
        isOpenNow: true,
        isVerified: true,
        hasStudentDiscount: true,
        discountDetails: '₹50/kg Student Laundry Special',
        dimensionRatings: {'Speed': 4.2, 'Care': 4.4, 'Price': 4.5},
      ),
    ];
  }

  void _showCampusSwitcher() {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => Container(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Select Campus',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            ListTile(
              leading: const Icon(Icons.school, color: AppTheme.primary),
              title: const Text('MIT Academy of Engineering (MIT AOE)'),
              subtitle: const Text('Alandi, Pune • Active Pilot (3 km radius)'),
              trailing: const Icon(Icons.check_circle, color: AppTheme.success),
              onTap: () async {
                await StorageService.setCampus(
                  id: 'mit-aoe-pilot',
                  name: 'MIT Academy of Engineering (MIT AOE)',
                );
                Navigator.pop(ctx);
                _loadData();
              },
            ),
            ListTile(
              leading: const Icon(Icons.location_city, color: AppTheme.textSecondary),
              title: const Text('COEP Tech University'),
              subtitle: const Text('Shivajinagar, Pune'),
              onTap: () async {
                await StorageService.setCampus(
                  id: 'coep-pune',
                  name: 'COEP Tech University, Pune',
                );
                Navigator.pop(ctx);
                _loadData();
              },
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        titleSpacing: 16,
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Good evening, Student 👋',
              style: TextStyle(fontSize: 14, fontWeight: FontWeight.w500, color: AppTheme.textSecondary),
            ),
            GestureDetector(
              onTap: _showCampusSwitcher,
              child: Row(
                children: [
                  const Icon(Icons.school_rounded, size: 16, color: AppTheme.primary),
                  const SizedBox(width: 4),
                  Flexible(
                    child: Text(
                      _campusName,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w700, color: AppTheme.textPrimary),
                    ),
                  ),
                  const Icon(Icons.keyboard_arrow_down, size: 18, color: AppTheme.textSecondary),
                ],
              ),
            ),
          ],
        ),
        actions: [
          Container(
            margin: const EdgeInsets.only(right: 16),
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
            decoration: BoxDecoration(
              color: AppTheme.success.withOpacity(0.12),
              borderRadius: BorderRadius.circular(20),
            ),
            child: const Row(
              children: [
                Icon(Icons.radar_rounded, size: 14, color: AppTheme.success),
                SizedBox(width: 4),
                Text('3 km', style: TextStyle(color: AppTheme.success, fontWeight: FontWeight.w700, fontSize: 11)),
              ],
            ),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () async => _loadDataInstantly(),
        color: AppTheme.primary,
        child: SingleChildScrollView(
          padding: const EdgeInsets.only(bottom: 32),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Search input box shortcut
              Padding(
                padding: const EdgeInsets.all(16.0),
                child: GestureDetector(
                  onTap: widget.onNavigateToSearch,
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(14),
                      border: Border.all(color: AppTheme.border),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withOpacity(0.03),
                          blurRadius: 8,
                          offset: const Offset(0, 3),
                        ),
                      ],
                    ),
                    child: const Row(
                      children: [
                        Icon(Icons.search_rounded, color: AppTheme.primary, size: 22),
                        SizedBox(width: 12),
                        Expanded(
                          child: Text(
                            'What do you need? (mess, printing, cafe...)',
                            style: TextStyle(color: AppTheme.textMuted, fontSize: 14),
                          ),
                        ),
                        Icon(Icons.tune_rounded, color: AppTheme.textSecondary, size: 20),
                      ],
                    ),
                  ),
                ),
              ),

              // Student Deals Banner
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16.0),
                child: Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      colors: [Color(0xFF0F766E), Color(0xFF0D9488)],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                    borderRadius: BorderRadius.circular(16),
                    boxShadow: [
                      BoxShadow(
                        color: AppTheme.primary.withOpacity(0.2),
                        blurRadius: 10,
                        offset: const Offset(0, 4),
                      ),
                    ],
                  ),
                  child: Row(
                    children: [
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                              decoration: BoxDecoration(
                                color: Colors.white.withOpacity(0.2),
                                borderRadius: BorderRadius.circular(6),
                              ),
                              child: const Text(
                                'CAMPUS EXCLUSIVE',
                                style: TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold),
                              ),
                            ),
                            const SizedBox(height: 6),
                            const Text(
                              'Verified Student Discounts',
                              style: TextStyle(color: Colors.white, fontSize: 17, fontWeight: FontWeight.w800),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              'Flash your college ID for up to 20% off at local mess, print shops & cafes',
                              style: TextStyle(color: Colors.white.withOpacity(0.9), fontSize: 12),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(width: 8),
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: const Icon(Icons.local_offer_rounded, color: AppTheme.primary, size: 28),
                      ),
                    ],
                  ),
                ),
              ),

              const SizedBox(height: 24),

              // Quick Categories Grid
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16.0),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text(
                      'Quick Categories',
                      style: TextStyle(fontSize: 17, fontWeight: FontWeight.w800, color: AppTheme.textPrimary),
                    ),
                    GestureDetector(
                      onTap: widget.onNavigateToSearch,
                      child: const Text(
                        'See All',
                        style: TextStyle(color: AppTheme.primary, fontWeight: FontWeight.w600, fontSize: 13),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 12),
              SizedBox(
                height: 100,
                child: ListView.separated(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  scrollDirection: Axis.horizontal,
                  itemCount: _quickCategories.length,
                  separatorBuilder: (_, __) => const SizedBox(width: 14),
                  itemBuilder: (ctx, idx) {
                    final cat = _quickCategories[idx];
                    return GestureDetector(
                      onTap: widget.onNavigateToSearch,
                      child: Column(
                        children: [
                          Container(
                            width: 58,
                            height: 58,
                            decoration: BoxDecoration(
                              color: (cat['color'] as Color).withOpacity(0.12),
                              borderRadius: BorderRadius.circular(16),
                            ),
                            child: Icon(cat['icon'] as IconData, color: cat['color'] as Color, size: 26),
                          ),
                          const SizedBox(height: 6),
                          SizedBox(
                            width: 66,
                            child: Text(
                              cat['name'] as String,
                              textAlign: TextAlign.center,
                              maxLines: 2,
                              overflow: TextOverflow.ellipsis,
                              style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600),
                            ),
                          ),
                        ],
                      ),
                    );
                  },
                ),
              ),

              const SizedBox(height: 24),

              // Popular Near You
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16.0),
                child: const Text(
                  'Popular Near Campus',
                  style: TextStyle(fontSize: 17, fontWeight: FontWeight.w800, color: AppTheme.textPrimary),
                ),
              ),
              const SizedBox(height: 12),
              _isLoading
                  ? const Center(child: Padding(padding: EdgeInsets.all(24), child: CircularProgressIndicator()))
                  : SizedBox(
                      height: 220,
                      child: ListView.separated(
                        padding: const EdgeInsets.symmetric(horizontal: 16),
                        scrollDirection: Axis.horizontal,
                        itemCount: _popularBusinesses.length,
                        separatorBuilder: (_, __) => const SizedBox(width: 14),
                        itemBuilder: (ctx, idx) {
                          final biz = _popularBusinesses[idx];
                          return _buildPopularCard(biz);
                        },
                      ),
                    ),

              const SizedBox(height: 24),

              // Highly Rated by Students
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16.0),
                child: const Text(
                  'Highly Rated by Students ⭐',
                  style: TextStyle(fontSize: 17, fontWeight: FontWeight.w800, color: AppTheme.textPrimary),
                ),
              ),
              const SizedBox(height: 12),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16.0),
                child: ListView.separated(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  itemCount: _topRatedBusinesses.length,
                  separatorBuilder: (_, __) => const SizedBox(height: 12),
                  itemBuilder: (ctx, idx) {
                    final biz = _topRatedBusinesses[idx];
                    return _buildVerticalBizCard(biz);
                  },
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildPopularCard(BusinessModel biz) {
    return GestureDetector(
      onTap: () {
        Navigator.of(context).push(
          MaterialPageRoute(builder: (_) => BusinessDetailScreen(businessId: biz.id, initialBusiness: biz)),
        );
      },
      child: Container(
        width: 220,
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: AppTheme.border),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.03),
              blurRadius: 6,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              height: 100,
              decoration: BoxDecoration(
                color: AppTheme.primary.withOpacity(0.08),
                borderRadius: const BorderRadius.vertical(top: Radius.circular(15)),
              ),
              child: Stack(
                children: [
                  Center(
                    child: Icon(Icons.storefront_rounded, size: 48, color: AppTheme.primary.withOpacity(0.4)),
                  ),
                  Positioned(
                    top: 8,
                    left: 8,
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 3),
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.9),
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: Row(
                        children: [
                          const Icon(Icons.location_on, size: 12, color: AppTheme.primary),
                          const SizedBox(width: 2),
                          Text(biz.formattedDistance, style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold)),
                        ],
                      ),
                    ),
                  ),
                  if (biz.isVerified)
                    Positioned(
                      top: 8,
                      right: 8,
                      child: Container(
                        padding: const EdgeInsets.all(4),
                        decoration: BoxDecoration(
                          color: AppTheme.success,
                          shape: BoxShape.circle,
                        ),
                        child: const Icon(Icons.verified, size: 12, color: Colors.white),
                      ),
                    ),
                ],
              ),
            ),
            Padding(
              padding: const EdgeInsets.all(10.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    biz.name,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    biz.categoryName,
                    style: const TextStyle(color: AppTheme.textSecondary, fontSize: 12),
                  ),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 2),
                        decoration: BoxDecoration(
                          color: AppTheme.secondary.withOpacity(0.15),
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: Row(
                          children: [
                            const Icon(Icons.star_rounded, size: 13, color: AppTheme.secondary),
                            const SizedBox(width: 2),
                            Text(
                              biz.rating.toStringAsFixed(1),
                              style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Color(0xFFB45309)),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(width: 6),
                      Text('(${biz.reviewCount})', style: const TextStyle(color: AppTheme.textMuted, fontSize: 11)),
                      const Spacer(),
                      Text(biz.priceLevel, style: const TextStyle(fontWeight: FontWeight.bold, color: AppTheme.textSecondary, fontSize: 12)),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildVerticalBizCard(BusinessModel biz) {
    return GestureDetector(
      onTap: () {
        Navigator.of(context).push(
          MaterialPageRoute(builder: (_) => BusinessDetailScreen(businessId: biz.id, initialBusiness: biz)),
        );
      },
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: AppTheme.border),
        ),
        child: Row(
          children: [
            Container(
              width: 64,
              height: 64,
              decoration: BoxDecoration(
                color: AppTheme.primary.withOpacity(0.08),
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Icon(Icons.storefront_rounded, color: AppTheme.primary, size: 30),
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
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                        ),
                      ),
                      if (biz.isVerified)
                        const Icon(Icons.verified, size: 15, color: AppTheme.success),
                    ],
                  ),
                  const SizedBox(height: 2),
                  Text(
                    '${biz.categoryName} • ${biz.formattedDistance}',
                    style: const TextStyle(color: AppTheme.textSecondary, fontSize: 12),
                  ),
                  const SizedBox(height: 6),
                  Row(
                    children: [
                      const Icon(Icons.star_rounded, size: 15, color: AppTheme.secondary),
                      const SizedBox(width: 2),
                      Text(
                        biz.rating.toStringAsFixed(1),
                        style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold),
                      ),
                      Text(' (${biz.reviewCount} reviews)', style: const TextStyle(color: AppTheme.textMuted, fontSize: 11)),
                      const Spacer(),
                      if (biz.hasStudentDiscount)
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                          decoration: BoxDecoration(
                            color: AppTheme.primary.withOpacity(0.1),
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: const Text('🎓 Student Discount', style: TextStyle(color: AppTheme.primary, fontSize: 10, fontWeight: FontWeight.bold)),
                        ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
