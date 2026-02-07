/// Produkt von der API (ASOS), flexibel für verschiedene Response-Strukturen.
class ProductItem {
  final String? id;
  final String? name;
  final String? imageUrl;
  final String? price;
  final String? url;

  ProductItem({
    this.id,
    this.name,
    this.imageUrl,
    this.price,
    this.url,
  });

  factory ProductItem.fromJson(Map<String, dynamic> json) {
    final priceObj = json['price'];
    Object? priceVal = priceObj;
    if (priceObj is Map) {
      priceVal = priceObj['current']?['value'] ?? priceObj['value'] ?? priceObj;
    }
    String? imageUrl = json['imageUrl'] as String?;
    if (imageUrl == null && json['media'] != null) {
      final media = json['media'] as Map<String, dynamic>?;
      final images = media?['images'] as List?;
      if (images != null && images.isNotEmpty) {
        final first = images[0];
        if (first is Map && first['url'] != null) {
          imageUrl = first['url'] as String?;
        }
      }
    }
    return ProductItem(
      id: json['id']?.toString(),
      name: json['name'] as String? ?? json['productName'] as String? ?? json['title'] as String?,
      imageUrl: imageUrl,
      price: priceVal?.toString(),
      url: json['url'] as String?,
    );
  }
}
