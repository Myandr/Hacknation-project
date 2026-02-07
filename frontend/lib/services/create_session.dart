import 'dart:convert';
import 'package:http/http.dart' as http;

/// Basis-URL des Backends.
/// Für Android-Emulator: 'http://10.0.2.2:8000'
/// Für iOS-Simulator / Web: 'http://127.0.0.1:8000'
const String baseUrl = 'http://172.22.13.251:8000';

/// Erstellt eine neue Session über POST /sessions.
/// Gibt die session_id als String zurück oder wirft einen Fehler.
Future<String> createSession() async {
  final url = Uri.parse('$baseUrl/sessions');

  final response = await http.post(
    url,
    headers: {'Content-Type': 'application/json'},
  );

  if (response.statusCode == 200) {
    final data = jsonDecode(response.body);
    final sessionId = data['session_id'] as String;
    return sessionId;
  } else {
    throw Exception(
      'Session konnte nicht erstellt werden (${response.statusCode}): ${response.body}',
    );
  }
}
