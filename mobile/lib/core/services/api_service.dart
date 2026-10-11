import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import '../constants/api_constants.dart';
import 'storage_service.dart';

class ApiResponse<T> {
  final bool success;
  final T? data;
  final String? error;

  ApiResponse({required this.success, this.data, this.error});
}

class ApiService {
  static String get _baseUrl => StorageService.getBaseUrl();

  static Map<String, String> _headers({bool requiresAuth = true}) {
    final headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };
    if (requiresAuth) {
      final token = StorageService.getAccessToken();
      if (token != null) {
        headers['Authorization'] = 'Bearer $token';
      }
    }
    return headers;
  }

  // --- AUTHENTICATION ---

  static Future<ApiResponse<Map<String, dynamic>>> login({
    required String email,
    required String password,
  }) async {
    try {
      final url = Uri.parse('$_baseUrl${ApiConstants.authLogin}');
      // FastApi OAuth2PasswordRequestForm expects form-urlencoded
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: {'username': email, 'password': password},
      ).timeout(const Duration(seconds: 15));

      final data = jsonDecode(response.body);
      if (response.statusCode == 200) {
        final accessToken = data['access_token'] as String;
        final refreshToken = data['refresh_token'] as String;
        await StorageService.saveTokens(
          accessToken: accessToken,
          refreshToken: refreshToken,
        );
        return ApiResponse(success: true, data: data);
      } else {
        return ApiResponse(
          success: false,
          error: data['detail'] ?? 'Login failed. Please check your credentials.',
        );
      }
    } catch (e) {
      return ApiResponse(success: false, error: 'Connection error: $e');
    }
  }

  static Future<void> logout() async {
    try {
      final refreshToken = StorageService.getRefreshToken();
      final url = Uri.parse('$_baseUrl${ApiConstants.authLogout}');
      await http.post(
        url,
        headers: _headers(),
        body: jsonEncode({'refresh_token': refreshToken}),
      ).timeout(const Duration(seconds: 5));
    } catch (_) {}
    await StorageService.clearSession();
  }

  // --- CAMPUSES ---

  static Future<ApiResponse<List<dynamic>>> getCampuses() async {
    try {
      final url = Uri.parse('$_baseUrl${ApiConstants.campuses}?limit=50');
      final response = await http.get(url, headers: _headers(requiresAuth: false));
      if (response.statusCode == 200) {
        final body = jsonDecode(response.body);
        final list = (body['items'] as List?) ?? [];
        return ApiResponse(success: true, data: list);
      }
      return ApiResponse(success: false, error: 'Failed to load campuses');
    } catch (e) {
      return ApiResponse(success: false, error: e.toString());
    }
  }

  // --- CATEGORIES ---

  static Future<ApiResponse<List<dynamic>>> getCategories() async {
    try {
      final url = Uri.parse('$_baseUrl${ApiConstants.categories}?is_active=true&root_only=true');
      final response = await http.get(url, headers: _headers(requiresAuth: false));
      if (response.statusCode == 200) {
        final list = jsonDecode(response.body) as List;
        return ApiResponse(success: true, data: list);
      }
      return ApiResponse(success: false, error: 'Failed to load categories');
    } catch (e) {
      return ApiResponse(success: false, error: e.toString());
    }
  }

  // --- BUSINESSES ---

  static Future<ApiResponse<Map<String, dynamic>>> getBusinesses({
    String? search,
    String? campusId,
    String? categoryId,
    double? minRating,
    String? priceLevel,
    bool? studentDiscount,
    bool? openNow,
    String sort = 'newest',
    int page = 1,
    int pageSize = 20,
  }) async {
    try {
      final queryParams = <String, String>{
        'page': page.toString(),
        'page_size': pageSize.toString(),
        'sort': sort,
      };

      if (search != null && search.trim().isNotEmpty) queryParams['search'] = search.trim();
      if (campusId != null) queryParams['campus_id'] = campusId;
      if (categoryId != null) queryParams['category_id'] = categoryId;
      if (minRating != null) queryParams['min_rating'] = minRating.toString();
      if (priceLevel != null) queryParams['price_level'] = priceLevel;
      if (studentDiscount != null && studentDiscount) queryParams['student_discount'] = 'true';
      if (openNow != null && openNow) queryParams['open_now'] = 'true';

      final uri = Uri.parse('$_baseUrl${ApiConstants.businesses}').replace(queryParameters: queryParams);
      final response = await http.get(uri, headers: _headers(requiresAuth: false));

      if (response.statusCode == 200) {
        final body = jsonDecode(response.body) as Map<String, dynamic>;
        return ApiResponse(success: true, data: body);
      }
      return ApiResponse(success: false, error: 'Failed to load businesses');
    } catch (e) {
      return ApiResponse(success: false, error: e.toString());
    }
  }

  static Future<ApiResponse<Map<String, dynamic>>> getBusinessDetail(String businessId) async {
    try {
      final url = Uri.parse('$_baseUrl${ApiConstants.businesses}/$businessId');
      final response = await http.get(url, headers: _headers(requiresAuth: false));
      if (response.statusCode == 200) {
        return ApiResponse(success: true, data: jsonDecode(response.body));
      }
      return ApiResponse(success: false, error: 'Business not found');
    } catch (e) {
      return ApiResponse(success: false, error: e.toString());
    }
  }

  // --- REVIEWS ---

  static Future<ApiResponse<Map<String, dynamic>>> submitReview({
    required String businessId,
    required double rating,
    required String comment,
    Map<String, double>? dimensionRatings,
  }) async {
    try {
      final url = Uri.parse('$_baseUrl${ApiConstants.businesses}/$businessId/reviews');
      final payload = {
        'rating': rating,
        'comment': comment,
        'dimensions': dimensionRatings ?? {},
      };
      final response = await http.post(
        url,
        headers: _headers(),
        body: jsonEncode(payload),
      );
      if (response.statusCode == 200 || response.statusCode == 201) {
        return ApiResponse(success: true, data: jsonDecode(response.body));
      }
      final err = jsonDecode(response.body);
      return ApiResponse(success: false, error: err['detail'] ?? 'Could not submit review');
    } catch (e) {
      return ApiResponse(success: false, error: e.toString());
    }
  }

  // --- OFFERS ---

  static Future<ApiResponse<List<dynamic>>> getOffers({String? campusId, String? categoryId}) async {
    try {
      final queryParams = <String, String>{'status': 'ACTIVE'};
      if (campusId != null) queryParams['campus_id'] = campusId;
      if (categoryId != null) queryParams['category_id'] = categoryId;

      final uri = Uri.parse('$_baseUrl${ApiConstants.offers}').replace(queryParameters: queryParams);
      final response = await http.get(uri, headers: _headers(requiresAuth: false));
      if (response.statusCode == 200) {
        final body = jsonDecode(response.body);
        final list = (body['items'] as List?) ?? [];
        return ApiResponse(success: true, data: list);
      }
      return ApiResponse(success: false, error: 'Failed to load offers');
    } catch (e) {
      return ApiResponse(success: false, error: e.toString());
    }
  }

  static Future<ApiResponse<Map<String, dynamic>>> claimOffer(String offerId) async {
    try {
      final url = Uri.parse('$_baseUrl${ApiConstants.offers}/$offerId/claim');
      final response = await http.post(url, headers: _headers());
      if (response.statusCode == 200 || response.statusCode == 201) {
        return ApiResponse(success: true, data: jsonDecode(response.body));
      }
      final err = jsonDecode(response.body);
      return ApiResponse(success: false, error: err['detail'] ?? 'Could not claim offer');
    } catch (e) {
      return ApiResponse(success: false, error: e.toString());
    }
  }

  // --- FAVORITES ---

  static Future<ApiResponse<bool>> toggleFavorite(String businessId) async {
    try {
      final url = Uri.parse('$_baseUrl${ApiConstants.businesses}/$businessId/favorite');
      final response = await http.post(url, headers: _headers());
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return ApiResponse(success: true, data: data['is_favorited'] ?? true);
      }
      // Local fallback toggle
      final local = await StorageService.toggleSavedBusiness(businessId);
      return ApiResponse(success: true, data: local);
    } catch (_) {
      final local = await StorageService.toggleSavedBusiness(businessId);
      return ApiResponse(success: true, data: local);
    }
  }

  // --- STUDENT PROFILE ---

  static Future<ApiResponse<Map<String, dynamic>>> getStudentProfile() async {
    try {
      final url = Uri.parse('$_baseUrl${ApiConstants.studentsMe}');
      final response = await http.get(url, headers: _headers());
      if (response.statusCode == 200) {
        return ApiResponse(success: true, data: jsonDecode(response.body));
      }
      return ApiResponse(success: false, error: 'Failed to fetch student profile');
    } catch (e) {
      return ApiResponse(success: false, error: e.toString());
    }
  }
}
