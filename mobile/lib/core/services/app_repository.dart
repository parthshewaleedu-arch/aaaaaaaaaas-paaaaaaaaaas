import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../../models/business_model.dart';
import '../../models/offer_model.dart';

class CategoryPlan {
  final String name;
  final int monthlyFee; // In Rupees
  final String icon;

  const CategoryPlan({
    required this.name,
    required this.monthlyFee,
    required this.icon,
  });
}

class AppRepository {
  static const String _keyBusinesses = 'aaspaas_all_businesses';
  static const String _keyUniqueStudents = 'aaspaas_unique_students';
  static const String _keyOffers = 'aaspaas_all_offers';

  static SharedPreferences? _prefs;

  // Exact categories & pricing per user requirements
  static const List<CategoryPlan> categoriesWithPlans = [
    CategoryPlan(name: 'HOSTEL (BOYS SEPARATE)', monthlyFee: 2000, icon: 'hotel'),
    CategoryPlan(name: 'HOSTEL (GIRLS SEPARATE)', monthlyFee: 2000, icon: 'hotel'),
    CategoryPlan(name: 'HOTEL (LUNCH AND DINNER)', monthlyFee: 1500, icon: 'restaurant'),
    CategoryPlan(name: 'MESS', monthlyFee: 1500, icon: 'restaurant_menu'),
    CategoryPlan(name: 'CAFE', monthlyFee: 500, icon: 'local_cafe'),
    CategoryPlan(name: 'SNACKS HOTEL', monthlyFee: 500, icon: 'fastfood'),
    CategoryPlan(name: 'GYM', monthlyFee: 500, icon: 'fitness_center'),
    CategoryPlan(name: 'MOBILE REPAIRING', monthlyFee: 500, icon: 'build'),
    CategoryPlan(name: 'HOSPITAL', monthlyFee: 500, icon: 'local_hospital'),
    CategoryPlan(name: 'CLOTHES', monthlyFee: 500, icon: 'checkroom'),
    CategoryPlan(name: 'SHOES', monthlyFee: 500, icon: 'shopping_bag'),
    CategoryPlan(name: 'STATIONARY', monthlyFee: 300, icon: 'edit_note'),
    CategoryPlan(name: 'LAUNDRY', monthlyFee: 300, icon: 'local_laundry_service'),
    CategoryPlan(name: 'SALON', monthlyFee: 300, icon: 'content_cut'),
    CategoryPlan(name: 'PARLOUR', monthlyFee: 300, icon: 'face'),
    CategoryPlan(name: 'MEDICAL', monthlyFee: 300, icon: 'local_pharmacy'),
    CategoryPlan(name: 'SPECTACLES', monthlyFee: 300, icon: 'visibility'),
    CategoryPlan(name: 'BAKERY', monthlyFee: 300, icon: 'bakery_dining'),
    CategoryPlan(name: 'SWEETS', monthlyFee: 300, icon: 'cake'),
    CategoryPlan(name: 'CHAT CENTRE', monthlyFee: 300, icon: 'lunch_dining'),
    CategoryPlan(name: 'DAIRY', monthlyFee: 300, icon: 'egg_alt'),
    CategoryPlan(name: 'GROCERY', monthlyFee: 300, icon: 'shopping_cart'),
    CategoryPlan(name: 'ELECTRONICS', monthlyFee: 300, icon: 'electrical_services'),
    CategoryPlan(name: 'RETAIL SHOPS', monthlyFee: 300, icon: 'storefront'),
    CategoryPlan(name: 'GARAGE', monthlyFee: 300, icon: 'car_repair'),
    CategoryPlan(name: 'CYBER CAFE', monthlyFee: 300, icon: 'computer'),
    CategoryPlan(name: 'MALL', monthlyFee: 300, icon: 'local_mall'),
    CategoryPlan(name: 'GIFT SHOPS', monthlyFee: 300, icon: 'card_giftcard'),
    CategoryPlan(name: 'ACCESSORIES', monthlyFee: 300, icon: 'watch'),
    CategoryPlan(name: 'FRUIT CENTRE', monthlyFee: 300, icon: 'apple'),
    CategoryPlan(name: 'FURNITURE', monthlyFee: 300, icon: 'chair'),
  ];

  static int getFeeForCategory(String categoryName) {
    for (final plan in categoriesWithPlans) {
      if (plan.name.toLowerCase() == categoryName.toLowerCase()) {
        return plan.monthlyFee;
      }
    }
    return 300; // default minimum
  }

  // In-memory instant cache
  static List<Map<String, dynamic>> _businesses = [];
  static Set<String> _uniqueStudents = {};
  static List<Map<String, dynamic>> _offers = [];

  static Future<void> init() async {
    _prefs ??= await SharedPreferences.getInstance();
    _loadFromStorage();
  }

  static void _loadFromStorage() {
    final rawBiz = _prefs?.getString(_keyBusinesses);
    if (rawBiz != null) {
      try {
        final list = jsonDecode(rawBiz) as List;
        _businesses = list.cast<Map<String, dynamic>>();
      } catch (_) {
        _businesses = [];
      }
    } else {
      _businesses = [];
    }

    final rawStudents = _prefs?.getStringList(_keyUniqueStudents);
    if (rawStudents != null) {
      _uniqueStudents = rawStudents.toSet();
    } else {
      _uniqueStudents = {};
    }

    final rawOffers = _prefs?.getString(_keyOffers);
    if (rawOffers != null) {
      try {
        final list = jsonDecode(rawOffers) as List;
        _offers = list.cast<Map<String, dynamic>>();
      } catch (_) {
        _offers = [];
      }
    } else {
      _offers = [];
    }

    // If completely first launch, seed with default MIT AOE pilot sample businesses
    if (_businesses.isEmpty) {
      _seedDefaultBusinesses();
    }
  }

  static Future<void> _persistBusinesses() async {
    await _prefs?.setString(_keyBusinesses, jsonEncode(_businesses));
  }

  static Future<void> _persistStudents() async {
    await _prefs?.setStringList(_keyUniqueStudents, _uniqueStudents.toList());
  }

  static Future<void> _persistOffers() async {
    await _prefs?.setString(_keyOffers, jsonEncode(_offers));
  }

  // --- STUDENT TRACKING ---
  static void registerStudentLogin(String email) {
    if (email.isNotEmpty && !_uniqueStudents.contains(email)) {
      _uniqueStudents.add(email);
      _persistStudents();
    }
  }

  static int getUniqueStudentsCount() {
    return _uniqueStudents.isEmpty ? 1 : _uniqueStudents.length;
  }

  // --- BUSINESS OPERATIONS ---

  static Map<String, dynamic>? getBusinessByOwner(String ownerEmail) {
    for (final b in _businesses) {
      if (b['owner_email'] == ownerEmail) {
        return b;
      }
    }
    return null;
  }

  static List<Map<String, dynamic>> getAllBusinesses() {
    return List.unmodifiable(_businesses);
  }

  static List<Map<String, dynamic>> getVerifiedBusinesses() {
    return _businesses.where((b) => b['status'] == 'VERIFIED').toList();
  }

  static List<Map<String, dynamic>> getPendingBusinesses() {
    return _businesses.where((b) => b['status'] == 'PENDING_REVIEW').toList();
  }

  static Future<Map<String, dynamic>> addOrUpdateBusiness({
    required String ownerEmail,
    required String name,
    required String categoryName,
    required String address,
    required String phone,
    String? whatsapp,
    required String openingHours,
    required String priceLevel,
    required String discountDetails,
    required String description,
    String? googleMapsUrl,
    List<Map<String, dynamic>>? services,
  }) async {
    final fee = getFeeForCategory(categoryName);
    final id = 'biz-${DateTime.now().millisecondsSinceEpoch}';

    // Check if owner already has a listing to update
    final existingIndex = _businesses.indexWhere((b) => b['owner_email'] == ownerEmail);

    final bizData = <String, dynamic>{
      'id': existingIndex != -1 ? _businesses[existingIndex]['id'] : id,
      'owner_email': ownerEmail,
      'name': name,
      'category_name': categoryName,
      'monthly_fee': fee,
      'address': address,
      'phone': phone,
      'whatsapp': whatsapp ?? phone,
      'opening_hours_text': openingHours,
      'price_level': priceLevel,
      'has_student_discount': discountDetails.trim().isNotEmpty,
      'discount_details': discountDetails,
      'description': description,
      'google_maps_url': googleMapsUrl ?? 'https://maps.google.com/?q=18.6757,73.8967',
      'status': 'PENDING_REVIEW', // Awaiting Admin Approval!
      'rating': existingIndex != -1 ? _businesses[existingIndex]['rating'] ?? 4.5 : 4.5,
      'review_count': existingIndex != -1 ? _businesses[existingIndex]['review_count'] ?? 1 : 0,
      'distance_meters': 350.0,
      'services': services ?? [
        {'name': 'Standard Student Service', 'price': 100.0, 'description': 'Standard package rate'}
      ],
      'created_at': DateTime.now().toIso8601String(),
    };

    if (existingIndex != -1) {
      _businesses[existingIndex] = bizData;
    } else {
      _businesses.insert(0, bizData);
    }

    await _persistBusinesses();
    return bizData;
  }

  static Future<void> approveBusiness(String businessId) async {
    final idx = _businesses.indexWhere((b) => b['id'] == businessId);
    if (idx != -1) {
      _businesses[idx]['status'] = 'VERIFIED';
      await _persistBusinesses();
    }
  }

  static Future<void> rejectBusiness(String businessId) async {
    final idx = _businesses.indexWhere((b) => b['id'] == businessId);
    if (idx != -1) {
      _businesses[idx]['status'] = 'REJECTED';
      await _persistBusinesses();
    }
  }

  // --- SERVICES / MENU ---
  static Future<void> addServiceToBusiness(String businessId, Map<String, dynamic> service) async {
    final idx = _businesses.indexWhere((b) => b['id'] == businessId);
    if (idx != -1) {
      final services = List<Map<String, dynamic>>.from(_businesses[idx]['services'] ?? []);
      services.insert(0, service);
      _businesses[idx]['services'] = services;
      await _persistBusinesses();
    }
  }

  // --- OFFERS WITH MAX STUDENT QUOTA ---
  static List<Map<String, dynamic>> getOffersForBusiness(String businessId) {
    return _offers.where((o) => o['business_id'] == businessId).toList();
  }

  static List<Map<String, dynamic>> getAllActiveOffers() {
    return List.unmodifiable(_offers);
  }

  static Future<void> createOffer({
    required String businessId,
    required String businessName,
    required String title,
    required String discountText,
    required String code,
    required int maxStudentsLimit, // e.g. first 10 students
  }) async {
    final newOffer = <String, dynamic>{
      'id': 'off-${DateTime.now().millisecondsSinceEpoch}',
      'business_id': businessId,
      'business_name': businessName,
      'title': title,
      'discount_text': discountText,
      'code': code,
      'max_claims': maxStudentsLimit,
      'claimed_count': 0,
      'claimed_emails': <String>[],
      'status': 'ACTIVE',
      'valid_until_text': 'Valid for first $maxStudentsLimit students',
    };
    _offers.insert(0, newOffer);
    await _persistOffers();
  }

  static Future<bool> claimOffer(String offerId, String studentEmail) async {
    final idx = _offers.indexWhere((o) => o['id'] == offerId);
    if (idx != -1) {
      final o = _offers[idx];
      final max = (o['max_claims'] as num?)?.toInt() ?? 10;
      final claimed = (o['claimed_count'] as num?)?.toInt() ?? 0;
      final emails = List<String>.from(o['claimed_emails'] ?? []);

      if (claimed >= max) {
        return false; // Quota full!
      }

      if (!emails.contains(studentEmail)) {
        emails.add(studentEmail);
        o['claimed_emails'] = emails;
        o['claimed_count'] = claimed + 1;
        if (claimed + 1 >= max) {
          o['status'] = 'EXPIRED';
        }
        await _persistOffers();
        return true;
      }
    }
    return true;
  }

  static void _seedDefaultBusinesses() {
    _businesses = [
      {
        'id': 'seed-1',
        'owner_email': 'owner@sharmamess.com',
        'name': 'Sharma Mess & Tiffin Service',
        'category_name': 'MESS',
        'monthly_fee': 1500,
        'address': 'Near MIT AOE Back Gate, Alandi, Pune',
        'phone': '+91 98234 56789',
        'whatsapp': '+91 98234 56789',
        'opening_hours_text': '08:00 AM - 10:30 PM',
        'price_level': '₹',
        'has_student_discount': true,
        'discount_details': '15% Off Monthly Mess Pass with MIT AOE ID',
        'description': 'Pure vegetarian hygienic daily unlimited mess and tiffin box delivery.',
        'google_maps_url': 'https://maps.google.com/?q=18.6757,73.8967',
        'status': 'VERIFIED',
        'rating': 4.6,
        'review_count': 42,
        'distance_meters': 350.0,
        'services': [
          {'name': 'Unlimited Student Thali', 'price': 90.0, 'description': '2 sabzi, 4 roti, dal, rice'},
          {'name': 'Monthly Mess Pass', 'price': 2400.0, 'description': 'Lunch + Dinner 30 days booklet'}
        ],
      },
      {
        'id': 'seed-2',
        'owner_email': 'owner@omhostel.com',
        'name': 'Om Sai Boys Hostel',
        'category_name': 'HOSTEL (BOYS SEPARATE)',
        'monthly_fee': 2000,
        'address': 'Opp. MIT AOE Gate 3, Alandi',
        'phone': '+91 98900 12345',
        'whatsapp': '+91 98900 12345',
        'opening_hours_text': '24 Hours',
        'price_level': '₹₹',
        'has_student_discount': true,
        'discount_details': '₹500 Off First Month Deposit',
        'description': 'Wi-Fi, 24/7 hot water, biometric security, furnished rooms for engineering students.',
        'google_maps_url': 'https://maps.google.com/?q=18.6760,73.8970',
        'status': 'VERIFIED',
        'rating': 4.7,
        'review_count': 28,
        'distance_meters': 180.0,
        'services': [
          {'name': 'Double Sharing Room', 'price': 3500.0, 'description': 'Per month with Wi-Fi & attached bath'},
          {'name': 'Triple Sharing Room', 'price': 2800.0, 'description': 'Per month with study desk & bed'}
        ],
      },
      {
        'id': 'seed-3',
        'owner_email': 'owner@xeroxhub.com',
        'name': 'Campus Xerox & Stationery Hub',
        'category_name': 'STATIONARY',
        'monthly_fee': 300,
        'address': 'Opposite Main Gate, Alandi',
        'phone': '+91 98221 44556',
        'whatsapp': '+91 98221 44556',
        'opening_hours_text': '08:30 AM - 10:00 PM',
        'price_level': '₹',
        'has_student_discount': true,
        'discount_details': 'Spiral binding ₹20 special rate',
        'description': 'Color prints, project book binding, drawing sheets, lab manuals and engineering stationery.',
        'google_maps_url': 'https://maps.google.com/?q=18.6752,73.8962',
        'status': 'VERIFIED',
        'rating': 4.8,
        'review_count': 35,
        'distance_meters': 120.0,
        'services': [
          {'name': 'B&W Photocopy / Print', 'price': 1.5, 'description': 'Per single side print'},
          {'name': 'Hardcover Project Binding', 'price': 150.0, 'description': 'Golden embossed standard project copy'}
        ],
      },
    ];

    _offers = [
      {
        'id': 'off-seed-1',
        'business_id': 'seed-1',
        'business_name': 'Sharma Mess & Tiffin Service',
        'title': 'First 10 Students Monthly Mess Deal',
        'discount_text': '₹300 OFF',
        'code': 'AASPAAS-MESS300',
        'max_claims': 10,
        'claimed_count': 3,
        'claimed_emails': ['demo1@mitaoe.ac.in', 'demo2@mitaoe.ac.in', 'demo3@mitaoe.ac.in'],
        'status': 'ACTIVE',
        'valid_until_text': 'Limited to first 10 students',
      },
      {
        'id': 'off-seed-2',
        'business_id': 'seed-2',
        'business_name': 'Om Sai Boys Hostel',
        'title': 'Early Booking Semester Discount',
        'discount_text': '₹500 OFF',
        'code': 'HOSTEL500',
        'max_claims': 15,
        'claimed_count': 5,
        'claimed_emails': [],
        'status': 'ACTIVE',
        'valid_until_text': 'Limited to first 15 students',
      },
    ];
  }
}
