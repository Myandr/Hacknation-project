import 'package:flutter/material.dart';
import 'package:hacknation_app/components/MyResult.dart';
import 'package:hacknation_app/models/product_item.dart';

class MyResults extends StatelessWidget {
  const MyResults({
    super.key,
    required this.messages,
    required this.products,
    this.isLoading = false,
  });

  final List<ChatMessage> messages;
  final List<ProductItem> products;
  final bool isLoading;

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          ...messages.map((m) => _ChatBubble(role: m.role, content: m.content)),
          if (isLoading)
            const Padding(
              padding: EdgeInsets.symmetric(vertical: 12),
              child: Center(child: CircularProgressIndicator(strokeWidth: 2)),
            ),
          if (products.isNotEmpty) ...[
            const SizedBox(height: 16),
            Padding(
              padding: const EdgeInsets.only(left: 4, bottom: 8),
              child: Text(
                'Deine Produkte',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Colors.grey.shade800,
                ),
              ),
            ),
            ...products.map(
              (p) => Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: MyResult(
                  name: p.name ?? 'Produkt',
                  price: p.price != null ? '${p.price} €' : '—',
                  imageUrl: p.imageUrl,
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }
}

class ChatMessage {
  final String role; // 'user' | 'assistant'
  final String content;

  ChatMessage({required this.role, required this.content});
}

class _ChatBubble extends StatelessWidget {
  final String role;
  final String content;

  const _ChatBubble({required this.role, required this.content});

  @override
  Widget build(BuildContext context) {
    final isUser = role == 'user';
    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.only(bottom: 10),
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.8),
        decoration: BoxDecoration(
          color: isUser ? Colors.black87 : Colors.grey.shade200,
          borderRadius: BorderRadius.circular(16),
        ),
        child: Text(
          content,
          style: TextStyle(
            fontSize: 15,
            color: isUser ? Colors.white : Colors.black87,
          ),
        ),
      ),
    );
  }
}
