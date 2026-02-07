import 'package:flutter/material.dart';

class MyResult extends StatelessWidget {
  MyResult({
    super.key,
    required this.name,
    required this.price,
    this.imageUrl,
  });

  final String name;
  final String price;
  final String? imageUrl;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.06),
            blurRadius: 10,
            spreadRadius: 2,
          ),
        ],
      ),
      child: Row(
        children: [
          Expanded(
            child: ClipRRect(
              borderRadius: BorderRadius.circular(16),
              child: imageUrl != null && imageUrl!.isNotEmpty
                  ? Image.network(
                      imageUrl!,
                      height: 80,
                      fit: BoxFit.cover,
                      errorBuilder: (_, __, ___) => _placeholder(),
                    )
                  : _placeholder(),
            ),
          ),
          Expanded(
            child: Padding(
              padding: const EdgeInsets.only(left: 12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    name,
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  Text(
                    price,
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.grey.shade600,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _placeholder() {
    return Container(
      height: 80,
      decoration: BoxDecoration(
        color: Colors.grey.shade300,
        borderRadius: BorderRadius.circular(16),
      ),
      child: Icon(
        Icons.image_not_supported,
        color: Colors.grey.shade500,
        size: 32,
      ),
    );
  }
}

/// Name, Preis und Bild-URL aus API-Produkt-Map lesen.
(String name, String price, String? imageUrl) productDisplayFromMap(Map<String, dynamic> p) {
  String name = p['name'] as String? ?? p['productName'] as String? ?? p['title'] as String? ?? 'Produkt';
  Object? priceVal = p['price'];
  if (priceVal is Map) {
    priceVal = priceVal['current']?['value'] ?? priceVal['value'];
  }
  String price = priceVal != null ? '$priceVal €' : '—';
  String? imageUrl = p['imageUrl'] as String?;
  if (imageUrl == null && p['media'] is Map) {
    final images = (p['media'] as Map)['images'] as List?;
    if (images != null && images.isNotEmpty && images[0] is Map) {
      imageUrl = (images[0] as Map)['url'] as String?;
    }
  }
  return (name, price, imageUrl);
}