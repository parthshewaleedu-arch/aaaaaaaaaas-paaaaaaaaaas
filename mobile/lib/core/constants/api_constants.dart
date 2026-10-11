class ApiConstants {
  // Default base URL for Android emulator connecting to host backend
  // For physical devices or cloud, update this or change via Profile > Server URL
  static const String defaultBaseUrl = 'http://10.0.2.2:8000/api/v1';

  // Fallback production or local network URL
  static const String localNetworkUrl = 'http://192.168.1.100:8000/api/v1';

  // Pilot campus constants
  static const String defaultCampusName = 'MIT Academy of Engineering (MIT AOE)';
  static const String defaultCampusCity = 'Alandi, Pune';
  static const double defaultCampusLat = 18.6757;
  static const double defaultCampusLng = 73.8967;
  static const double defaultRadiusKm = 3.0;

  // Endpoint paths
  static const String authLogin = '/auth/token';
  static const String authRefresh = '/auth/refresh-token';
  static const String authLogout = '/auth/logout';
  static const String campuses = '/campuses';
  static const String categories = '/categories';
  static const String businesses = '/businesses';
  static const String reviews = '/reviews';
  static const String offers = '/offers';
  static const String studentsMe = '/students/me/profile';
  static const String studentFavorites = '/students/favorites';
}
