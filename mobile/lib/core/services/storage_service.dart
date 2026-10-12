import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../constants/api_constants.dart';

import 'app_repository.dart';

class StorageService {
  static const String _keyAccessToken = 'access_token';
  static const String _keyRefreshToken = 'refresh_token';
  static const String _keyUser = 'user_data';
  static const String _keyUserRole = 'user_role'; // STUDENT, OWNER, ADMIN
  static const String _keyIsLoggedIn = 'is_logged_in';
  static const String _keyCampusId = 'selected_campus_id';
  static const String _keyCampusName = 'selected_campus_name';
  static const String _keyBaseUrl = 'custom_base_url';
  static const String _keySavedBusinesses = 'saved_business_ids';

  static SharedPreferences? _prefs;

  static Future<void> init() async {
    _prefs ??= await SharedPreferences.getInstance();
    await AppRepository.init();
  }

  static String getCurrentUserEmail() {
    final user = getUser();
    return user?['email']?.toString() ?? '';
  }

  // Tokens
  static Future<void> saveTokens({
    required String accessToken,
    required String refreshToken,
  }) async {
    await init();
    await _prefs?.setString(_keyAccessToken, accessToken);
    await _prefs?.setString(_keyRefreshToken, refreshToken);
  }

  static String? getAccessToken() {
    return _prefs?.getString(_keyAccessToken);
  }

  static String? getRefreshToken() {
    return _prefs?.getString(_keyRefreshToken);
  }

  // Session & Role Persistence
  static bool hasValidSession() {
    return _prefs?.getBool(_keyIsLoggedIn) == true;
  }

  static Future<void> setSession({
    required String role,
    required Map<String, dynamic> user,
    String? accessToken,
    String? refreshToken,
  }) async {
    await init();
    await _prefs?.setBool(_keyIsLoggedIn, true);
    await _prefs?.setString(_keyUserRole, role.toUpperCase());
    await _prefs?.setString(_keyUser, jsonEncode(user));
    if (accessToken != null) {
      await _prefs?.setString(_keyAccessToken, accessToken);
    }
    if (refreshToken != null) {
      await _prefs?.setString(_keyRefreshToken, refreshToken);
    }
  }

  static String getUserRole() {
    return _prefs?.getString(_keyUserRole) ?? 'STUDENT';
  }

  static Future<void> setUserRole(String role) async {
    await init();
    await _prefs?.setString(_keyUserRole, role.toUpperCase());
  }

  static Future<void> clearSession() async {
    await init();
    await _prefs?.remove(_keyAccessToken);
    await _prefs?.remove(_keyRefreshToken);
    await _prefs?.remove(_keyUser);
    await _prefs?.remove(_keyUserRole);
    await _prefs?.setBool(_keyIsLoggedIn, false);
  }

  // Base URL
  static String getBaseUrl() {
    return _prefs?.getString(_keyBaseUrl) ?? ApiConstants.defaultBaseUrl;
  }

  static Future<void> setBaseUrl(String url) async {
    await init();
    await _prefs?.setString(_keyBaseUrl, url);
  }

  // Campus context
  static String getCampusName() {
    return _prefs?.getString(_keyCampusName) ?? ApiConstants.defaultCampusName;
  }

  static String? getCampusId() {
    return _prefs?.getString(_keyCampusId);
  }

  static Future<void> setCampus({required String id, required String name}) async {
    await init();
    await _prefs?.setString(_keyCampusId, id);
    await _prefs?.setString(_keyCampusName, name);
  }

  // User details
  static Future<void> saveUser(Map<String, dynamic> user) async {
    await init();
    await _prefs?.setString(_keyUser, jsonEncode(user));
  }

  static Map<String, dynamic>? getUser() {
    final raw = _prefs?.getString(_keyUser);
    if (raw == null) return null;
    try {
      return jsonDecode(raw) as Map<String, dynamic>;
    } catch (_) {
      return null;
    }
  }

  // Favorites / Saved businesses
  static List<String> getSavedBusinessIds() {
    return _prefs?.getStringList(_keySavedBusinesses) ?? [];
  }

  static Future<bool> toggleSavedBusiness(String businessId) async {
    await init();
    final list = getSavedBusinessIds();
    bool isSavedNow;
    if (list.contains(businessId)) {
      list.remove(businessId);
      isSavedNow = false;
    } else {
      list.add(businessId);
      isSavedNow = true;
    }
    await _prefs?.setStringList(_keySavedBusinesses, list);
    return isSavedNow;
  }

  static bool isBusinessSaved(String businessId) {
    final list = getSavedBusinessIds();
    return list.contains(businessId);
  }
}
