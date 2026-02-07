import 'dart:convert';

import 'package:http/http.dart' as http;

import '../models/product_item.dart';

/// Basis-URL des Backends. Android-Emulator: http://10.0.2.2:8000
const String baseUrl = 'http://127.0.0.1:8000';

class ApiService {
  /// Neue Session erstellen, gibt session_id zurück.
  static Future<String?> createSession() async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/sessions'),
        headers: {'Content-Type': 'application/json'},
      );
      if (response.statusCode != 200) return null;
      final data = jsonDecode(response.body) as Map<String, dynamic>;
      return data['session_id'] as String?;
    } catch (_) {
      return null;
    }
  }

  /// Nachricht senden. Gibt reply, status und ggf. products zurück.
  static Future<ChatResponse?> sendMessage(String sessionId, String message) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/sessions/$sessionId/chat'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'message': message}),
      );
      if (response.statusCode != 200) return null;
      final data = jsonDecode(response.body) as Map<String, dynamic>;
      final productsList = data['products'] as List<dynamic>? ?? [];
      final products = productsList
          .map((e) => ProductItem.fromJson(e as Map<String, dynamic>))
          .toList();
      return ChatResponse(
        reply: data['reply'] as String? ?? '',
        status: data['status'] as String? ?? 'gathering_info',
        products: products,
      );
    } catch (_) {
      return null;
    }
  }

  /// Produkte nachladen (Fallback, wenn Chat-Response keine products hatte).
  static Future<List<ProductItem>> fetchProducts(String sessionId, {int limit = 10, int offset = 0}) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/sessions/$sessionId/search/products?limit=$limit&offset=$offset'),
      );
      if (response.statusCode != 200) return [];
      final data = jsonDecode(response.body) as Map<String, dynamic>;
      final list = data['products'] as List<dynamic>? ?? [];
      return list.map((e) => ProductItem.fromJson(e as Map<String, dynamic>)).toList();
    } catch (_) {
      return [];
    }
  }
}

class ChatResponse {
  final String reply;
  final String status;
  final List<ProductItem> products;

  ChatResponse({required this.reply, required this.status, required this.products});
}
