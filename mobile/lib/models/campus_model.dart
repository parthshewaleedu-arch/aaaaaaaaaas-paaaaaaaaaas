class CampusModel {
  final String id;
  final String name;
  final String? code;
  final String? city;
  final double latitude;
  final double longitude;
  final double radiusKm;
  final int activeBusinessesCount;

  CampusModel({
    required this.id,
    required this.name,
    this.code,
    this.city,
    required this.latitude,
    required this.longitude,
    this.radiusKm = 3.0,
    this.activeBusinessesCount = 0,
  });

  factory CampusModel.fromJson(Map<String, dynamic> json) {
    return CampusModel(
      id: json['id']?.toString() ?? '',
      name: json['name']?.toString() ?? 'Unknown Campus',
      code: json['code']?.toString(),
      city: json['city']?.toString() ?? 'Pune',
      latitude: (json['latitude'] as num?)?.toDouble() ?? 18.6757,
      longitude: (json['longitude'] as num?)?.toDouble() ?? 73.8967,
      radiusKm: (json['radius_km'] as num?)?.toDouble() ?? 3.0,
      activeBusinessesCount: (json['active_businesses_count'] as num?)?.toInt() ?? 0,
    );
  }
}
