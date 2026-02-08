import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:hacknation_app/services/search_products.dart';

const String baseUrl = 'http://172.22.13.251:8000';

/// Datenmodell für Shopping Plan Component
class ShoppingPlanComponent {
  final String id;
  final String name;
  final String category;
  final double budgetMin;
  final double budgetMax;
  final String priority;
  final int quantity;
  final List<String> notes;

  ShoppingPlanComponent({
    required this.id,
    required this.name,
    required this.category,
    required this.budgetMin,
    required this.budgetMax,
    this.priority = 'must_have',
    this.quantity = 1,
    this.notes = const [],
  });

  factory ShoppingPlanComponent.fromJson(Map<String, dynamic> json) {
    return ShoppingPlanComponent(
      id: json['id'] as String,
      name: json['name'] as String,
      category: json['category'] as String,
      budgetMin: (json['budget_min'] as num).toDouble(),
      budgetMax: (json['budget_max'] as num).toDouble(),
      priority: json['priority'] as String? ?? 'must_have',
      quantity: json['quantity'] as int? ?? 1,
      notes: (json['notes'] as List?)?.map((e) => e as String).toList() ?? [],
    );
  }
}

/// Datenmodell für Shopping Plan
class ShoppingPlan {
  final String currency;
  final double totalBudgetMin;
  final double totalBudgetMax;
  final List<ShoppingPlanComponent> components;

  ShoppingPlan({
    this.currency = 'EUR',
    required this.totalBudgetMin,
    required this.totalBudgetMax,
    required this.components,
  });

  factory ShoppingPlan.fromJson(Map<String, dynamic> json) {
    return ShoppingPlan(
      currency: json['currency'] as String? ?? 'EUR',
      totalBudgetMin: (json['total_budget_min'] as num).toDouble(),
      totalBudgetMax: (json['total_budget_max'] as num).toDouble(),
      components: (json['components'] as List)
          .map((c) => ShoppingPlanComponent.fromJson(c))
          .toList(),
    );
  }
}

/// Google Shopping Ergebnis (Rohdaten von der API)
class GoogleShoppingResult {
  final String title;
  final String? link;
  final String? price;
  final String? source;
  final String? thumbnail;
  final Map<String, dynamic> raw;

  GoogleShoppingResult({
    required this.title,
    this.link,
    this.price,
    this.source,
    this.thumbnail,
    required this.raw,
  });

  factory GoogleShoppingResult.fromJson(Map<String, dynamic> json) {
    return GoogleShoppingResult(
      title: json['title'] as String? ?? '',
      link: json['link'] as String?,
      price: json['price'] as String?,
      source: json['source'] as String?,
      thumbnail: json['thumbnail'] as String?,
      raw: json,
    );
  }
}

/// Plan Komponente mit Google Shopping Ergebnissen
class PlanComponentSearch {
  final ShoppingPlanComponent component;
  final List<GoogleShoppingResult> shoppingResults;

  PlanComponentSearch({required this.component, required this.shoppingResults});

  factory PlanComponentSearch.fromJson(Map<String, dynamic> json) {
    return PlanComponentSearch(
      component: ShoppingPlanComponent.fromJson(json['component']),
      shoppingResults: (json['shopping_results'] as List)
          .map((r) => GoogleShoppingResult.fromJson(r))
          .toList(),
    );
  }
}

/// Ruft die Shopping Plan API auf
Future<ShoppingPlan> createShoppingPlan({required String sessionId}) async {
  final url = Uri.parse('$baseUrl/sessions/$sessionId/shopping-plan');

  final response = await http.post(
    url,
    headers: {'Content-Type': 'application/json'},
  );

  if (response.statusCode == 200) {
    final data = jsonDecode(response.body);
    return ShoppingPlan.fromJson(data);
  } else {
    throw Exception(
      'Shopping Plan konnte nicht erstellt werden: ${response.statusCode} - ${response.body}',
    );
  }
}

/// Ruft die Google Shopping API für den Shopping Plan auf
/// Gibt für jede Komponente die ersten 3 Google Shopping Treffer zurück
Future<List<PlanComponentSearch>> createShoppingPlanWithGoogleShopping({
  required String sessionId,
}) async {
  final url = Uri.parse(
    '$baseUrl/sessions/$sessionId/shopping-plan/google-shopping',
  );

  final response = await http.post(
    url,
    headers: {'Content-Type': 'application/json'},
  );

  if (response.statusCode == 200) {
    final data = jsonDecode(response.body) as List;
    return data.map((item) => PlanComponentSearch.fromJson(item)).toList();
  } else {
    throw Exception(
      'Google Shopping Suche konnte nicht durchgeführt werden: ${response.statusCode} - ${response.body}',
    );
  }
}

/// Hilfsfunktion: Preis-String aus Google Shopping in double konvertieren
/// Beispiele: "$25.99" -> 25.99, "25,99 €" -> 25.99, "1.299,00 EUR" -> 1299.00
double _parsePrice(String? priceString) {
  if (priceString == null || priceString.isEmpty) return 0.0;

  // Entferne alle Nicht-Ziffern außer Komma und Punkt
  String cleaned = priceString.replaceAll(RegExp(r'[^\d,.]'), '');

  // Europäisches Format: 1.299,99 -> 1299.99
  if (cleaned.contains(',') && cleaned.contains('.')) {
    cleaned = cleaned.replaceAll('.', '').replaceAll(',', '.');
  }
  // Nur Komma: 25,99 -> 25.99
  else if (cleaned.contains(',')) {
    cleaned = cleaned.replaceAll(',', '.');
  }

  return double.tryParse(cleaned) ?? 0.0;
}

/// Konvertiert Google Shopping Ergebnisse in RankedProduct-Objekte für die Anzeige
List<RankedProduct> convertGoogleShoppingToRankedProducts(
  List<PlanComponentSearch> searchResults,
) {
  final List<RankedProduct> products = [];

  for (var componentResult in searchResults) {
    final component = componentResult.component;

    for (var (index, result) in componentResult.shoppingResults.indexed) {
      // Score basierend auf Position (1. = beste, absteigend)
      final score = 1.0 - (index * 0.1);

      products.add(
        RankedProduct(
          retailerId: result.source ?? 'google_shopping',
          productId: '${component.id}_$index',
          title: result.title,
          price: _parsePrice(result.price),
          currency: 'EUR',
          deliveryEstimateDays: null,
          imageUrl: result.thumbnail,
          productUrl: result.link,
          score: score,
          scoreBreakdown: {'position': score, 'component': component.name},
          explanation:
              'Gefunden für: ${component.name} (${component.category})',
        ),
      );
    }
  }

  return products;
}
