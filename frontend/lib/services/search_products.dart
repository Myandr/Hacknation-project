import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:hacknation_app/services/create_session.dart' show baseUrl;

/// Ein geranktes Produkt aus der Suche.
class RankedProduct {
  final String retailerId;
  final String productId;
  final String title;
  final double price;
  final String currency;
  final int? deliveryEstimateDays;
  final String? imageUrl;
  final String? productUrl;
  final double score;
  final Map<String, dynamic> scoreBreakdown;
  final String explanation;

  RankedProduct({
    required this.retailerId,
    required this.productId,
    required this.title,
    required this.price,
    required this.currency,
    this.deliveryEstimateDays,
    this.imageUrl,
    this.productUrl,
    required this.score,
    required this.scoreBreakdown,
    required this.explanation,
  });

  factory RankedProduct.fromJson(Map<String, dynamic> json) {
    return RankedProduct(
      retailerId: json['retailer_id'] as String,
      productId: json['product_id'] as String,
      title: json['title'] as String,
      price: (json['price'] as num).toDouble(),
      currency: (json['currency'] as String?) ?? 'EUR',
      deliveryEstimateDays: json['delivery_estimate_days'] as int?,
      imageUrl: json['image_url'] as String?,
      productUrl: json['product_url'] as String?,
      score: (json['score'] as num).toDouble(),
      scoreBreakdown: (json['score_breakdown'] as Map<String, dynamic>?) ?? {},
      explanation: (json['explanation'] as String?) ?? '',
    );
  }
}

/// Ergebnis der Multi-Retailer-Suche.
class SearchResult {
  final List<RankedProduct> products;
  final String rankingExplanation;
  final String whyFirst;

  SearchResult({
    required this.products,
    required this.rankingExplanation,
    required this.whyFirst,
  });

  factory SearchResult.fromJson(Map<String, dynamic> json) {
    final productsList = (json['products'] as List<dynamic>)
        .map((p) => RankedProduct.fromJson(p as Map<String, dynamic>))
        .toList();

    return SearchResult(
      products: productsList,
      rankingExplanation: (json['ranking_explanation'] as String?) ?? '',
      whyFirst: (json['why_first'] as String?) ?? '',
    );
  }
}

/// Ruft die Suche auf: POST /sessions/{sessionId}/search.
/// Wird erst aufgerufen, wenn der Session-Status "ready_for_search" ist.
Future<SearchResult> searchProducts({required String sessionId}) async {
  final url = Uri.parse('$baseUrl/sessions/$sessionId/search');

  final response = await http.post(
    url,
    headers: {'Content-Type': 'application/json'},
  );

  if (response.statusCode == 200) {
    final data = jsonDecode(response.body) as Map<String, dynamic>;
    return SearchResult.fromJson(data);
  } else {
    throw Exception(
      'Suche fehlgeschlagen (${response.statusCode}): ${response.body}',
    );
  }
}
