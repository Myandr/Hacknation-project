import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:hacknation_app/services/create_session.dart' show baseUrl;

/// Holt Produkte zur Session (GET /sessions/{sessionId}/search/products).
/// Fallback, wenn die Chat-Response keine products enthielt.
Future<List<Map<String, dynamic>>> getProducts(String sessionId, {int limit = 10, int offset = 0}) async {
  final url = Uri.parse('$baseUrl/sessions/$sessionId/search/products?limit=$limit&offset=$offset');
  final response = await http.get(url);
  if (response.statusCode != 200) return [];
  final data = jsonDecode(response.body) as Map<String, dynamic>?;
  final list = data?['products'] as List<dynamic>? ?? [];
  return list.whereType<Map<String, dynamic>>().toList();
}
