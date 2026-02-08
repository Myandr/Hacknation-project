import 'package:flutter/material.dart';
import 'package:hacknation_app/components/MyResult.dart';
import 'package:hacknation_app/services/search_products.dart';

class MyResults extends StatelessWidget {
  const MyResults({
    super.key,
    required this.products,
    this.onAddToCart,
    this.cartProductIds = const {},
  });

  final List<RankedProduct> products;
  final void Function(RankedProduct product)? onAddToCart;
  final Set<String> cartProductIds;

  @override
  Widget build(BuildContext context) {
    if (products.isEmpty) {
      return const Center(
        child: Padding(
          padding: EdgeInsets.all(24),
          child: Text(
            'Keine Produkte gefunden.',
            style: TextStyle(color: Colors.grey, fontSize: 16),
          ),
        ),
      );
    }

    return ListView.separated(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      itemCount: products.length,
      separatorBuilder: (_, __) => const SizedBox(height: 10),
      itemBuilder: (context, index) {
        final product = products[index];
        return MyResult(
          product: product,
          isInCart: cartProductIds.contains(product.productId),
          onAddToCart: onAddToCart != null ? () => onAddToCart!(product) : null,
        );
      },
    );
  }
}
