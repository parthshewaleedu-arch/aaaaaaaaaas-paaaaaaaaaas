class OfferModel {
  final String id;
  final String title;
  final String? description;
  final String businessId;
  final String businessName;
  final String discountText;
  final String? code;
  final String validUntil;
  final bool isClaimed;

  OfferModel({
    required this.id,
    required this.title,
    this.description,
    required this.businessId,
    required this.businessName,
    required this.discountText,
    this.code,
    this.validUntil = 'Limited Time',
    this.isClaimed = false,
  });

  factory OfferModel.fromJson(Map<String, dynamic> json) {
    return OfferModel(
      id: json['id']?.toString() ?? '',
      title: json['title']?.toString() ?? 'Special Student Deal',
      description: json['description']?.toString(),
      businessId: json['business_id']?.toString() ?? '',
      businessName: json['business_name']?.toString() ?? (json['business']?['name']?.toString() ?? 'Campus Business'),
      discountText: json['discount_text']?.toString() ?? (json['discount_percentage'] != null ? '${json['discount_percentage']}% OFF' : 'Student Deal'),
      code: json['code']?.toString() ?? 'CAMPUSPASS',
      validUntil: json['valid_until_text']?.toString() ?? 'Valid this term',
      isClaimed: json['is_claimed'] as bool? ?? false,
    );
  }
}
