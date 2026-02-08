import 'package:flutter/material.dart';
import 'package:hacknation_app/services/search_products.dart';

class MyResult extends StatelessWidget {
  const MyResult({
    super.key,
    required this.product,
    this.onAddToCart,
    this.isInCart = false,
  });

  final RankedProduct product;
  final VoidCallback? onAddToCart;
  final bool isInCart;

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
          // Produktbild
          ClipRRect(
            borderRadius: BorderRadius.circular(16),
            child: SizedBox(
              width: 90,
              height: 90,
              child: product.imageUrl != null && product.imageUrl!.isNotEmpty
                  ? Image.network(
                      product.imageUrl!,
                      fit: BoxFit.cover,
                      errorBuilder: (_, __, ___) => Container(
                        color: Colors.grey.shade200,
                        child: const Icon(
                          Icons.image_not_supported,
                          color: Colors.grey,
                        ),
                      ),
                    )
                  : Container(
                      color: Colors.grey.shade200,
                      child: const Icon(Icons.shopping_bag, color: Colors.grey),
                    ),
            ),
          ),
          const SizedBox(width: 12),
          // Produktinfos
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  product.title,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 4),
                Text(
                  '${product.price.toStringAsFixed(2)} ${product.currency}',
                  style: TextStyle(fontSize: 15, color: Colors.grey.shade700),
                ),
                const SizedBox(height: 4),
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 6,
                        vertical: 2,
                      ),
                      decoration: BoxDecoration(
                        color: Colors.pink.shade50,
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        product.retailerId,
                        style: TextStyle(
                          fontSize: 11,
                          color: Colors.pink.shade700,
                        ),
                      ),
                    ),
                    const SizedBox(width: 6),
                    if (product.deliveryEstimateDays != null)
                      Text(
                        '📦 ${product.deliveryEstimateDays} Tage',
                        style: TextStyle(
                          fontSize: 11,
                          color: Colors.grey.shade500,
                        ),
                      ),
                  ],
                ),
              ],
            ),
          ),
          // Score + Cart-Button
          Column(
            children: [
              Text(
                '${(product.score * 100).toInt()}%',
                style: const TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                  color: Colors.green,
                ),
              ),
              const Text(
                'Match',
                style: TextStyle(fontSize: 10, color: Colors.grey),
              ),
              const SizedBox(height: 8),
              GestureDetector(
                onTap: isInCart ? null : onAddToCart,
                child: Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 10,
                    vertical: 6,
                  ),
                  decoration: BoxDecoration(
                    color: isInCart ? Colors.grey.shade300 : Colors.black,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Icon(
                    isInCart ? Icons.check : Icons.add,
                    color: isInCart ? Colors.grey.shade600 : Colors.white,
                    size: 18,
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
