class CategoryModel {
  final String id;
  final String name;
  final String slug;
  final String? icon;
  final int businessCount;

  CategoryModel({
    required this.id,
    required this.name,
    required this.slug,
    this.icon,
    this.businessCount = 0,
  });

  factory CategoryModel.fromJson(Map<String, dynamic> json) {
    return CategoryModel(
      id: json['id']?.toString() ?? '',
      name: json['name']?.toString() ?? 'Category',
      slug: json['slug']?.toString() ?? '',
      icon: json['icon']?.toString(),
      businessCount: (json['business_count'] as num?)?.toInt() ?? 0,
    );
  }
}
