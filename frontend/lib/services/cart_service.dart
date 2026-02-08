import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:hacknation_app/services/create_session.dart' show baseUrl;
import 'package:hacknation_app/services/search_products.dart'
    show RankedProduct;

/// Ein Item im Warenkorb.
class CartItem {
  final int id;
  final String retailerId;
  final String productId;
  final String title;
  final double price;
  final String currency;
  final int? deliveryEstimateDays;
  final int quantity;
  final String? imageUrl;
  final String? productUrl;

  CartItem({
    required this.id,
    required this.retailerId,
    required this.productId,
    required this.title,
    required this.price,
    required this.currency,
    this.deliveryEstimateDays,
    required this.quantity,
    this.imageUrl,
    this.productUrl,
  });

  factory CartItem.fromJson(Map<String, dynamic> json) {
    return CartItem(
      id: json['id'] as int,
      retailerId: json['retailer_id'] as String,
      productId: json['product_id'] as String,
      title: json['title'] as String,
      price: (json['price'] as num).toDouble(),
      currency: (json['currency'] as String?) ?? 'EUR',
      deliveryEstimateDays: json['delivery_estimate_days'] as int?,
      quantity: (json['quantity'] as int?) ?? 1,
      imageUrl: json['image_url'] as String?,
      productUrl: json['product_url'] as String?,
    );
  }
}

/// Zusammenfassung des Warenkorbs.
class CartSummary {
  final List<CartItem> items;
  final double totalPrice;
  final String currency;
  final Map<String, double> byRetailer;
  final String deliverySummary;

  CartSummary({
    required this.items,
    required this.totalPrice,
    required this.currency,
    required this.byRetailer,
    required this.deliverySummary,
  });

  factory CartSummary.fromJson(Map<String, dynamic> json) {
    final items = (json['items'] as List<dynamic>)
        .map((i) => CartItem.fromJson(i as Map<String, dynamic>))
        .toList();
    final byRetailer =
        (json['by_retailer'] as Map<String, dynamic>?)?.map(
          (k, v) => MapEntry(k, (v as num).toDouble()),
        ) ??
        {};
    return CartSummary(
      items: items,
      totalPrice: (json['total_price'] as num).toDouble(),
      currency: (json['currency'] as String?) ?? 'EUR',
      byRetailer: byRetailer,
      deliverySummary: (json['delivery_summary'] as String?) ?? '',
    );
  }
}

/// Produkt in den Warenkorb legen: POST /sessions/{sessionId}/cart/items
/// Akzeptiert ein [RankedProduct] aus den Suchergebnissen.
Future<void> addToCart({
  required String sessionId,
  required RankedProduct product,
  int quantity = 1,
}) async {
  final url = Uri.parse('$baseUrl/sessions/$sessionId/cart/items');

  final response = await http.post(
    url,
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode({
      'retailer_id': product.retailerId,
      'product_id': product.productId,
      'title': product.title,
      'price': product.price,
      'currency': product.currency,
      'delivery_estimate_days': product.deliveryEstimateDays,
      'image_url': product.imageUrl,
      'product_url': product.productUrl,
      'variants': [],
      'quantity': quantity,
    }),
  );

  if (response.statusCode != 200) {
    throw Exception(
      'Konnte nicht in den Warenkorb gelegt werden (${response.statusCode}): ${response.body}',
    );
  }
}

/// Warenkorb abrufen: GET /sessions/{sessionId}/cart
Future<CartSummary> getCart({required String sessionId}) async {
  final url = Uri.parse('$baseUrl/sessions/$sessionId/cart');

  final response = await http.get(
    url,
    headers: {'Content-Type': 'application/json'},
  );

  if (response.statusCode == 200) {
    final data = jsonDecode(response.body) as Map<String, dynamic>;
    return CartSummary.fromJson(data);
  } else {
    throw Exception(
      'Warenkorb konnte nicht geladen werden (${response.statusCode}): ${response.body}',
    );
  }
}

/// Item aus dem Warenkorb entfernen: DELETE /sessions/{sessionId}/cart/items/{cartItemId}
Future<void> removeFromCart({
  required String sessionId,
  required int cartItemId,
}) async {
  final url = Uri.parse('$baseUrl/sessions/$sessionId/cart/items/$cartItemId');

  final response = await http.delete(
    url,
    headers: {'Content-Type': 'application/json'},
  );

  if (response.statusCode != 200) {
    throw Exception(
      'Konnte nicht entfernt werden (${response.statusCode}): ${response.body}',
    );
  }
}

/// Menge eines Cart-Items ändern: PATCH /sessions/{sessionId}/cart/items/{cartItemId}
Future<void> updateQuantity({
  required String sessionId,
  required int cartItemId,
  required int quantity,
}) async {
  final url = Uri.parse('$baseUrl/sessions/$sessionId/cart/items/$cartItemId');

  final response = await http.patch(
    url,
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode({'quantity': quantity}),
  );

  if (response.statusCode != 200) {
    throw Exception(
      'Menge konnte nicht geändert werden (${response.statusCode}): ${response.body}',
    );
  }
}
