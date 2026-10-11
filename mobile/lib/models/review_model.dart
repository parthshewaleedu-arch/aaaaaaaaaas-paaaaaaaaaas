class ReviewModel {
  final String id;
  final String authorName;
  final bool isVerifiedStudent;
  final double rating;
  final Map<String, double> dimensionRatings;
  final String comment;
  final String timeAgo;
  final int helpfulCount;

  ReviewModel({
    required this.id,
    required this.authorName,
    this.isVerifiedStudent = true,
    required this.rating,
    this.dimensionRatings = const {},
    required this.comment,
    this.timeAgo = 'Recently',
    this.helpfulCount = 0,
  });

  factory ReviewModel.fromJson(Map<String, dynamic> json) {
    final rawDims = json['dimensions'] as Map<String, dynamic>? ?? {};
    final dims = <String, double>{};
    rawDims.forEach((k, v) {
      dims[k] = (v as num).toDouble();
    });

    return ReviewModel(
      id: json['id']?.toString() ?? '',
      authorName: json['student_name']?.toString() ?? (json['user']?['name']?.toString() ?? 'Verified Student'),
      isVerifiedStudent: json['is_student_verified'] as bool? ?? true,
      rating: (json['rating'] as num?)?.toDouble() ?? 5.0,
      dimensionRatings: dims,
      comment: json['comment']?.toString() ?? json['text']?.toString() ?? '',
      timeAgo: json['created_at_text']?.toString() ?? '2 days ago',
      helpfulCount: (json['helpful_count'] as num?)?.toInt() ?? 0,
    );
  }
}
