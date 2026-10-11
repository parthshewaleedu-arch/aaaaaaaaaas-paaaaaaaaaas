import 'package:flutter/material.dart';
import '../../core/services/api_service.dart';
import '../../core/services/storage_service.dart';
import '../../core/theme/app_theme.dart';
import '../../models/business_model.dart';
import '../../models/review_model.dart';
import '../review/add_review_screen.dart';

class BusinessDetailScreen extends StatefulWidget {
  final String businessId;
  final BusinessModel? initialBusiness;

  const BusinessDetailScreen({
    super.key,
    required this.businessId,
    this.initialBusiness,
  });

  @override
  State<BusinessDetailScreen> createState() => _BusinessDetailScreenState();
}

class _BusinessDetailScreenState extends State<BusinessDetailScreen> {
  late BusinessModel _business;
  bool _isLoading = true;
  bool _isSaved = false;
  List<ReviewModel> _reviews = [];

  @override
  void initState() {
    super.initState();
    _business = widget.initialBusiness ??
        BusinessModel(
          id: widget.businessId,
          name: 'Campus Partner Business',
          address: 'Alandi, Pune',
          categoryName: 'General',
        );
    _isSaved = StorageService.isBusinessSaved(widget.businessId);
    _loadDetails();
  }

  Future<void> _loadDetails() async {
    setState(() => _isLoading = true);

    final res = await ApiService.getBusinessDetail(widget.businessId);
    if (res.success && res.data != null) {
      _business = BusinessModel.fromJson(res.data!);
    } else if (widget.initialBusiness != null) {
      _business = widget.initialBusiness!;
    }

    _reviews = _getSampleReviews();

    if (mounted) {
      setState(() => _isLoading = false);
    }
  }

  List<ReviewModel> _getSampleReviews() {
    return [
      ReviewModel(
        id: 'rev-1',
        authorName: 'Snehal K. (Third Year CS)',
        isVerifiedStudent: true,
        rating: 4.5,
        dimensionRatings: {'Quality': 4.6, 'Hygiene': 4.2, 'Value': 4.8},
        comment: 'Best unlimited thali near campus! Very friendly uncle and clean dining space. The dal tadka on Wednesdays is unbeatable.',
        timeAgo: '2 days ago',
        helpfulCount: 14,
      ),
      ReviewModel(
        id: 'rev-2',
        authorName: 'Aditya P. (Mechanical)',
        isVerifiedStudent: true,
        rating: 4.0,
        dimensionRatings: {'Quality': 4.0, 'Hygiene': 4.0, 'Value': 4.2},
        comment: 'Great student discounts if you show MIT AOE ID card. Service is fast during lunch peak.',
        timeAgo: 'Last week',
        helpfulCount: 8,
      ),
    ];
  }

  Future<void> _toggleFavorite() async {
    final nowSaved = await StorageService.toggleSavedBusiness(_business.id);
    setState(() => _isSaved = nowSaved);
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(nowSaved ? 'Added to Saved Places' : 'Removed from Saved Places'),
        duration: const Duration(seconds: 1),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      body: CustomScrollView(
        slivers: [
          // Collapsible Image AppBar
          SliverAppBar(
            expandedHeight: 220,
            pinned: true,
            backgroundColor: AppTheme.primary,
            leading: CircleAvatar(
              backgroundColor: Colors.black.withOpacity(0.4),
              child: IconButton(
                icon: const Icon(Icons.arrow_back, color: Colors.white),
                onPressed: () => Navigator.pop(context),
              ),
            ),
            actions: [
              CircleAvatar(
                backgroundColor: Colors.black.withOpacity(0.4),
                child: IconButton(
                  icon: Icon(_isSaved ? Icons.bookmark : Icons.bookmark_border, color: Colors.white),
                  onPressed: _toggleFavorite,
                ),
              ),
              const SizedBox(width: 8),
              CircleAvatar(
                backgroundColor: Colors.black.withOpacity(0.4),
                child: IconButton(
                  icon: const Icon(Icons.share, color: Colors.white),
                  onPressed: () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Sharing campus recommendation')),
                    );
                  },
                ),
              ),
              const SizedBox(width: 12),
            ],
            flexibleSpace: FlexibleSpaceBar(
              background: Container(
                color: AppTheme.primary,
                child: Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.store_mall_directory_rounded, size: 70, color: Colors.white.withOpacity(0.7)),
                      const SizedBox(height: 8),
                      Text(
                        _business.categoryName.toUpperCase(),
                        style: TextStyle(
                          color: Colors.white.withOpacity(0.8),
                          letterSpacing: 2.0,
                          fontSize: 12,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),

          // Business Content Body
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Title and Verified Badge
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Expanded(
                        child: Text(
                          _business.name,
                          style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w800, color: AppTheme.textPrimary),
                        ),
                      ),
                      if (_business.isVerified)
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                          decoration: BoxDecoration(
                            color: AppTheme.success.withOpacity(0.12),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: const Row(
                            children: [
                              Icon(Icons.verified, size: 14, color: AppTheme.success),
                              SizedBox(width: 4),
                              Text('Verified', style: TextStyle(color: AppTheme.success, fontSize: 11, fontWeight: FontWeight.bold)),
                            ],
                          ),
                        ),
                    ],
                  ),

                  const SizedBox(height: 6),

                  // Rating, distance, hours
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
                            const Icon(Icons.star_rounded, size: 15, color: AppTheme.secondary),
                            const SizedBox(width: 3),
                            Text(_business.rating.toStringAsFixed(1), style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                          ],
                        ),
                      ),
                      const SizedBox(width: 6),
                      Text('${_business.reviewCount} student reviews', style: const TextStyle(color: AppTheme.textSecondary, fontSize: 13)),
                      const SizedBox(width: 8),
                      const Text('•', style: TextStyle(color: AppTheme.textMuted)),
                      const SizedBox(width: 8),
                      Text(_business.formattedDistance, style: const TextStyle(color: AppTheme.textSecondary, fontSize: 13)),
                      const SizedBox(width: 8),
                      const Text('•', style: TextStyle(color: AppTheme.textMuted)),
                      const SizedBox(width: 8),
                      Text(_business.priceLevel, style: const TextStyle(color: AppTheme.textSecondary, fontWeight: FontWeight.bold, fontSize: 13)),
                    ],
                  ),

                  const SizedBox(height: 12),

                  // Open status banner
                  Row(
                    children: [
                      const Icon(Icons.access_time_rounded, size: 16, color: AppTheme.success),
                      const SizedBox(width: 6),
                      Text(
                        _business.isOpenNow ? 'Open Now (${_business.openingHours ?? "until 10:30 PM"})' : 'Closed',
                        style: TextStyle(
                          color: _business.isOpenNow ? AppTheme.success : AppTheme.error,
                          fontWeight: FontWeight.w600,
                          fontSize: 13,
                        ),
                      ),
                    ],
                  ),

                  const SizedBox(height: 16),

                  // Student Discount callout card
                  if (_business.hasStudentDiscount)
                    Container(
                      padding: const EdgeInsets.all(14),
                      decoration: BoxDecoration(
                        color: AppTheme.primary.withOpacity(0.08),
                        borderRadius: BorderRadius.circular(14),
                        border: Border.all(color: AppTheme.primary.withOpacity(0.25)),
                      ),
                      child: Row(
                        children: [
                          const Icon(Icons.school_rounded, color: AppTheme.primary, size: 26),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const Text(
                                  'Student Discount Available',
                                  style: TextStyle(fontWeight: FontWeight.bold, color: AppTheme.primary, fontSize: 14),
                                ),
                                const SizedBox(height: 2),
                                Text(
                                  _business.discountDetails ?? 'Show your valid College ID for special student rates',
                                  style: const TextStyle(fontSize: 12, color: AppTheme.textPrimary),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),

                  const SizedBox(height: 20),

                  // Quick Action Buttons (Call, Directions, WhatsApp)
                  Row(
                    children: [
                      Expanded(
                        child: OutlinedButton.icon(
                          icon: const Icon(Icons.call, size: 18),
                          label: const Text('Call'),
                          onPressed: () {
                            ScaffoldMessenger.of(context).showSnackBar(
                              SnackBar(content: Text('Calling ${_business.phone ?? "+91 98765 43210"}')),
                            );
                          },
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: ElevatedButton.icon(
                          icon: const Icon(Icons.directions, size: 18),
                          label: const Text('Directions'),
                          onPressed: () {
                            ScaffoldMessenger.of(context).showSnackBar(
                              SnackBar(content: Text('Navigating ${_business.formattedDistance} from MIT AOE Campus')),
                            );
                          },
                        ),
                      ),
                    ],
                  ),

                  const SizedBox(height: 24),

                  // Address card
                  Container(
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(14),
                      border: Border.all(color: AppTheme.border),
                    ),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Icon(Icons.location_on_rounded, color: AppTheme.primary, size: 20),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Text('Address', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                              const SizedBox(height: 2),
                              Text(_business.address, style: const TextStyle(color: AppTheme.textSecondary, fontSize: 13)),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: 24),

                  // Structured Ratings by Dimension (Section 13)
                  const Text(
                    'Ratings by Category',
                    style: TextStyle(fontSize: 17, fontWeight: FontWeight.w800, color: AppTheme.textPrimary),
                  ),
                  const SizedBox(height: 12),
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: AppTheme.border),
                    ),
                    child: Column(
                      children: [
                        _buildDimensionBar('Food Quality / Work', _business.dimensionRatings['Food Quality'] ?? 4.4),
                        const SizedBox(height: 10),
                        _buildDimensionBar('Hygiene & Cleanliness', _business.dimensionRatings['Hygiene'] ?? 3.8),
                        const SizedBox(height: 10),
                        _buildDimensionBar('Quantity / Completeness', _business.dimensionRatings['Quantity'] ?? 4.5),
                        const SizedBox(height: 10),
                        _buildDimensionBar('Value for Money', _business.dimensionRatings['Value'] ?? 4.3),
                        const SizedBox(height: 10),
                        _buildDimensionBar('Student Friendliness', 4.6),
                      ],
                    ),
                  ),

                  const SizedBox(height: 24),

                  // Services & Pricing with Freshness Indicator
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text(
                        'Services & Pricing',
                        style: TextStyle(fontSize: 17, fontWeight: FontWeight.w800, color: AppTheme.textPrimary),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                        decoration: BoxDecoration(
                          color: AppTheme.success.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(6),
                        ),
                        child: const Text('Price verified 4 days ago', style: TextStyle(color: AppTheme.success, fontSize: 10, fontWeight: FontWeight.bold)),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  _buildServiceMenu(),

                  const SizedBox(height: 24),

                  // Reviews Section & Add Review Button
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text(
                        'Student Reviews',
                        style: TextStyle(fontSize: 17, fontWeight: FontWeight.w800, color: AppTheme.textPrimary),
                      ),
                      TextButton.icon(
                        icon: const Icon(Icons.edit, size: 16),
                        label: const Text('Write Review'),
                        onPressed: () {
                          Navigator.of(context).push(
                            MaterialPageRoute(
                              builder: (_) => AddReviewScreen(
                                businessId: _business.id,
                                businessName: _business.name,
                              ),
                            ),
                          );
                        },
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),

                  ListView.separated(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    itemCount: _reviews.length,
                    separatorBuilder: (_, __) => const SizedBox(height: 12),
                    itemBuilder: (ctx, idx) {
                      final rev = _reviews[idx];
                      return _buildReviewCard(rev);
                    },
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDimensionBar(String label, double rating) {
    return Row(
      children: [
        Expanded(
          flex: 4,
          child: Text(label, style: const TextStyle(fontSize: 13, color: AppTheme.textSecondary)),
        ),
        Expanded(
          flex: 5,
          child: ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: rating / 5.0,
              backgroundColor: AppTheme.border,
              valueColor: const AlwaysStoppedAnimation<Color>(AppTheme.primary),
              minHeight: 8,
            ),
          ),
        ),
        const SizedBox(width: 10),
        SizedBox(
          width: 28,
          child: Text(
            rating.toStringAsFixed(1),
            style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12),
          ),
        ),
      ],
    );
  }

  Widget _buildServiceMenu() {
    final sampleServices = [
      {'name': 'Unlimited Student Thali', 'price': '₹90', 'desc': '2 sabzi, 4 roti, dal, rice, sweet on weekends'},
      {'name': 'Single Meal Tiffin', 'price': '₹75', 'desc': 'Packed hot in foil containers'},
      {'name': 'Monthly Mess Pass', 'price': '₹2,400', 'desc': 'Lunch + Dinner 30 days coupon booklet'},
    ];

    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppTheme.border),
      ),
      child: ListView.separated(
        shrinkWrap: true,
        physics: const NeverScrollableScrollPhysics(),
        itemCount: sampleServices.length,
        separatorBuilder: (_, __) => const Divider(height: 1, color: AppTheme.border),
        itemBuilder: (ctx, idx) {
          final s = sampleServices[idx];
          return ListTile(
            title: Text(s['name']!, style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14)),
            subtitle: Text(s['desc']!, style: const TextStyle(fontSize: 12, color: AppTheme.textSecondary)),
            trailing: Text(
              s['price']!,
              style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 15, color: AppTheme.primary),
            ),
          );
        },
      ),
    );
  }

  Widget _buildReviewCard(ReviewModel rev) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: AppTheme.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              CircleAvatar(
                radius: 16,
                backgroundColor: AppTheme.primary.withOpacity(0.12),
                child: Text(
                  rev.authorName.substring(0, 1),
                  style: const TextStyle(color: AppTheme.primary, fontWeight: FontWeight.bold),
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(rev.authorName, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                    if (rev.isVerifiedStudent)
                      const Text('🎓 Verified Student', style: TextStyle(color: AppTheme.primary, fontSize: 11, fontWeight: FontWeight.w600)),
                  ],
                ),
              ),
              Text(rev.timeAgo, style: const TextStyle(color: AppTheme.textMuted, fontSize: 11)),
            ],
          ),
          const SizedBox(height: 8),
          Row(
            children: List.generate(5, (index) {
              return Icon(
                index < rev.rating.round() ? Icons.star_rounded : Icons.star_border_rounded,
                size: 16,
                color: AppTheme.secondary,
              );
            }),
          ),
          const SizedBox(height: 8),
          Text(rev.comment, style: const TextStyle(fontSize: 13, height: 1.4)),
          const SizedBox(height: 10),
          Row(
            children: [
              const Icon(Icons.thumb_up_alt_outlined, size: 14, color: AppTheme.textMuted),
              const SizedBox(width: 4),
              Text('Helpful (${rev.helpfulCount})', style: const TextStyle(fontSize: 11, color: AppTheme.textMuted)),
              const Spacer(),
              const Text('Report', style: TextStyle(fontSize: 11, color: AppTheme.textMuted)),
            ],
          ),
        ],
      ),
    );
  }
}
