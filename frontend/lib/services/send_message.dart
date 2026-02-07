import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:hacknation_app/services/create_session.dart' show baseUrl;

/// Antwort-Modell für den Chat-Endpoint.
class ChatResponse {
  final String sessionId;
  final String reply;
  final String status;
  final Map<String, dynamic> requirements;
  /// Bei status == 'ready_for_search': bis zu 10 Produkte aus der API.
  final List<Map<String, dynamic>> products;

  ChatResponse({
    required this.sessionId,
    required this.reply,
    required this.status,
    required this.requirements,
    this.products = const [],
  });

  factory ChatResponse.fromJson(Map<String, dynamic> json) {
    final productsRaw = json['products'];
    List<Map<String, dynamic>> products = [];
    if (productsRaw is List) {
      for (final e in productsRaw) {
        if (e is Map<String, dynamic>) products.add(e);
      }
    }
    return ChatResponse(
      sessionId: json['session_id'] as String,
      reply: json['reply'] as String,
      status: json['status'] as String,
      requirements: json['requirements'] as Map<String, dynamic>? ?? {},
      products: products,
    );
  }
}

/// Sendet eine Nachricht an die KI über POST /sessions/{sessionId}/chat.
/// Gibt eine [ChatResponse] mit der Antwort zurück.
Future<ChatResponse> sendMessage({
  required String sessionId,
  required String message,
}) async {
  final url = Uri.parse('$baseUrl/sessions/$sessionId/chat');

  final response = await http.post(
    url,
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode({'message': message}),
  );

  if (response.statusCode == 200) {
    final data = jsonDecode(response.body) as Map<String, dynamic>;
    return ChatResponse.fromJson(data);
  } else {
    throw Exception(
      'Nachricht konnte nicht gesendet werden (${response.statusCode}): ${response.body}',
    );
  }
}
