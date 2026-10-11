class ServiceModel {
  final String id;
  final String name;
  final String? description;
  final double price;
  final String? priceFreshness;

  ServiceModel({
    required this.id,
    required this.name,
    this.description,
    required this.price,
    this.priceFreshness,
  });

  factory ServiceModel.fromJson(Map<String, dynamic> json) {
    return ServiceModel(
      id: json['id']?.toString() ?? '',
      name: json['name']?.toString() ?? 'Service',
      description: json['description']?.toString(),
      price: (json['price'] as num?)?.toDouble() ?? 0.0,
      priceFreshness: json['price_freshness']?.toString() ?? 'Updated recently',
    );
  }
}

class BusinessModel {
  final String id;
  final String name;
  final String? description;
  final String? phone;
  final String? whatsapp;
  final String address;
  final String categoryName;
  final String priceLevel;
  final double rating;
  final int reviewCount;
  final double? distanceMeters;
  final bool isOpenNow;
  final bool isVerified;
  final bool hasStudentDiscount;
  final String? discountDetails;
  final Map<String, double> dimensionRatings;
  final List<ServiceModel> services;
  final List<String> photos;
  final String? openingHours;

  BusinessModel({
    required this.id,
    required this.name,
    this.description,
    this.phone,
    this.whatsapp,
    required this.address,
    required this.categoryName,
    this.priceLevel = '₹₹',
    this.rating = 0.0,
    this.reviewCount = 0,
    this.distanceMeters,
    this.isOpenNow = true,
    this.isVerified = false,
    this.hasStudentDiscount = false,
    this.discountDetails,
    this.dimensionRatings = const {},
    this.services = const [],
    this.photos = const [],
    this.openingHours,
  });

  String get formattedDistance {
    if (distanceMeters == null) return 'Nearby';
    if (distanceMeters! < 1000) {
      return '${distanceMeters!.round()} m';
    }
    return '${(distanceMeters! / 1000).toStringAsFixed(1)} km';
  }

  factory BusinessModel.fromJson(Map<String, dynamic> json) {
    // Parse dimension ratings
    final rawDims = json['dimension_ratings'] as Map<String, dynamic>? ?? {};
    final dims = <String, double>{};
    rawDims.forEach((key, val) {
      dims[key] = (val as num).toDouble();
    });

    // Parse services
    final rawServices = json['services'] as List? ?? [];
    final services = rawServices.map((s) => ServiceModel.fromJson(s as Map<String, dynamic>)).toList();

    // Parse photos
    final rawPhotos = json['photos'] as List? ?? [];
    final photos = rawPhotos.map((p) => p is Map ? (p['url']?.toString() ?? '') : p.toString()).where((s) => s.isNotEmpty).toList();

    return BusinessModel(
      id: json['id']?.toString() ?? '',
      name: json['name']?.toString() ?? 'Unnamed Business',
      description: json['description']?.toString(),
      phone: json['phone']?.toString(),
      whatsapp: json['whatsapp']?.toString(),
      address: json['address']?.toString() ?? 'Alandi, Pune',
      categoryName: json['category_name']?.toString() ?? (json['category']?['name']?.toString() ?? 'General'),
      priceLevel: json['price_level']?.toString() ?? '₹₹',
      rating: (json['average_rating'] as num?)?.toDouble() ?? (json['rating'] as num?)?.toDouble() ?? 4.2,
      reviewCount: (json['review_count'] as num?)?.toInt() ?? 0,
      distanceMeters: (json['distance_meters'] as num?)?.toDouble(),
      isOpenNow: json['is_open_now'] as bool? ?? true,
      isVerified: json['verification_status'] == 'VERIFIED' || json['is_verified'] == true,
      hasStudentDiscount: json['student_discount'] as bool? ?? (json['has_offers'] as bool? ?? false),
      discountDetails: json['discount_details']?.toString(),
      dimensionRatings: dims,
      services: services,
      photos: photos,
      openingHours: json['opening_hours_text']?.toString() ?? '10:00 AM - 10:00 PM',
    );
  }
}
