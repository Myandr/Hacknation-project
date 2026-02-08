import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:hacknation_app/services/cart_service.dart';

/// Öffnet die Warenkorb-Seite als Modal-Bottom-Sheet.
void showCartSheet(
  BuildContext context, {
  required String sessionId,
  VoidCallback? onCartChanged,
}) {
  showModalBottomSheet(
    context: context,
    isScrollControlled: true,
    backgroundColor: Colors.transparent,
    builder: (_) =>
        CartPage(sessionId: sessionId, onCartChanged: onCartChanged),
  );
}

class CartPage extends StatefulWidget {
  const CartPage({super.key, required this.sessionId, this.onCartChanged});

  final String sessionId;
  final VoidCallback? onCartChanged;

  @override
  State<CartPage> createState() => _CartPageState();
}

class _CartPageState extends State<CartPage> {
  CartSummary? _cart;
  bool _isLoading = true;
  String? _error;
  final Set<int> _removingIds = {};
  bool _isCheckoutProcessing = false;
  bool _checkoutSuccess = false;

  @override
  void initState() {
    super.initState();
    _loadCart();
  }

  Future<void> _loadCart() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final cart = await getCart(sessionId: widget.sessionId);
      setState(() {
        _cart = cart;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _removeItem(CartItem item) async {
    setState(() => _removingIds.add(item.id));

    try {
      await removeFromCart(sessionId: widget.sessionId, cartItemId: item.id);
      widget.onCartChanged?.call();
      await _loadCart();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Fehler: $e'), backgroundColor: Colors.red),
        );
      }
    } finally {
      setState(() => _removingIds.remove(item.id));
    }
  }

  Future<void> _updateQuantity(CartItem item, int newQuantity) async {
    if (newQuantity < 1) {
      _removeItem(item);
      return;
    }

    try {
      await updateQuantity(
        sessionId: widget.sessionId,
        cartItemId: item.id,
        quantity: newQuantity,
      );
      widget.onCartChanged?.call();
      await _loadCart();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Fehler: $e'), backgroundColor: Colors.red),
        );
      }
    }
  }

  Future<void> _simulateCheckout() async {
    if (_isCheckoutProcessing || _checkoutSuccess) return;

    setState(() {
      _isCheckoutProcessing = true;
      _checkoutSuccess = false;
    });

    try {
      await Future.delayed(const Duration(milliseconds: 900));
      if (!mounted) return;
      setState(() {
        _isCheckoutProcessing = false;
        _checkoutSuccess = true;
      });
      widget.onCartChanged?.call();

      await Future.delayed(const Duration(milliseconds: 900));
      if (!mounted) return;
      Navigator.pop(context);
    } catch (_) {
      if (mounted) {
        setState(() {
          _isCheckoutProcessing = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      height: MediaQuery.of(context).size.height * 0.80,
      decoration: const BoxDecoration(
        color: Color(0xFFF7F7F8),
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      child: Column(
        children: [
          // ── Header ──
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
            child: Row(
              children: [
                GestureDetector(
                  onTap: () => Navigator.pop(context),
                  child: const Icon(CupertinoIcons.xmark, size: 22),
                ),
                const Expanded(
                  child: Text(
                    'Warenkorb',
                    textAlign: TextAlign.center,
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                ),
                const SizedBox(width: 22),
              ],
            ),
          ),
          const Divider(height: 1),

          // ── Body ──
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : _error != null
                ? Center(
                    child: Padding(
                      padding: const EdgeInsets.all(24),
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          const Icon(
                            Icons.error_outline,
                            color: Colors.red,
                            size: 48,
                          ),
                          const SizedBox(height: 12),
                          Text(
                            'Fehler beim Laden:\n$_error',
                            textAlign: TextAlign.center,
                            style: const TextStyle(color: Colors.red),
                          ),
                          const SizedBox(height: 16),
                          ElevatedButton(
                            onPressed: _loadCart,
                            child: const Text('Erneut versuchen'),
                          ),
                        ],
                      ),
                    ),
                  )
                : _cart == null || _cart!.items.isEmpty
                ? const Center(
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(CupertinoIcons.cart, size: 64, color: Colors.grey),
                        SizedBox(height: 12),
                        Text(
                          'Dein Warenkorb ist leer',
                          style: TextStyle(fontSize: 16, color: Colors.grey),
                        ),
                      ],
                    ),
                  )
                : RefreshIndicator(
                    onRefresh: _loadCart,
                    child: ListView.separated(
                      padding: const EdgeInsets.all(16),
                      itemCount: _cart!.items.length,
                      separatorBuilder: (_, __) => const SizedBox(height: 12),
                      itemBuilder: (context, index) {
                        final item = _cart!.items[index];
                        final isRemoving = _removingIds.contains(item.id);
                        return _CartItemTile(
                          item: item,
                          isRemoving: isRemoving,
                          onRemove: () => _removeItem(item),
                          onQuantityChanged: (newQty) =>
                              _updateQuantity(item, newQty),
                        );
                      },
                    ),
                  ),
          ),

          // ── Footer: Summe ──
          if (_cart != null && _cart!.items.isNotEmpty)
            Container(
              padding: const EdgeInsets.fromLTRB(20, 12, 20, 32),
              decoration: BoxDecoration(
                color: Colors.white,
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.06),
                    blurRadius: 10,
                    offset: const Offset(0, -4),
                  ),
                ],
              ),
              child: Column(
                children: [
                  // Lieferinfo
                  if (_cart!.deliverySummary.isNotEmpty)
                    Padding(
                      padding: const EdgeInsets.only(bottom: 8),
                      child: Text(
                        _cart!.deliverySummary,
                        style: TextStyle(
                          fontSize: 13,
                          color: Colors.grey.shade600,
                        ),
                        textAlign: TextAlign.center,
                      ),
                    ),
                  // Gesamt
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text(
                        'Gesamt',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Text(
                        '${_cart!.totalPrice.toStringAsFixed(2)} ${_cart!.currency}',
                        style: const TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  // Checkout-Button
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      onPressed: (_isCheckoutProcessing || _checkoutSuccess)
                          ? null
                          : () => _simulateCheckout(),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: _checkoutSuccess
                            ? Colors.green
                            : Colors.black,
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 14),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(14),
                        ),
                      ),
                      child: _isCheckoutProcessing
                          ? Row(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: const [
                                SizedBox(
                                  width: 16,
                                  height: 16,
                                  child: CircularProgressIndicator(
                                    strokeWidth: 2,
                                    color: Colors.white,
                                  ),
                                ),
                                SizedBox(width: 10),
                                Text('Wird geladen...'),
                              ],
                            )
                          : _checkoutSuccess
                          ? Row(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: const [
                                Icon(Icons.check_circle, size: 18),
                                SizedBox(width: 8),
                                Text('Erfolgreich gekauft'),
                              ],
                            )
                          : const Text(
                              'Zur Kasse',
                              style: TextStyle(fontSize: 16),
                            ),
                    ),
                  ),
                ],
              ),
            ),
        ],
      ),
    );
  }
}

/// Ein einzelnes Warenkorb-Item.
class _CartItemTile extends StatelessWidget {
  const _CartItemTile({
    required this.item,
    required this.isRemoving,
    required this.onRemove,
    required this.onQuantityChanged,
  });

  final CartItem item;
  final bool isRemoving;
  final VoidCallback onRemove;
  final ValueChanged<int> onQuantityChanged;

  @override
  Widget build(BuildContext context) {
    return Opacity(
      opacity: isRemoving ? 0.5 : 1.0,
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 8,
              spreadRadius: 1,
            ),
          ],
        ),
        child: Row(
          children: [
            // Bild
            ClipRRect(
              borderRadius: BorderRadius.circular(12),
              child: SizedBox(
                width: 70,
                height: 70,
                child: item.imageUrl != null && item.imageUrl!.isNotEmpty
                    ? Image.network(
                        item.imageUrl!,
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
                        child: const Icon(
                          Icons.shopping_bag,
                          color: Colors.grey,
                        ),
                      ),
              ),
            ),
            const SizedBox(width: 12),
            // Info
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    item.title,
                    style: const TextStyle(
                      fontSize: 15,
                      fontWeight: FontWeight.w600,
                    ),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 4),
                  Text(
                    '${item.price.toStringAsFixed(2)} ${item.currency}',
                    style: TextStyle(fontSize: 14, color: Colors.grey.shade700),
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
                          item.retailerId,
                          style: TextStyle(
                            fontSize: 11,
                            color: Colors.pink.shade700,
                          ),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Text(
                        'Menge: ${item.quantity}',
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.grey.shade500,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  // Quantity Stepper
                  Row(
                    children: [
                      _QuantityButton(
                        icon: Icons.remove,
                        onTap: isRemoving
                            ? null
                            : () => onQuantityChanged(item.quantity - 1),
                      ),
                      Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 12),
                        child: Text(
                          '${item.quantity}',
                          style: const TextStyle(
                            fontSize: 15,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                      _QuantityButton(
                        icon: Icons.add,
                        onTap: isRemoving
                            ? null
                            : () => onQuantityChanged(item.quantity + 1),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            // Entfernen-Button
            IconButton(
              onPressed: isRemoving ? null : onRemove,
              icon: isRemoving
                  ? const SizedBox(
                      width: 18,
                      height: 18,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : Icon(
                      CupertinoIcons.trash,
                      color: Colors.red.shade400,
                      size: 20,
                    ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Kleiner runder +/- Button für den Quantity-Stepper.
class _QuantityButton extends StatelessWidget {
  const _QuantityButton({required this.icon, this.onTap});

  final IconData icon;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: 28,
        height: 28,
        decoration: BoxDecoration(
          color: onTap != null ? Colors.grey.shade200 : Colors.grey.shade100,
          borderRadius: BorderRadius.circular(8),
        ),
        child: Icon(
          icon,
          size: 16,
          color: onTap != null ? Colors.black : Colors.grey,
        ),
      ),
    );
  }
}
